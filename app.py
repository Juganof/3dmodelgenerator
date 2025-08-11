from flask import Flask, jsonify, render_template, request
from bot import MarktplaatsBot
import os

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


@app.route("/check", methods=["GET"])
def check():
    bot.check_negotiations()
    return jsonify({"status": "checked"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
