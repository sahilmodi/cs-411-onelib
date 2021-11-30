from flask.helpers import url_for

from werkzeug.utils import redirect
from app import app
from app import database as db_helper

from flask import jsonify, render_template, request, flash

from app.utils import render_template_with_nav
import app.user as user

@app.route("/")
def homepage():
    books = db_helper.test()
    data = {"status":True, "books":books}
    return render_template_with_nav("index.html", **data)


@app.route("/index.html")
def index():
    return homepage()


@app.route("/top_charts.html")
def top_charts():
    data = {}
    data["top_books"] = db_helper.advanced_query_top_books()
    data["top_users"] = db_helper.advanced_query_top_users()
    return render_template_with_nav("top_charts.html", **data)


@app.route("/borrow_book.html", methods=['GET', 'POST'])
def borrow_book():
    if request.method == "POST":
        if int(request.values['return']) == 0:
            db_helper.checkout_book(request.values['user_id'], request.values['library_id'], request.values['isbn'])
        else:
            db_helper.return_book(request.values['user_id'], request.values['library_id'], request.values['isbn'])
        redirect(url_for("borrow_book"))
    
    books = db_helper.get_rentable_books(0)
    borrowed_books = db_helper.get_borrowed_books(user_id=user.get_current_user_id(), amount=25)
    data = {"books":books, "borrowed_books":borrowed_books}

    fee, score = db_helper.get_fee_score(user_id=user.get_current_user_id())
    data['confirm_msg'] = f"You have a library score of {score:0.2f} and owe ${fee:0.2f}."
    if score < 0.2 or fee > 10:
        data['confirm_msg'] += " Due date automatically reduced to 1 week."
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
        data = {"status":True, "books":spbook}
        return render_template_with_nav("search_book.html", **data)
    return render_template_with_nav("search_book.html")


@app.route("/search_library.html", methods=['GET', 'POST'])
def search_library():
    if request.method == "POST":
        splibrary = db_helper.fetch_splibrary(request.values['zipcode'])
        data = {"status":True, "libraries":splibrary}
        return render_template("search_library.html", **data)
    return render_template("search_library.html")

  
@app.route("/review")
def reviewpage():
    '''Define reviewpage'''
    reviews = db_helper.fetch_bookreview(842332251)
    isbns=842332251
    bookinfo=db_helper.fetch_bookinfo(842332251)
    bookrate=db_helper.fetch_bookrate(842332251)
    return render_template_with_nav("review.html",reviews=reviews,isbns=isbns,bookinfo=bookinfo,bookrate=bookrate)

@app.route("/review/<string:isbn>")
def bookreviewpage(isbn):
    '''Define reviewpage'''
    reviews = db_helper.fetch_bookreview(isbn)
    bookinfo=db_helper.fetch_bookinfo(isbn)
    isbns=isbn
    bookrate=db_helper.fetch_bookrate(isbn)
    return render_template_with_nav("review.html",reviews=reviews,isbns=isbns,bookinfo=bookinfo,bookrate=bookrate)

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
