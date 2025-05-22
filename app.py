from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import time
import x
import json
import os
import uuid
import requests
import languages

app = Flask(__name__)

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


##############################
@app.context_processor
def inject_language():
    lan = session.get("lan", "en")
    return dict(lan=lan)


##############################
@app.route("/set-language/<lan>")
def set_language(lan):
    languages_allowed = ["en", "dk"]
    if lan not in languages_allowed:
        lan = "en"
    session["lan"] = lan

    ref = request.referrer
    if ref:
        parsed_url = urlparse(ref)
        path = parsed_url.path  # fx /login/en eller /en or /en/page

        parts = path.strip("/").split("/")

        # Prøv at finde sproget i path
        idx = None
        for i, part in enumerate(parts):
            if part in languages_allowed:
                idx = i
                break

        if idx is not None:
            # Erstat sproget på den position
            parts[idx] = lan
            new_path = "/" + "/".join(parts)
        else:
            # Hvis intet sprog i URL, tilføj sprog som første segment
            new_path = f"/{lan}" + (path if path != "/" else "")

        return redirect(new_path)

    return redirect(url_for("show_index", lan=lan))


##############################
@app.get("/rates")
def get_rates():
    try:
        data = requests.get("https://api.exchangerate-api.com/v4/latest/usd")
        ic(data.json())
        with open("rates.txt", "w") as file:
            file.write(data.text)
        return data.json()
    except Exception as ex:
        ic(ex)


