from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Andrea"  # This should return "Hello Andrea"

if __name__ == "__main__":
    app.run()
