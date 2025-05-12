from flask import Flask, render_template, request
from flask_session import Session
import x
import json
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



##############################
@app.get("/")
def view_index():
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
        return render_template("index.html", title="Shelter", items=items, rates=rates)
    except Exception as ex:
        ic(ex)
        return "ups"
    finally:
        pass


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

