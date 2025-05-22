from flask import request
import mysql.connector
import re
import uuid
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)


##############################
def db():
    db = mysql.connector.connect(
        host = "mysql",      # Replace with your MySQL server's address or docker service name "mysql"
        user = "root",  # Replace with your MySQL username
        password = "password",  # Replace with your MySQL password
        database = "shelter"   # Replace with your MySQL database name
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor


##############################
USER_USERNAME_MIN = 2
USER_USERNAME_MAX = 20
USER_USERNAME_REGEX = f"^.{{{USER_USERNAME_MIN},{USER_USERNAME_MAX}}}$"
def validate_user_username(texts):
    user_username = request.form.get("user_username", "").strip()
    if not re.match(USER_USERNAME_REGEX, user_username): raise Exception(texts["invalid_username"])
    return user_username


##############################
USER_NAME_MIN = 2
USER_NAME_MAX = 20
USER_NAME_REGEX = f"^.{{{USER_NAME_MIN},{USER_NAME_MAX}}}$"
def validate_user_name(texts):
    user_name = request.form.get("user_name", "").strip()
    if not re.match(USER_NAME_REGEX, user_name): raise Exception(texts["invalid_first_name"])
    return user_name


##############################
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
USER_LAST_NAME_REGEX = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"
def validate_user_last_name(texts):
    user_last_name = request.form.get("user_last_name", "").strip()
    if not re.match(USER_LAST_NAME_REGEX, user_last_name): raise Exception(texts["invalid_last_name"])
    return user_last_name

##############################
USER_EMAIL_REGEX = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
def validate_user_email(texts):
    user_email = request.form.get("user_email", "").strip()
    if not re.match(USER_EMAIL_REGEX, user_email):
        raise Exception(texts["invalid_email"])  # Use localized error message
    return user_email

##############################
USER_PASSWORD_MIN = 6
USER_PASSWORD_MAX = 20
USER_PASSWORD_REGEX = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"
def validate_user_password(texts):
    user_password = request.form.get("user_password", "").strip()
    if len(user_password) < USER_PASSWORD_MIN or len(user_password) > USER_PASSWORD_MAX:
        raise Exception(texts["invalid_password"]) 
    return user_password

##############################
PAGE_NUMBER_REGEX = "^[1-9][0-9]*$"
def validate_page_number(page_number):
    error = "page number not valid"
    if not re.match(PAGE_NUMBER_REGEX, page_number): raise Exception(error)
    return int(page_number)

##############################
ITEM_NAME_MIN = 2
ITEM_NAME_MAX = 50
ITEM_NAME_REGEX = f"^.{{{ITEM_NAME_MIN},{ITEM_NAME_MAX}}}$"
def validate_item_name():
    item_name = request.form.get("item_name", "").strip()
    if not re.match(ITEM_NAME_REGEX, item_name):
        raise Exception("invalid_shelter_name")
    return item_name

##############################
ITEM_ADDRESS_MIN = 5
ITEM_ADDRESS_MAX = 100
ITEM_ADDRESS_REGEX = f"^.{{{ITEM_ADDRESS_MIN},{ITEM_ADDRESS_MAX}}}$"
def validate_item_address():
    item_address = request.form.get("item_address", "").strip()
    if not re.match(ITEM_ADDRESS_REGEX, item_address):
        raise Exception("invalid_address")
    return item_address


##############################
LAT_LON_REGEX = "^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$"
def validate_item_lat():
    item_lat = request.form.get("item_lat", "").strip()
    if not re.match(LAT_LON_REGEX, item_lat):
        raise Exception("invalid_latitude")
    return float(item_lat)

def validate_item_lon():
    item_lon = request.form.get("item_lon", "").strip()
    if not re.match(LAT_LON_REGEX, item_lon):
        raise Exception("invalid_longitude")
    return float(item_lon)


##############################
ITEM_PRICE_MIN = 0
ITEM_PRICE_MAX = 1000000   
ITEM_PRICE_REGEX = f"^([1-9][0-9]{{0,6}}|0)(\.[0-9]{{1,2}})?$"
def validate_item_price():
    item_price = request.form.get("item_price", "").strip()
    if not re.match(ITEM_PRICE_REGEX, item_price):
        raise Exception("invalid_price")
    item_price = float(item_price)
    if item_price < ITEM_PRICE_MIN or item_price > ITEM_PRICE_MAX:
        raise Exception("invalid_price")
    return item_price



##############################
ALLOWED_EXSTENSIONS = ["png", "jpg", "jpeg", "gif"]
MAX_FILE_SIZE = 1 * 1024 * 1024 #1MB size in bytes
MAX_IMAGE_UPLOAD = 5
MIN_IMAGE_UPLOAD = 3

def validate_item_images():
    images_names = []
    files = request.files.getlist("images")  # <-- Changed from "files" to "images"

    if not files or all(not f.filename for f in files):
        raise Exception("no_images_uploaded")

    if len(files) < MIN_IMAGE_UPLOAD:
        raise Exception("not_enough_images_uploaded")

    if len(files) > MAX_IMAGE_UPLOAD:
        raise Exception("max_upload_exceeded")

    for the_file in files:
        file_size = len(the_file.read())
        file_name, file_extension = os.path.splitext(the_file.filename)
        the_file.seek(0)
        file_extension = file_extension.lstrip(".").lower()
        if file_extension not in ALLOWED_EXSTENSIONS:
            raise Exception("file_extension_not_allowed")
        if file_size > MAX_FILE_SIZE:
            raise Exception("file_too_large")

        new_file_name = f"{uuid.uuid4().hex}.{file_extension}"
        images_names.append(new_file_name)
        file_path = os.path.join("static/uploads", new_file_name)
        the_file.save(file_path)

    return images_names


##############################
SEARCH_FOR_MIN = 2
SEARCH_FOR_MAX = 100
SEARCH_FOR_REGEX = f"^[a-zA-Z0-9æøåÆØÅ .,'\"!?()-]{{{SEARCH_FOR_MIN},{SEARCH_FOR_MAX}}}$"
def validate_search_for(texts):
    search_for = request.args.get("q", "").strip()
    if not re.match(SEARCH_FOR_REGEX, search_for): raise Exception(texts["no_results"])
    return search_for




##############################
def send_email(user_name, user_last_name, user_email, verification_key, lan):
    try:

        sender_email = "andrea.hauberg1@gmail.com"
        password = "ffna legf lmja vzdv"  

        receiver_email = user_email

        if lan == "dk":
            subject = "Velkommen"
            greeting = f"Tak {user_name} {user_last_name} for din tilmelding. Velkommen."
            verify_text = f"""For at bekræfte din konto, <a href="http://127.0.0.1/dk/verify/{verification_key}">klik her</a>."""
        else:
            subject = "Welcome"
            greeting = f"Thank you {user_name} {user_last_name} for signing up. Welcome."
            verify_text = f"""To verify your account, please <a href="http://127.0.0.1/en/verify/{verification_key}">click here</a>."""
            
        message = MIMEMultipart()
        message["From"] = "Shelter Service Message" 
        message["To"] = receiver_email
        message["Subject"] = subject

        body = f"""
                <html>
                    <body>
                        <p>{greeting}</p>
                        <p>{verify_text}</p>
                    </body>
                </html>
                """
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        ic("Email sent successfully!")

        return "email sent"
       
    except Exception as ex:
        ic(ex)
        raise Exception("cannot send email")
    finally:
        pass




##############################
def send_reset_email(user_name, user_email, verification_key, lan):
    try:
        sender_email = "andrea.hauberg1@gmail.com"
        password = "ffna legf lmja vzdv"  

        receiver_email = user_email

        if lan == "dk":
            subject = "Nulstil din adgangskode"
            reset_link = f"http://127.0.0.1/dk/reset-password/{verification_key}"
            body_greeting = f"Hej {user_name},"
            body_text = f"""
            Vi har modtaget en anmodning om at nulstille din adgangskode.
            Klik venligst <a href="{reset_link}">her for at nulstille din adgangskode</a>.
            Hvis du ikke har anmodet om dette, kan du ignorere denne email.
            """
        else:
            subject = "Reset Your Password"
            reset_link = f"http://127.0.0.1/en/reset-password/{verification_key}"
            body_greeting = f"Hello {user_name},"
            body_text = f"""
            We received a request to reset your password.
            Please <a href="{reset_link}">click here to reset your password</a>.
            If you didn't request this, please ignore this email.
            """

        message = MIMEMultipart()
        message["From"] = "Shelter Service Message"
        message["To"] = receiver_email
        message["Subject"] = subject

        body = f"""
            <html>
                <body>
                    <p>{body_greeting}</p>
                    <p>{body_text}</p>
                </body>
            </html>
            """
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        ic("Reset email sent successfully!")
        return "reset email sent"

    except Exception as ex:
        ic(ex)
        raise Exception("cannot send reset email")
