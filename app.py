import os

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from bot import MarktplaatsBot

load_dotenv()
app = Flask(__name__)
bot = MarktplaatsBot()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword")
    if not keyword:
        return jsonify({"error": "keyword required"}), 400
    listings = bot.search_and_analyze(keyword)
    return jsonify({"results": listings})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