##############################
@app.after_request
def disable_cache(response):
    """
    This function automatically disables caching for all responses.
    It is applied after every request to the server.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


#############################
@app.get("/send-email")
def send_email():
    try:
        x.send_email()
        return "email"
    except Exception as ex:
        ic(ex)
        return "error"

###############################
@app.get("/send_reset_email")
def send_reset_email():
    try:
        x.send_reset_email()
        return "email"
    except Exception as ex:
        ic(ex)
        return "error"


##############################
@app.get("/")
def show_index_default():
    return redirect(url_for("show_index", lan="en"))
@app.get("/<lan>")
def show_index(lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: 
            lan = "en"
            session["lan"] = lan
        texts = languages.languages[lan]
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_blocked_at = 0 AND item_deleted_at = 0 ORDER BY item_created_at DESC LIMIT 2"
        cursor.execute(q)
        items = cursor.fetchall()
        rates = ""
        with open("rates.txt", "r") as file:
            rates = file.read()
        ic(rates)
        rates = json.loads(rates)
        is_session = False
        if session.get("user"): is_session = True
        return render_template("index.html", languages=texts,   title=texts["page_title_index"], items=items, is_session = is_session, rates=rates)
    except Exception as ex:
        ic(ex)
        return "ups"
    finally:
        pass


##############################
@app.get("/profile")
def show_profile_default():
    return redirect(url_for("show_profile", lan="en"))

@app.get("/<lan>/profile")
def show_profile(lan):
    try:
        # Allowed languages and fallback
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"
            session["lan"] = lan
        texts = languages.languages[lan]
        old_values = session.pop("old_values", {})

        # Pop toast message from session (single message + type)
        message = session.pop("message", "")
        message_type = session.pop("message_type", "")

        # DB connection
        db, cursor = x.db()

        # Fetch all items (you may want to filter by user, if needed)
        q_items = """
                    SELECT * FROM items
                    WHERE item_blocked_at = 0
                    AND item_deleted_at = 0
                    ORDER BY item_created_at DESC
                    """
        cursor.execute(q_items)
        items = cursor.fetchall()

        # Read rates from file (json)
        with open("rates.txt", "r") as file:
            rates = json.load(file)

        # Fetch images for all items
        item_pks = [item['item_pk'] for item in items]
        if item_pks:
            format_strings = ','.join(['%s'] * len(item_pks))
            q_images = f"SELECT item_pk, image_name FROM images WHERE item_pk IN ({format_strings})"
            cursor.execute(q_images, tuple(item_pks))
            images = cursor.fetchall()
        else:
            images = []

        # Group images by item_pk
        images_by_item = {}
        for img in images:
            images_by_item.setdefault(img['item_pk'], []).append(img['image_name'])

        # Session active?
        is_session = "user" in session

        # Render template with unified message
        return render_template(
            "profile.html",
            title=texts["page_title_profile"],
            user=session.get("user"),
            x=x,
            is_session=is_session,
            message=message,
            message_type=message_type,
            old_values=old_values,
            items=items,
            images_by_item=images_by_item,
            lan=lan,
            languages=texts,
            rates=rates,
        )

    except Exception as ex:
        ic(ex)
        return redirect(url_for("show_login"))
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()




##############################
@app.get("/signup")
def show_signup_default():
    return redirect(url_for("show_signup", lan="en"))

@app.get("/<lan>/signup")
def show_signup(lan):
    try:
        # Retrieve messages from session, if any
        message = session.pop("message", "")
        message_type = session.pop("message_type", "")
        old_values = session.pop("old_values", {})

        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"
            session["lan"] = lan

        texts = languages.languages[lan]

        return render_template(
            "signup.html",
            x=x,
            active_signup="active",
            message=message,
            message_type=message_type,
            old_values={},
            languages=texts,
            title=texts["page_title_signup"]
        )
    except Exception as ex:
        ic(ex)
    finally:
        pass

##############################
@app.post("/<lan>/signup")
def signup(lan):
    languages_allowed = ["en", "dk"]
    if lan not in languages_allowed:
        lan = "en"
    texts = languages.languages[lan]

    try:
        user_pk = str(uuid.uuid4())
        user_name = x.validate_user_name(texts)
        user_username = x.validate_user_username(texts)
        user_last_name = x.validate_user_last_name(texts)
        user_email = x.validate_user_email(texts)
        user_password = x.validate_user_password(texts)
        hashed_password = generate_password_hash(user_password)
        verification_key = str(uuid.uuid4())
        user_created_at = int(time.time())
        user_updated_at = int(time.time())

        q = """INSERT INTO users
        (user_pk, user_name, user_last_name, user_email, user_username, user_password,
         user_created_at, user_updated_at, user_deleted_at, user_blocked_at, user_verified_at,
         user_verification_key, user_role)
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, %s, 'user')"""

        db, cursor = x.db()
        cursor.execute(q, (
            user_pk,
            user_name,
            user_last_name,
            user_email,
            user_username,
            hashed_password,
            user_created_at,
            user_updated_at,
            verification_key
        ))

        if cursor.rowcount != 1:
            raise Exception(texts["system_error"])

        db.commit()

        x.send_email(user_name, user_last_name, user_email, verification_key, lan)

        # Use session to store success message for redirect
        session["message"] = texts["signup_success"]
        session["message_type"] = "success"

        return redirect(url_for("show_login", lan=lan))

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()

        old_values = request.form.to_dict()

        # Handle validation and database errors inline, render template with error message and old values
        error_str = str(ex).lower()

        # Map possible errors to keys and error message fields
        if "username" in error_str:
            old_values.pop("user_username", None)
            return render_template("signup.html",
                                   message=texts.get("invalid_username", "Invalid username"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_username_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "first_name" in error_str:
            old_values.pop("user_name", None)
            return render_template("signup.html",
                                   message=texts.get("invalid_first_name", "Invalid first name"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_name_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "last_name" in error_str:
            old_values.pop("user_last_name", None)
            return render_template("signup.html",
                                   message=texts.get("invalid_last_name", "Invalid last name"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_last_name_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "invalid_email" in error_str:
            old_values.pop("user_email", None)
            return render_template("signup.html",
                                   message=texts.get("invalid_email", "Invalid email"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_email_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "password" in error_str:
            old_values.pop("user_password", None)
            return render_template("signup.html",
                                   message=texts.get("invalid_password", "Invalid password"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_password_error="input_error",
                                   lan=lan,
                                   languages=texts)

        # Handle unique constraint errors via redirect + session messages (email and username exists)
        if "users.user_email" in error_str:
            session["message"] = texts.get("email_exists", "Email already exists")
            session["message_type"] = "error"
            return redirect(url_for("show_signup", lan=lan))

        if "users.user_username" in error_str:
            session["message"] = texts.get("username_exists", "Username already exists")
            session["message_type"] = "error"
            return redirect(url_for("show_signup", lan=lan))

        # Fallback: redirect with error message in session
        session["message"] = ex.args[0] if ex.args else "Unknown error"
        session["message_type"] = "error"
        return redirect(url_for("show_signup", lan=lan))

    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



#############################
@app.get("/verify/<verification_key>")
def verify_default():
    return redirect(url_for("verify", lan="en"))
@app.get("/<lan>/verify/<verification_key>")
def verify(verification_key, lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: 
            lan = "en"
            session["lan"] = lan
        
        texts = languages.languages[lan]

        db, cursor = x.db()
 
        q = "SELECT user_pk FROM users WHERE user_verification_key = %s AND user_verified_at = 0"

        cursor.execute(q, (verification_key,))
        user = cursor.fetchone()
 
        if not user:
            return texts["invalid_key"]
        current_time = int(time.time())
        q_update = """UPDATE users
                      SET user_verified_at = %s,
                        user_verification_key = NULL
                      WHERE user_pk = %s"""
        cursor.execute(q_update, (current_time, user["user_pk"]))
        db.commit()
        return texts["account_verified"]
    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()
        return texts.get("verification_failed", "Verification failed"), 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



##############################
@app.get("/login")
def show_login_default():
    return redirect(url_for("show_login", lan="en"))

@app.get("/<lan>/login")
def show_login(lan):
    try:
        message = session.pop("message", "")
        message_type = session.pop("message_type", "")

        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: 
            lan = "en"
            session["lan"] = lan
        texts = languages.languages[lan]
        return render_template(
            "login.html", 
            x=x,
            message=message,
            message_type=message_type,
            old_values={},
            languages=texts,
            title=texts["page_title_login"]
        )
    except Exception as ex:
        ic(ex)
    finally:
        pass


##############################
@app.post("/<lan>/login")
def login(lan):
    languages_allowed = ["en", "dk"]
    if lan not in languages_allowed:
        lan = "en"
    texts = languages.languages[lan]

    try:
        user_email = x.validate_user_email(texts)
        user_password = x.validate_user_password(texts)
        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_email = %s"
        cursor.execute(q, (user_email,))
        user = cursor.fetchone()
        ic(user)

        if not user:
            raise Exception(texts["user_not_found"])
        if user["user_verified_at"] == 0:
            raise Exception(texts["user_not_verified"])
        if user["user_deleted_at"] != 0:
            raise Exception(texts["user_blocked"])
        if user["user_blocked_at"] != 0:
            raise Exception(texts["user_blocked"])
        if not check_password_hash(user["user_password"], user_password):
            raise Exception(texts["invalid_password"])

        user.pop("user_password")
        session["user"] = user
        session["user_pk"] = user["user_pk"]
        session["message"] = texts["login_success"]
        session["message_type"] = "success"

        if user["user_role"] == "admin":
            return redirect(url_for("show_admin", lan=lan))
        else:
            return redirect(url_for("show_profile", lan=lan))

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()

        old_values = request.form.to_dict()

        known_errors = [
            texts["invalid_email"],
            texts["invalid_password"],
            texts["user_not_found"],
            texts["user_not_verified"],
            texts["user_deleted"]
        ]

        if str(ex) in known_errors:
            if str(ex) == texts["invalid_password"]:
                old_values.pop("user_password", None)
            if str(ex) == texts["invalid_email"]:
                old_values.pop("user_email", None)

            return render_template("login.html",
                message=str(ex),
                message_type="error",
                old_values=old_values,
                lan=lan,
                languages=texts)
        
        session["message"] = str(ex)
        session["message_type"] = "error"
        return redirect(url_for("show_login", lan=lan))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/logout")
def logout_default():
    return redirect(url_for("logout", lan=session.get("lan", "en")))

@app.get("/<lan>/logout")
def logout(lan):
    session.pop("user", None)
    return redirect(url_for("show_login", lan=lan))


##############################
@app.get("/forgot-password")
def show_forgot_password_default():
    return redirect(url_for("show_forgot_password", lan="en"))

@app.get("/<lan>/forgot-password")
def show_forgot_password(lan):
    try:
        message = session.pop("message", "")
        message_type = session.pop("message_type", "")

        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"
        session["lan"] = lan
        texts = languages.languages[lan]

        return render_template("forgot_password.html", title=texts["page_title_forgot"], languages=texts, lan=lan, message=message, message_type=message_type)
    except Exception as ex:
        ic(ex)
        return "Error loading page", 500
    


##############################
@app.post("/<lan>/forgot-password")
def forgot_password(lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"
        session["lan"] = lan
        texts = languages.languages[lan]

        user_email = x.validate_user_email(texts)
        db, cursor = x.db()

        q = "SELECT * FROM users WHERE user_email = %s"
        cursor.execute(q, (user_email,))
        user = cursor.fetchone()

        if not user: raise Exception(texts["user_not_found"])
        if user["user_verified_at"] == 0: raise Exception(texts["user_not_verified"])
        if user["user_deleted_at"] != 0: raise Exception(texts["user_deleted"])

        verification_key = str(uuid.uuid4())
        q_update = """UPDATE users
                      SET user_verification_key = %s
                      WHERE user_pk = %s"""
        cursor.execute(q_update, (verification_key, user["user_pk"]))
        db.commit()

        x.send_reset_email(user["user_name"], user["user_email"], verification_key, lan)
        session["message"] = texts["reset_email_sent"]
        session["message_type"] = "success"
        return redirect(url_for("show_login", lan=lan))
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        session["message"] = ex.args[0]
        session["message_type"] = "error"
        return redirect(url_for("forgot_password", lan=lan))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.get("/items/<item_pk>")
def get_item_by_pk_default(item_pk):
    return redirect(url_for("get_item_by_pk", lan="en", item_pk=item_pk))

@app.get("/<lan>/items/<item_pk>")
def get_item_by_pk(item_pk, lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:lan = "en"
        session["lan"] = lan
        texts = languages.languages[lan]

        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_pk = %s AND item_blocked_at = 0 AND item_deleted_at = 0"
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        if not item:
            return texts.get("item_not_found", "Item not found."), 500

        with open("rates.txt", "r") as file:
            rates = json.load(file)

        html = render_template("_item.html", item=item, rates=rates, languages=texts, lan=lan)

        return f"""
            <mixhtml mix-replace="#item">
                {html}
            </mixhtml>
        """

    except Exception as ex:
        ic(ex)
        return texts.get("system_error", "An error occurred while fetching the item."), 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.get("/items/page/<page_number>")
def get_items_by_page(page_number):
    try:
        lan = session.get("lan", "en")
        texts = languages.languages.get(lan, languages.languages["en"])

        page_number = x.validate_page_number(page_number)
        items_per_page = 2
        offset = (page_number-1) * items_per_page
        extra_item = items_per_page + 1
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_blocked_at = 0 AND item_deleted_at = 0 ORDER BY item_created_at DESC LIMIT %s OFFSET %s"
        cursor.execute(q, (extra_item, offset))
        items = cursor.fetchall()
        html = ""
        
        rates= ""
        with open("rates.txt", "r") as file:
            rates = file.read() # this is text that looks like json
            rates = json.loads(rates)

        for item in items[:items_per_page]:
            i = render_template("_item_mini.html", item=item, rates=rates, languages=texts)
            html += i
        button = render_template("_button_more_items.html", page_number=page_number + 1, languages=texts)
        if len(items) < extra_item: button = ""
        return f"""
            <mixhtml mix-bottom="#items">
                {html}
            </mixhtml>
            <mixhtml mix-replace="#button_more_items">
                {button}
            </mixhtml>
            <mixhtml mix-function="add_markers_to_map">
                {json.dumps(items[:items_per_page])}
            </mixhtml>            
        """
    except Exception as ex:
        ic(ex)
        if "company_ex page number" in str(ex):
            message = texts.get("invalid_page_number", "Invalid page number.")
            return """
                <mixhtml mix-top="body">
                    {message}
                </mixhtml>
            """
        message = texts.get("system_error", "An error occurred while fetching items.")
        return """
            <mixhtml mix-top="body">
                {message}
            </mixhtml>
        """
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
@app.get("/search")
def search():
    try:
        lan = session.get("lan", "en")
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        search_for = x.validate_search_for(texts)
        db, cursor = x.db()

        q = "SELECT * FROM items WHERE item_blocked_at = 0 AND item_deleted_at = 0 AND item_name LIKE %s"
        cursor.execute(q, (f"{search_for}%",))
        items = cursor.fetchall()

        if not items:
            raise Exception(texts["no_results"])

        # Return JSON data as a list of dicts
        return {"results": items}

    except Exception as ex:
        ic(ex)
        message = ex.args[0] if lan in locals() and isinstance(ex.args[0], str) else texts.get("search_failed", "Search failed")
        return {"error": message}, 400

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



#################################
@app.post("/<lan>/add-item")
def add_item(lan):
    try:
        if lan not in ["en", "dk"]:
            lan = session.get("lan", "en")
            if lan not in ["en", "dk"]:
                lan = "en"
        session["lan"] = lan

        texts = languages.languages[lan]

        user = session.get("user")
        if not user or "user_pk" not in user:
            raise Exception("User is not logged in")
        user_pk = user["user_pk"]

        item_pk = str(uuid.uuid4())
        item_name = x.validate_item_name()
        item_address = x.validate_item_address()
        item_lat = x.validate_item_lat()
        item_lon = x.validate_item_lon()
        item_created_at = int(time.time())
        item_price = x.validate_item_price()

        # Billedhåndtering
        item_icon = "shelter.svg"
        image_filenames = x.validate_item_images()  # <- Now uses your validator

        image_values = ""
        timestamp = int(time.time())
        first_image_filename = image_filenames[0]  # First validated/saved image

        for filename in image_filenames:
            image_pk = uuid.uuid4().hex
            image_values += f"('{image_pk}', '{item_pk}', '{filename}', {timestamp}),"


        db, cursor = x.db()

        # Indsæt item med hovedbillede
        q_item = """INSERT INTO items
                    (item_pk, 
                    item_name, 
                    item_image, 
                    item_address,
                    item_icon,
                    item_price,  
                    item_lon, 
                    item_lat, 
                    item_created_at, 
                    item_blocked_at, 
                    item_updated_at,
                    item_deleted_at,
                    user_fk 
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(q_item, (
            item_pk, 
            item_name,
            first_image_filename, 
            item_address,
            item_icon,
            item_price,
            item_lon, 
            item_lat, 
            item_created_at,
            0,
            None,
            0,
            user_pk
        ))
        if cursor.rowcount != 1:
            raise Exception(texts["could_not_insert_item"])

        # Indsæt billeder
        if image_values:
            image_values = image_values.rstrip(",")
            q_images = f"INSERT INTO images (image_pk, item_pk, image_name, created_at) VALUES {image_values}"
            cursor.execute(q_images)

        db.commit()
        return redirect(url_for("show_index", lan=lan))

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()

        old_values = request.form.to_dict()
        ex_str = str(ex).lower()

        if "invalid_shelter_name" in ex_str:
            old_values.pop("item_name", None)
            message = texts.get("invalid_shelter_name", "Invalid shelter name")
        elif "address" in ex_str:
            old_values.pop("item_address", None)
            message = texts.get("invalid_address", "Invalid address")
        elif "latitude" in ex_str:
            old_values.pop("item_lat", None)
            message = texts.get("invalid_latitude", "Invalid latitude")
        elif "longitude" in ex_str:
            old_values.pop("item_lon", None)
            message = texts.get("invalid_longitude", "Invalid longitude")
        elif "price" in ex_str:
            old_values.pop("item_price", None)
            message = texts.get("invalid_price", "Invalid price")
        elif "no_images_uploaded" in ex_str:
            message = texts.get("no_images_uploaded", "No images uploaded")
        elif "not_enough_images_uploaded" in ex_str:
            message = texts.get("not_enough_images_uploaded", "Please upload at least 3 images")
        elif "max_upload_exceeded" in ex_str:
            message = texts.get("max_upload_exceeded", "You can upload a maximum of 5 images.")
        elif "file_extension_not_allowed" in ex_str:
            message = texts.get("file_extension_not_allowed", "Only certain image types are allowed.")
        elif "file_too_large" in ex_str:
            message = texts.get("file_too_large", "Image too large.")
        else:
            message = texts.get("unknown_error", "An unexpected error occurred")

        session["old_values"] = old_values
        session["message"] = message
        session["message_type"] = "error"

        return redirect(url_for("show_profile", lan=lan))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()





###############################
@app.get("/admin")
def show_admin_default():
    return redirect(url_for("show_admin", lan="en"))

@app.get("/<lan>/admin")
def show_admin(lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: 
            lan = "en"
            session["lan"] = lan
        texts = languages.languages[lan]
        old_values = session.pop("old_values", {})

        message = session.pop("message", "")
        message_type = session.pop("message_type", "")

        db, cursor = x.db()
        q_users = "SELECT * FROM users"
        cursor.execute(q_users)
        users = cursor.fetchall()

        # Get items (like on index)
        q_items = "SELECT * FROM items WHERE item_deleted_at = 0 ORDER BY item_created_at"
        cursor.execute(q_items)
        items = cursor.fetchall()

        # Load rates from file
        rates = ""
        with open("rates.txt", "r") as file:
            rates = file.read()
        rates = json.loads(rates)  # Convert to dict

        # Session check
        is_session = 'user' in session

        return render_template("admin.html",
                               users=users,
                               items=items,
                               rates=rates,
                               is_session=is_session,
                               languages=texts,
                               message=message,
                                message_type=message_type,
                                old_values=old_values,
                        title=texts["page_title_admin"]
                        )
    except Exception as ex:
        ic(ex)
        return redirect(url_for("show_login"))
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()

##############################
@app.patch("/block-user/<user_pk>")
def block_user(user_pk):
    try:
        lan = session.get("lan", "en")
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        db, cursor = x.db()
        q = "UPDATE users SET user_blocked_at = %s WHERE user_pk = %s"
        blocked_at = int(time.time())
        cursor.execute(q, (blocked_at, user_pk))
        db.commit()

        if cursor.rowcount == 0:
            message = texts.get("block_failed", "User could not be blocked.")
            return f"""
            <mixhtml mix-replace="#toast-container">
                <div class="toast-container">
                    <div class="toast toast-error">{message}</div>
                </div>
            </mixhtml>
            """

        user = {"user_pk": user_pk}
        button_unblock = render_template("_button_unblock_user.html", user=user, languages=texts, lan=lan)
        return f"""
        <mixhtml mix-replace="#block-{user_pk}">
            {button_unblock}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        message = texts.get("block_exception", "An error occurred while trying to block the user.")
        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-error">{message}</div>
            </div>
        </mixhtml>
        """



##############################
@app.patch("/unblock-user/<user_pk>")
def unblock_user(user_pk):
    try:
        lan = session.get("lan", "en")
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        db, cursor = x.db()
        q = "UPDATE users SET user_blocked_at = %s WHERE user_pk = %s"
        cursor.execute(q, (0, user_pk))
        db.commit()

        if cursor.rowcount == 0:
            message = texts.get("unblock_failed", "User could not be unblocked.")
            return f"""
            <mixhtml mix-replace="#toast-container">
                <div class="toast-container">
                    <div class="toast toast-error">{message}</div>
                </div>
            </mixhtml>
            """

        user = {"user_pk": user_pk}
        button_block = render_template("_button_block_user.html", user=user, languages=texts, lan=lan)
        return f"""
        <mixhtml mix-replace="#unblock-{user_pk}">
            {button_block}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        message = texts.get("unblock_exception", "An error occurred while trying to unblock the user.")
        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-error">{message}</div>
            </div>
        </mixhtml>
        """


##############################
@app.patch("/block-item/<item_pk>")
def block_item(item_pk):
    try:
        lan = session.get("lan", "en")
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        db, cursor = x.db()
        blocked_at = int(time.time())
        q = "UPDATE items SET item_blocked_at = %s WHERE item_pk = %s"
        cursor.execute(q, (blocked_at, item_pk))
        db.commit()

        if cursor.rowcount == 0:
            message = texts.get("block_item_failed", "Item could not be blocked.")
            return f"""
            <mixhtml mix-replace="#toast-container">
                <div class="toast-container">
                    <div class="toast toast-error">{message}</div>
                </div>
            </mixhtml>
            """

        item = {"item_pk": item_pk}
        button_unblock = render_template("_button_unblock_item.html", item=item, languages=texts, lan=lan)
        return f"""
        <mixhtml mix-replace="#block-{item_pk}">
            {button_unblock}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        message = texts.get("block_item_exception", "An error occurred while trying to block the item.")
        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-error">{message}</div>
            </div>
        </mixhtml>
        """


##############################
@app.patch("/unblock-item/<item_pk>")
def unblock_item(item_pk):
    try:
        lan = session.get("lan", "en")
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        db, cursor = x.db()
        q = "UPDATE items SET item_blocked_at = %s WHERE item_pk = %s"
        cursor.execute(q, (0, item_pk))
        db.commit()

        if cursor.rowcount == 0:
            message = texts.get("unblock_item_failed", "Item could not be unblocked.")
            return f"""
            <mixhtml mix-replace="#toast-container">
                <div class="toast-container">
                    <div class="toast toast-error">{message}</div>
                </div>
            </mixhtml>
            """

        item = {"item_pk": item_pk}
        button_block = render_template("_button_block_item.html", item=item, languages=texts, lan=lan)
        return f"""
        <mixhtml mix-replace="#unblock-{item_pk}">
            {button_block}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        message = texts.get("unblock_item_exception", "An error occurred while trying to unblock the item.")
        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-error">{message}</div>
            </div>
        </mixhtml>
        """


###############################
@app.post("/<lan>/update-item/<item_pk>")
def update_item_inline(item_pk, lan):
    try:
        lan = session.get("lan", "en")
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        item_name = x.validate_item_name()
        item_address = x.validate_item_address()
        item_lat = x.validate_item_lat()
        item_lon = x.validate_item_lon()
        item_price = x.validate_item_price()
        item_updated_at = int(time.time())

        db, cursor = x.db()
        q = """UPDATE items 
               SET item_name = %s, 
                   item_address = %s, 
                   item_lat = %s, 
                   item_lon = %s, 
                   item_price = %s, 
                   item_updated_at = %s 
               WHERE item_pk = %s"""
        cursor.execute(q, (
            item_name, item_address, item_lat, item_lon, item_price, item_updated_at, item_pk
        ))

        if cursor.rowcount != 1:
            raise Exception("update_failed")

        db.commit()
        session["message"] = texts.get("item_updated", "Item updated successfully")
        session["message_type"] = "success"
        return redirect(url_for("show_profile", lan=lan))

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()

        old_values = request.form.to_dict()
        ex_str = str(ex).lower()

        if "invalid_shelter_name" in ex_str:
            old_values.pop("item_name", None)
            message = texts.get("invalid_shelter_name", "Invalid shelter name")
        elif "address" in ex_str:
            old_values.pop("item_address", None)
            message = texts.get("invalid_address", "Invalid address")
        elif "latitude" in ex_str:
            old_values.pop("item_lat", None)
            message = texts.get("invalid_latitude", "Invalid latitude")
        elif "longitude" in ex_str:
            old_values.pop("item_lon", None)
            message = texts.get("invalid_longitude", "Invalid longitude")
        elif "price" in ex_str:
            old_values.pop("item_price", None)
            message = texts.get("invalid_price", "Invalid price")
        elif "item_not_found" in ex_str:
            message = texts.get("item_not_found", "Update failed – item not found?")
        else:
            message = texts.get("unknown_error", "An unexpected error occurred")

        session["old_values"] = old_values
        session["message"] = message
        session["message_type"] = "error"

        return redirect(url_for("show_profile", lan=lan))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



###############################
@app.post("/<lan>/update-profile/<user_pk>")
def update_profile(user_pk, lan):
    languages_allowed = ["en", "dk"]
    if lan not in languages_allowed:
        lan = "en"
    texts = languages.languages[lan]

    try:
        user_name = x.validate_user_name(texts)
        user_last_name = x.validate_user_last_name(texts)
        user_username = x.validate_user_username(texts)
        user_email = x.validate_user_email(texts)
        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """UPDATE users 
               SET user_name=%s, user_last_name=%s, user_username=%s, 
                   user_email=%s, user_updated_at=%s
               WHERE user_pk=%s"""
        cursor.execute(q, (
            user_name, user_last_name, user_username, user_email,
            user_updated_at, user_pk
        ))

        if cursor.rowcount != 1:
            raise Exception(texts.get("update_failed", "Update failed"))

        db.commit()

        q = "SELECT * FROM users WHERE user_pk = %s"
        cursor.execute(q, (user_pk,))
        updated_user = cursor.fetchone()
        if updated_user:
            updated_user.pop("user_password", None)
            session["user"] = updated_user

        session["message"] = texts.get("profile_updated", "Profile updated successfully")
        session["message_type"] = "success"
        return redirect(url_for("show_profile", lan=lan))

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()

        old_values = request.form.to_dict()
        error_str = str(ex).lower()

        # Show inline field error
        if "username" in error_str:
            old_values.pop("user_username", None)
            return render_template("update_profile.html",
                                   message=texts.get("invalid_username", "Invalid username"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_username_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "first_name" in error_str:
            old_values.pop("user_name", None)
            return render_template("update_profile.html",
                                   message=texts.get("invalid_first_name", "Invalid first name"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_name_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "last_name" in error_str:
            old_values.pop("user_last_name", None)
            return render_template("update_profile.html",
                                   message=texts.get("invalid_last_name", "Invalid last name"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_last_name_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "invalid_email" in error_str:
            old_values.pop("user_email", None)
            return render_template("update_profile.html",
                                   message=texts.get("invalid_email", "Invalid email"),
                                   message_type="error",
                                   old_values=old_values,
                                   user_email_error="input_error",
                                   lan=lan,
                                   languages=texts)

        if "users.user_email" in error_str:
            session["message"] = texts.get("email_exists", "Email already exists")
            session["message_type"] = "error"
            return redirect(url_for("show_profile", lan=lan))

        if "users.user_username" in error_str:
            session["message"] = texts.get("username_exists", "Username already exists")
            session["message_type"] = "error"
            return redirect(url_for("show_profile", lan=lan))

        session["message"] = texts.get("unknown_error", str(ex))
        session["message_type"] = "error"
        return redirect(url_for("show_profile", lan=lan))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


###############################
@app.delete("/<lan>/user")
def delete_user(lan):
    try:
        lan = session.get("lan", lan)
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        user = session.get("user")
        if not user:
            raise Exception("no_user_logged_in")

        user_pk = user["user_pk"]
        deleted_at = int(time.time())

        db, cursor = x.db()
        q = "UPDATE users SET user_deleted_at = %s WHERE user_pk = %s"
        cursor.execute(q, (deleted_at, user_pk))
        if cursor.rowcount != 1:
            raise Exception("delete_failed")

        db.commit()
        session.pop("user", None)

        message = texts.get("delete_success", "User account deleted successfully.")

        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-success">{message}</div>
            </div>
        </mixhtml>
        <mixhtml mix-delay="2000" mix-redirect="/{lan}/login"></mixhtml>
        """

    except Exception as ex:
        ic(ex)

        if "db" in locals():
            db.rollback()

        lan = session.get("lan", lan)
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        message = texts.get("delete_failed", "An error occurred while deleting the user.")

        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-error">{message}</div>
            </div>
        </mixhtml>
        """

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/reset-password/<verification_key>")
def show_reset_password_default():
    return redirect(url_for("reset-password", lan="en"))

@app.get("/<lan>/reset-password/<verification_key>")
def show_reset_password(verification_key, lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: 
            lan = "en"
            session["lan"] = lan
        texts = languages.languages[lan]
        return render_template("reset_password.html", verification_key=verification_key, title=texts["page_title_reset"], languages=texts)
    except Exception as ex:
        ic(ex)
        return "Error loading reset form", 500


###############################
@app.post("/<lan>/reset-password/<verification_key>")
def reset_password(verification_key, lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed:
            lan = "en"
        session["lan"] = lan
        texts = languages.languages[lan]

        new_password = x.validate_user_password(texts)
        hashed_password = generate_password_hash(new_password)

        db, cursor = x.db()

        # Make sure the key is valid and not used
        q = "SELECT user_pk FROM users WHERE user_verification_key = %s AND user_verified_at != 0"
        cursor.execute(q, (verification_key,))
        user = cursor.fetchone()
        if not user:
            raise Exception(texts["reset_invalid_link"])

        # Update the password and invalidate the key
        q_update = """
        UPDATE users
        SET user_password = %s,
            user_verification_key = NULL,
            user_updated_at = %s
        WHERE user_pk = %s
        """
        cursor.execute(q_update, (hashed_password, int(time.time()), user["user_pk"]))
        db.commit()

        session["message"] = texts["reset_success"]
        session["message_type"] = "success"
        return redirect(url_for("show_login", lan=lan))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        session["message"] = ex.args[0] if ex.args else texts.get("reset_failed", "Password reset failed.")
        session["message_type"] = "error"
        return redirect(url_for("show_reset_password", verification_key=verification_key, lan=lan))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/single-item/<item_pk>")
def show_single_item_default(item_pk):
    return redirect(url_for("show_single_item", lan="en", item_pk=item_pk))

@app.get("/<lan>/single-item/<item_pk>")
def show_single_item(item_pk, lan):
    try:
        languages_allowed = ["en", "dk"]
        if lan not in languages_allowed: 
            lan = "en"
        session["lan"] = lan
        texts = languages.languages[lan]

        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_pk = %s AND item_blocked_at = 0 AND item_deleted_at = 0"
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        if not item:
            session["message"] = texts.get("item_not_found", "The requested item does not exist.")
            session["message_type"] = "error"
            return redirect(url_for("show_index", lan=lan))  

        with open("rates.txt", "r") as file:
            rates = json.load(file)

        page_title = f"{item['item_name']} | {texts['page_title_item_suffix']}"

        return render_template("item_single_view.html", title=page_title, item=item, rates=rates, languages=texts)

    except Exception as ex:
        ic(ex)
        session["message"] = texts.get("item_error", "Error loading item.")
        session["message_type"] = "error"
        return redirect(url_for("show_index", lan=lan))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.delete("/<lan>/item/<item_pk>")
def delete_item(lan, item_pk):
    try:
        lan = session.get("lan", lan)
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        # Check if admin or owner, if needed – optional
        # user = session.get("user")
        # if not user:
        #     raise Exception("no_user_logged_in")

        deleted_at = int(time.time())

        db, cursor = x.db()
        q = "UPDATE items SET item_deleted_at = %s WHERE item_pk = %s"
        cursor.execute(q, (deleted_at, item_pk))
        if cursor.rowcount != 1:
            raise Exception("delete_failed")

        db.commit()

        message = texts.get("delete_item_success", "Item deleted successfully.")

        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-success">{message}</div>
            </div>
        </mixhtml>
        <mixhtml mix-delay="2000" mix-redirect="/{lan}/profile"></mixhtml>
        <mixhtml mix-remove="#item-{item_pk}"></mixhtml>
        """

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()

        lan = session.get("lan", lan)
        if lan not in ["en", "dk"]:
            lan = "en"
        texts = languages.languages[lan]

        message = texts.get("delete_item_failed", "An error occurred while deleting the item.")

        return f"""
        <mixhtml mix-replace="#toast-container">
            <div class="toast-container">
                <div class="toast toast-error">{message}</div>
            </div>
        </mixhtml>
        """

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
