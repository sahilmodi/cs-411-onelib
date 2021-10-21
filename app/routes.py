from app import app
from app import database as db_helper

from flask import jsonify

@app.route("/")
def homepage():
    users = db_helper.test()
    return jsonify({r[0]:str(r[1:]) for r in users})