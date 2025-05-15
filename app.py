from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import time
import x
import json
import os
import uuid
import requests

app = Flask(__name__)

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


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


##############################
@app.get("/")
def show_index():
    try:
        db, cursor = x.db()
        q = "SELECT * FROM items ORDER BY item_created_at LIMIT 2"
        cursor.execute(q)
        items = cursor.fetchall()
        rates = ""
        with open("rates.txt", "r") as file:
            rates = file.read() # this is text that looks like json
        ic(rates)
        # Convert the text rates to json
        rates = json.loads(rates)
        is_session = False
        if session.get("user"): is_session = True
        active_index = "active"
        return render_template("index.html", title="Shelter", items=items, is_session = is_session, active_index=active_index, rates=rates)
    except Exception as ex:
        ic(ex)
        return "ups"
    finally:
        pass


##############################
@app.get("/profile")
def show_profile():
    error_message = request.args.get("error_message", "")
    try:
        db, cursor = x.db()

        # Fetch all items for the user (or all items)
        q_items = "SELECT * FROM items ORDER BY item_created_at DESC"
        cursor.execute(q_items)
        items = cursor.fetchall()

        # Fetch images for all those items
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

        is_session = False
        if session.get("user"):
            is_session = True
        active_profile = "active"

        return render_template("profile.html", 
                               title="Profile",
                               user=session["user"], 
                               x=x, 
                               is_session=is_session,
                               active_profile=active_profile, 
                               error_message=error_message,
                               old_values={},
                               items=items,
                               images_by_item=images_by_item)

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
def show_signup():
    active_signup ="active"
    error_message = request.args.get("error_message", "")
    try:
        return render_template("signup.html", title="Shelter Signup", x=x, active_signup=active_signup, 
                           error_message=error_message,
                           old_values={})
    except Exception as ex:
        ic(ex)
    finally:
       pass

##############################
@app.post("/signup")
def signup():
    try:
        user_pk = str(uuid.uuid4())
        user_name = x.validate_user_name()
        user_username = x.validate_user_username()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)
        verification_key = str(uuid.uuid4())
        # ic(hashed_password)
        user_created_at = int(time.time())
        user_updated_at = int(time.time())


        q = """INSERT INTO users
(user_pk, user_name, user_last_name, user_email, user_username, user_password,
 user_created_at, user_updated_at, user_deleted_at,
 user_is_blocked, user_verified_at, user_verification_key, user_role)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0, %s, 'user')
"""


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
            raise Exception("System under maintenance")
        
        db.commit()

        x.send_email(user_name, user_email, verification_key)
        return redirect(url_for("show_login", message="Signup ok"))
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        old_values = request.form.to_dict()

        if "username" in str(ex):
            old_values.pop("user_username", None)
            return render_template("signup.html",                                   
                error_message="Invalid username", old_values=old_values, user_user_name_error="input_error")
        if "first name" in str(ex):
            old_values.pop("user_name", None)
            return render_template("signup.html",
                error_message="Invalid name", old_values=old_values, user_name_error="input_error")
        if "last name" in str(ex):
            old_values.pop("user_last_name", None)
            return render_template("signup.html",
                error_message="Invalid last name", old_values=old_values, user_last_name_error="input_error")
        if "Invalid email" in str(ex):
            old_values.pop("user_email", None)
            return render_template("signup.html",
                error_message="Invalid email", old_values=old_values, user_email_error="input_error")
        if "password" in str(ex):
            old_values.pop("user_password", None)
            return render_template("signup.html",
                error_message="Invalid password", old_values=old_values, user_password_error="input_error")

        if "users.user_email" in str(ex):
            return redirect(url_for("show_signup",
                error_message="Email already exists", old_values=old_values, email_error=True))
        if "users.user_username" in str(ex): 
            return redirect(url_for("show_signup", 
                error_message="Username already exists", old_values=old_values, user_user_name_error=True))
        return redirect(url_for("show_signup", error_message=ex.args[0]))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close() 



