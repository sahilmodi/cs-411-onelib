from app import app
from app import database as db_helper

from flask import jsonify

@app.route("/")
def homepage():
    users = db_helper.test()
    return jsonify({r[0]:str(r[1:]) for r in users})

@app.route("/add")
def add():
    db_helper.add_borrowed_book(0, 0, "019509199X")
    bb = db_helper.read_from_table("BorrowedBook")
    return jsonify({r[0]:str(r[1:]) for r in bb})