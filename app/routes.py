import re
from flask.helpers import url_for

from werkzeug.utils import redirect
from app import app
from app import database as db_helper

from flask import jsonify, render_template, request, flash

@app.route("/")
def homepage():
    books = db_helper.test()
    data = {"status":True, "books":books}

    # advanced queries
    data["top_books"] = db_helper.advanced_query_top_books()
    data["top_users"] = db_helper.advanced_query_top_users()
    print(data["top_books"])
    return render_template("index.html", **data)

@app.route("/borrow_book.html", methods=['GET', 'POST'])
def borrow_book():
    if request.method == "POST":
        if int(request.values['return']) == 0:
            db_helper.checkout_book(request.values['user_id'], request.values['library_id'], request.values['isbn'])
        else:
            db_helper.return_book(request.values['user_id'], request.values['library_id'], request.values['isbn'])
        redirect(url_for("borrow_book"))
    books = db_helper.get_rentable_books(0)
    borrowed_books = db_helper.get_borrowed_books(amount=25)
    data = {"books":books, "borrowed_books":borrowed_books}
    return render_template("borrow_book.html", **data)



@app.route("/add")
def add():
    db_helper.add_borrowed_book(0, 0, "019509199X")
    bb = db_helper.read_from_table("BorrowedBook")
    return jsonify({r[0]:str(r[1:]) for r in bb})