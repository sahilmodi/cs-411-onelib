from app import app
from app import database as db_helper

from flask import jsonify

@app.route("/")
def homepage():
    return jsonify({"status": "ok"})