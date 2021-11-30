from flask.helpers import url_for

from werkzeug.utils import redirect
from app import app
from app import database as db_helper

from flask import jsonify, render_template, request, flash, session

from app.utils import render_template_with_nav
import app.user as user

@app.route('/register', methods=['post','get'])
def register():
    error=None
    success=None
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')

        if len(firstname) < 2: 
            error = "Firstname is too short"
        elif len(password) < 6:
            error = "Password is too short"
        elif password != confirmpassword:
            error = "Passwords do not match"
        # else:
            # db_helper.add
            # query = "INSERT INTO User(id,firstname,lastname,email,password) VALUES (NULL, %s, %s, %s, %s)"
            # cursor.execute(query, (firstname,lastname,email,password))
            # success = "You account has been created"

    return render_template('register.html',error=error,msg=success)

@app.route('/login', methods=['GET', 'POST'])
def login():
    email=request.form.get('email')
    password = request.form.get('password')
    u = user.login(email, password)
    if u is not None:
        if 'current_url' in session:
            print("Redirecting to", session.get('current_url'))
            return redirect(session.get('current_url'))
        return homepage()
    else:
        return render_template('login.html')


def homepage():
    return redirect("/search_book.html")

def check_login(url):
    if user.get_current_user_id() is None:
        session['current_url'] = url
        return redirect("/login")
    return None


@app.route("/")
def base():
    if user.get_current_user_id() is not None:
        return homepage()
    return login()


@app.route("/index.html")
def index():
    return base()

@app.route("/top_charts.html")
def top_charts():
    data = {}
    data["top_books"] = db_helper.advanced_query_top_books()
    data["top_users"] = db_helper.advanced_query_top_users()
    return render_template_with_nav("top_charts.html", **data)


@app.route("/borrow_book.html", methods=['GET', 'POST'])
def borrow_book():
    reload = check_login(request.path)
    if reload:
        return reload

    if request.method == "POST":
        db_helper.return_book(request.values['user_id'], request.values['library_id'], request.values['isbn'])
    
    borrowed_books = db_helper.get_borrowed_books(user_id=user.get_current_user_id())
    data = {"borrowed_books":borrowed_books}
    return render_template_with_nav("borrow_book.html", **data)


@app.route("/search_book.html", methods=['GET', 'POST'])
def search_book():
    reload = check_login(request.path)
    if reload:
        return reload

    data = {}
    if request.method == "POST":
        text = request.values['text']
        title = 'title' in request.values
        author = 'author' in request.values
        publisher = 'publisher' in request.values
        isbn = 'isbn' in request.values
        buyable = 'buyable' in request.values
        spbook = db_helper.fetch_spbook(text, title, author, publisher, isbn, buyable)
        data["books"] = spbook
    
    data['sample'] = db_helper.test()
    return render_template_with_nav("search_book.html", **data)


@app.route("/book/<string:isbn>", methods=['GET', 'POST'])
def book_info(isbn):
    reload = check_login(request.path)
    if reload:
        return reload

    u = user.get_current_user()
    
    if request.method == "POST":
        if int(request.values['return']) == 0:
            db_helper.checkout_book(request.values['user_id'], request.values['library_id'], request.values['isbn'])
        else:
            db_helper.return_book(request.values['user_id'], request.values['library_id'], request.values['isbn'])
        # redirect(f"/book/{request.values['isbn']}")

    data = {}
    fee, score = db_helper.get_fee_score(user_id=u.UserID)
    data['confirm_msg'] = f"You have a library score of {score:0.2f} and owe ${fee:0.2f}."
    if score < 0.2 or fee > 10:
        data['confirm_msg'] += " Due date will automatically be reduced to 1 week."
    data['confirm_msg'] += ' Proceed with checkout?'
    
    data['nearby_libraries'] = db_helper.fetch_splibrary(isbn, u.Zipcode)
    data['book'] = db_helper.fetch_bookinfo(isbn)[0]
    data['rate'] = db_helper.fetch_bookrate(isbn)[0]

    data['borrowed_books'] = db_helper.get_borrowed_books(user_id=u.UserID, amount=25)
    return render_template_with_nav("book_info.html", **data)

  
@app.route("/review")
def reviewpage():
    return redirect("/review/842332251")
    
@app.route("/review/<string:isbn>")
def bookreviewpage(isbn):
    reload = check_login(request.path)
    if reload:
        return reload

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
