import re
from flask.helpers import url_for

from werkzeug.utils import redirect
from app import app
from app import database as db_helper

from flask import jsonify, render_template, request, flash

from app.utils import render_template_with_nav

@app.route("/")
def homepage():
    books = db_helper.test()
    data = {"status":True, "books":books}

    # advanced queries
    data["top_books"] = db_helper.advanced_query_top_books()
    data["top_users"] = db_helper.advanced_query_top_users()
    return render_template_with_nav("index.html", **data)


@app.route("/index.html")
def index():
    return homepage()

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
    return render_template_with_nav("borrow_book.html", **data)



@app.route("/add")
def add():
    db_helper.add_borrowed_book(0, 0, "019509199X")
    bb = db_helper.read_from_table("BorrowedBook")
    return jsonify({r[0]:str(r[1:]) for r in bb})


@app.route("/search_book.html", methods=['GET', 'POST'])
def search_book():
    if request.method == "POST":
        spbook = db_helper.fetch_spbook(request.values['title'])
        #print(spbook)
        data = {"status":True, "books":spbook}
        return render_template_with_nav("search_book.html", **data)
    return render_template_with_nav("search_book.html")

  
@app.route("/review")
def reviewpage():
    '''Define reviewpage'''
    reviews = db_helper.fetch_allreview()
    isbns=842332251
    return render_template_with_nav("review.html",reviews=reviews,isbns=isbns)

@app.route("/review/<string:isbn>")
def bookreviewpage(isbn):
    '''Define reviewpage'''
    reviews = db_helper.fetch_bookreview(isbn)
    isbns=isbn
    return render_template_with_nav("review.html",reviews=reviews,isbns=isbns)

@app.route("/insertreview/<string:isbn>/<int:user_id>/<string:date>/<int:starrating>/<string:text>", methods=['POST'])
def insertreview(isbn,user_id,date,starrating,text):
    """ recieves post requests to add new task """
    try:
        db_helper.insert_new_review(isbn,user_id,date,starrating,text)
        result = {'success': True, 'response': 'Done'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)

@app.route("/deletereview/<string:isbn>/<int:user_id>", methods=['POST'])
def deletereview(isbn,user_id):
    try:
        db_helper.remove_review(isbn,user_id)
        result = {'success': True, 'response': 'Done'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)

@app.route("/editreview/<string:isbn>/<int:user_id>/<string:date>/<int:starrating>/<string:text>", methods=['POST'])
def updatereview(isbn,user_id,date,starrating,text):
    try:
        db_helper.update_review(isbn,user_id,date,starrating,text)
        result = {'success': True, 'response': 'Done'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)