#############################
@app.get("/verify/<verification_key>")
def verify(verification_key):
    try:
        db, cursor = x.db()
 
        q = "SELECT user_pk FROM users WHERE user_verification_key = %s AND user_verified_at = 0"

        cursor.execute(q, (verification_key,))
        user = cursor.fetchone()
 
        if not user:
            return "Invalid or already used verification key."
        current_time = int(time.time())
        q_update = """UPDATE users
                      SET user_verified_at = %s,
                        user_verification_key = NULL
                      WHERE user_pk = %s"""
        cursor.execute(q_update, (current_time, user["user_pk"]))
        db.commit()
        return "Your account has been verified!"
    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()
        return "Verification failed", 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()



##############################
@app.get("/login")
def show_login():
    active_login = "active"
    message = request.args.get("message", "")
    try:
        return render_template("login.html", title="Shelter Login", x=x, active_login = active_login,  message = message, old_values={})
    except Exception as ex:
        ic(ex)
    finally:
       pass


##############################
@app.post("/login")
def login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_email = %s"
        cursor.execute(q, (user_email,))
        user = cursor.fetchone() 
        ic(user)
        if not user: raise Exception("User not found")
        if user["user_verified_at"] == 0: raise Exception("User not verified")
        if not check_password_hash(user["user_password"], user_password):
            raise Exception("Invalid credentials")
        user.pop("user_password")
        session["user"] = user  
    
        if user["user_role"] == "admin":
            return redirect(url_for("show_admin"))
        else:
            return redirect(url_for("show_profile"))
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        old_values = request.form.to_dict()

        if "Invalid email" in str(ex):
            old_values.pop("user_email", None)
            return render_template("login.html",
                message="Invalid email", old_values=old_values)
        
        if "password" in str(ex):
            old_values.pop("user_password", None)
            return render_template("login.html",
                message="Invalid password", old_values=old_values)
        return redirect(url_for("show_login", message=ex.args[0]))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.get("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("show_login"))


##############################
@app.get("/items/<item_pk>")
def get_item_by_pk(item_pk):
    try:
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_pk = %s"
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        rates= ""
        with open("rates.txt", "r") as file:
            rates = file.read() # this is text that looks like json
            rates = json.loads(rates)

        html_item = render_template("_item.html", item=item, rates=rates)
        return f"""
            <mixhtml mix-replace="#item">
                {html_item}
            </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        if "company_ex page number" in str(ex):
            return """
                <mixhtml mix-top="body">
                    page number invalid
                </mixhtml>
            """
        # worst case, we cannot control exceptions
        return """
            <mixhtml mix-top="body">
                ups
            </mixhtml>
        """
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()





##############################
@app.get("/items/page/<page_number>")
def get_items_by_page(page_number):
    try:
        page_number = x.validate_page_number(page_number)
        items_per_page = 2
        offset = (page_number-1) * items_per_page
        extra_item = items_per_page + 1
        db, cursor = x.db()
        q = "SELECT * FROM items ORDER BY item_created_at LIMIT %s OFFSET %s"
        cursor.execute(q, (extra_item, offset))
        items = cursor.fetchall()
        html = ""
        
        rates= ""
        with open("rates.txt", "r") as file:
            rates = file.read() # this is text that looks like json
            rates = json.loads(rates)

        for item in items[:items_per_page]:
            i = render_template("_item_mini.html", item=item, rates=rates)
            html += i
        button = render_template("_button_more_items.html", page_number=page_number + 1)
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
            return """
                <mixhtml mix-top="body">
                    page number invalid
                </mixhtml>
            """
        # worst case, we cannot control exceptions
        return """
            <mixhtml mix-top="body">
                ups
            </mixhtml>
        """
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
@app.get("/search")
def search():
    try:
        search_for = request.args.get("q", "") # car
        # TODO: validate search_for
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_name LIKE %s"
        cursor.execute(q, (f"{search_for}%",))
        rows = cursor.fetchall()
        ic(rows)
        return rows # [{'item_name': 'aa1', 'item_pk': '193e055791ed4f...
    except Exception as ex:
        ic(ex)
        return "x", 400




#################################
@app.post("/add-item")
def add_item():
    try:
        item_pk = str(uuid.uuid4())
        item_name = x.validate_item_name()
        item_address = x.validate_item_address()
        item_lat = x.validate_item_lat()
        item_lon = x.validate_item_lon()
        item_created_at = int(time.time())
        item_price = x.validate_item_price()

        # Billedhåndtering
        uploaded_files = request.files.getlist("images")
        if not uploaded_files:
            raise Exception("No images uploaded")

        image_values = ""
        timestamp = int(time.time())
        first_image_filename = None

        for idx, file in enumerate(uploaded_files):
            if file.filename == "":
                continue
            filename = secure_filename(file.filename)
            filepath = os.path.join("static/uploads", filename)
            file.save(filepath)

            image_pk = uuid.uuid4().hex
            image_values += f"('{image_pk}', '{item_pk}', '{filename}', {timestamp}),"

            if idx == 0:
                first_image_filename = filename  # sæt første billede som hovedbillede

        db, cursor = x.db()

        # Indsæt item med hovedbillede
        q_item = """INSERT INTO items
                    (item_pk, item_name, item_address, item_lat, item_lon, item_image, item_created_at, item_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(q_item, (
            item_pk,
            item_name,
            item_address,
            item_lat,
            item_lon,
            first_image_filename,
            item_created_at,
            item_price
        ))
        if cursor.rowcount != 1:
            raise Exception("Could not insert item")

        # Indsæt billeder
        if image_values:
            image_values = image_values.rstrip(",")
            q_images = f"INSERT INTO images (image_pk, item_pk, image_name, created_at) VALUES {image_values}"
            cursor.execute(q_images)

        db.commit()
        return redirect(url_for("show_index"))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        old_values = request.form.to_dict()

        # fejlbeskeder
        if "Shelter name" in str(ex):
            old_values.pop("item_name", None)
            return render_template("add-item.html", error_message="input_error")
        if "Address" in str(ex):
            old_values.pop("item_address", None)
            return render_template("add-item.html", error_message="input_error")
        if "latitude" in str(ex):
            old_values.pop("item_lat", None)
            return render_template("add-item.html", error_message="input_error")
        if "longitude" in str(ex):
            old_values.pop("item_longitude", None)
            return render_template("add-item.html", error_message="input_error")
        if "price" in str(ex):
            old_values.pop("item_price", None)
            return render_template("add-item.html", error_message="input_error")

        return redirect(url_for("show_profile", error_message=str(ex)))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()





###############################
@app.get("/admin")
def show_admin():
    try:
        db, cursor = x.db()

        # Get users
        q_users = "SELECT * FROM users"
        cursor.execute(q_users)
        users = cursor.fetchall()

        # Get items (like on index)
        q_items = "SELECT * FROM items ORDER BY item_created_at"
        cursor.execute(q_items)
        items = cursor.fetchall()

        # Load rates from file
        rates = ""
        with open("rates.txt", "r") as file:
            rates = file.read()
        rates = json.loads(rates)  # Convert to dict

        # Session check
        is_session = 'user' in session

        # Optional: Set 'active_admin' to highlight current nav
        active_admin = "active"

        return render_template("admin.html",
                               users=users,
                               items=items,
                               rates=rates,
                               is_session=is_session,
                               active_admin=active_admin)
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
        pass



##############################
@app.patch("/block/<user_pk>")
def block_user(user_pk):
    try:
        # validate the user_pk
        db, cursor = x.db()
        q = "UPDATE users SET user_blocked_at = %s WHERE user_pk = %s"
        blocked_at = int(time.time())
        cursor.execute(q, (blocked_at, user_pk))
        db.commit()
        user = {
            "user_pk":user_pk
        }
        button_unblock = render_template("_button_unblock_user.html", user=user)
        return f"""
        <mixhtml mix-replace="#block-{user_pk}">
            {button_unblock}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
       pass


##############################
@app.patch("/unblock/<user_pk>")
def unblock_user(user_pk):
    try:
        # validate the user_pk
        # Connect to the db and unblock the user   
        # validate the user_pk
        db, cursor = x.db()
        q = "UPDATE users SET user_blocked_at = %s WHERE user_pk = %s"  
        cursor.execute(q, (0, user_pk))
        db.commit()              
        user = {
            "user_pk":user_pk
        }          
        button_block = render_template("_button_block_user.html", user=user)
        return f"""
        <mixhtml mix-replace="#unblock-{user_pk}">
            {button_block}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
       pass




##############################
@app.patch("/block/<item_pk>")
def block_item(item_pk):
    try:
        db, cursor = x.db()
        blocked_at = int(time.time())

        print(f"Trying to block item: {item_pk} at {blocked_at}")

        q = "UPDATE items SET item_blocked_at = %s WHERE item_pk = %s"
        cursor.execute(q, (blocked_at, item_pk))
        db.commit()

        cursor.execute("SELECT item_blocked_at FROM items WHERE item_pk = %s", (item_pk,))
        updated = cursor.fetchone()

        item = {"item_pk": item_pk}
        button_unblock = render_template("_button_unblock_item.html", item=item)
        return f"""
        <mixhtml mix-replace="#block-{item_pk}">
            {button_unblock}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        return str(ex)


##############################
@app.patch("/unblock/<item_pk>")
def unblock_item(item_pk):
    try:
        db, cursor = x.db()
        q = "UPDATE items SET item_blocked_at = %s WHERE item_pk = %s"
        cursor.execute(q, (0, item_pk))
        db.commit()
        item ={
            "item_pk": item_pk
        }
        button_block = render_template("_button_block_item.html", item=item)
        return f"""
        <mixhtml mix-replace="#unblock-{item_pk}">
            {button_block}
        </mixhtml>
        """
    except Exception as ex:
        ic(ex)
        return str(ex)
    finally:
       pass

@app.get("/items/<item_pk>/edit")
def show_edit_item(item_pk):
    try:
        db, cursor = x.db()
        q = "SELECT * FROM items WHERE item_pk = %s"
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()
        if not item:
            return "Item not found", 404

        return render_template("edit_item.html", item=item, title="Edit Item")
    except Exception as ex:
        ic(ex)
        return "Error loading item", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



@app.post("/update-item/<item_pk>")
def update_item_inline(item_pk):
    try:
        item_name = x.validate_item_name()
        item_address = x.validate_item_address()
        item_lat = x.validate_item_lat()
        item_lon = x.validate_item_lon()
        item_price = x.validate_item_price()
        item_updated_at = int(time.time())

        db, cursor = x.db()
        q = """UPDATE items 
               SET item_name = %s, item_address = %s, item_lat = %s, item_lon = %s, item_price = %s, item_updated_at = %s 
               WHERE item_pk = %s"""
        cursor.execute(q, (
            item_name, item_address, item_lat, item_lon, item_price, item_updated_at, item_pk
        ))

        if cursor.rowcount != 1:
            raise Exception("Update failed")

        db.commit()
        return redirect(url_for("show_profile"))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return redirect(url_for("show_profile", error_message=str(ex)))

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



@app.post("/update-profile/<user_pk>")
def update_profile(user_pk):
    try:
        # if "user_pk" not in session:
        #     return redirect(url_for("show_login"))

        # user_pk = session["user_pk"]

        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_username = x.validate_user_username()
        user_email = x.validate_user_email()
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
            raise Exception("Nothing was updated")

        db.commit()

        q = "SELECT * FROM users WHERE user_pk = %s"
        cursor.execute(q, (user_pk,))
        updated_user = cursor.fetchone()
        if updated_user:
            updated_user.pop("user_password", None)  # remove sensitive data
            session["user"] = updated_user

        return redirect(url_for("show_profile"))

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return redirect(url_for("show_profile", error_message=str(ex)))
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()
