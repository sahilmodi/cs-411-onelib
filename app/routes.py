from app import app
from app import database as db_helper

from flask import jsonify, render_template

@app.route("/")
def homepage():
    books = db_helper.test()
    print(books)
    data = {"status":True, "books":books}
    return render_template("index.html", **data)

@app.route("/add")
def add():
    db_helper.add_borrowed_book(0, 0, "019509199X")
    bb = db_helper.read_from_table("BorrowedBook")
    return jsonify({r[0]:str(r[1:]) for r in bb})