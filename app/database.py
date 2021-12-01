from app import db
import datetime

tables = {"User", "Review", "BorrowedBook", "Library", "LibraryBook", "Book"}

def test():
    return read_from_table("Book", 5)

def _search(table, field, keyword, amount=5):
    assert table in tables
    with db.begin() as conn:
        res = conn.execute(f"SELECT * FROM {table} WHERE {field} LIKE '%{keyword}%").fetchmany(amount)
    return res

def search_review(keyword, amount):
    return _search("Review", "Text", keyword, amount)

def search_library(keyword, amount):
    return _search("Library", "Name", keyword, amount)

def get_rentable_books(library_id, amount=10):
    with db.begin() as conn:
        res = conn.execute(f"SELECT * FROM LibraryBook NATURAL JOIN Library NATURAL JOIN Book WHERE LibraryID={library_id}").fetchmany(amount)
    return [b for b in res]

def get_borrowed_books(user_id, amount=10):
    query = "SELECT User.Name UserName, UserID, DueDate, ReturnDate, ImageURL, Library.Name LibraryName, Title, Author, ISBN, LibraryID FROM BorrowedBook NATURAL JOIN Book NATURAL JOIN User JOIN Library USING (LibraryID)"
    query += f" WHERE UserID={user_id}"
    with db.begin() as conn:
        res = conn.execute(query)
    return [r for r in res]


def checkout_book(user_id, library_id, isbn):
    conn = db.connect()
    res = conn.execute(f"SELECT Quantity, TimeLimitDays FROM LibraryBook WHERE LibraryID={library_id} AND ISBN LIKE '{isbn}'").fetchone()
    if res is None:
        return False
    quantity, time_limit_days = res
    if quantity == 0:
        return False
    if time_limit_days is None:
        q = f"Insert INTO BorrowedBook VALUES ({user_id}, {library_id}, '{isbn}', NULL, NULL)"
    else:
        due_date = datetime.datetime.today().date() + datetime.timedelta(days=time_limit_days)
        q = f"Insert INTO BorrowedBook VALUES ({user_id}, {library_id}, '{isbn}', '{due_date}', NULL)"
    conn.execute(q)
    conn.execute(f"UPDATE LibraryBook SET Quantity = Quantity-1 WHERE LibraryID={library_id} AND ISBN LIKE '{isbn}'")
    conn.close()
    return True

def return_book(user_id, library_id, isbn):
    conn = db.connect()
    conn.execute(f"UPDATE BorrowedBook SET ReturnDate = '{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}' WHERE UserID={user_id} AND LibraryID={library_id} AND ISBN LIKE '{isbn}'")
    conn.execute(f"UPDATE LibraryBook SET Quantity = Quantity+1 WHERE LibraryID={library_id} AND ISBN LIKE '{isbn}'")

    conn.close()
    return True

def get_fee_score(user_id):
    with db.begin() as conn:
        conn.execute(f"CALL CalculateLibraryFeeAndScores({user_id}, @total_fee, @score)")
        r = conn.execute("SELECT @total_fee, @score").fetchone()
    fee, score = r
    return fee, score

def seed_borrowed_books(user_id):
    with db.begin() as conn:
        conn.execute(f"TRUNCATE BorrowedBook")
        conn.execute(f"INSERT INTO BorrowedBook VALUES ({user_id}, 0, '019509199X', '2021-12-16', '2021-11-26')")
        conn.execute(f"INSERT INTO BorrowedBook VALUES ({user_id}, 0, '031202164X', '2021-12-11', '2021-11-26')")
        conn.execute(f"INSERT INTO BorrowedBook VALUES ({user_id}, 0, '1551667320', '2021-11-05', NULL)")

def read_from_table(table, amount=5):
    assert table in tables
    with db.begin() as conn:
        res = conn.execute(f"SELECT * FROM {table} LIMIT {amount}").fetchall()
    return [r for r in res]


def fetch_bookreview(isbn) -> dict:
    conn = db.connect()
    query='SELECT * FROM Review where ISBN LIKE "{}";'.format(isbn)
    query_results = conn.execute(query).fetchall()
    conn.close()
    bookreview = []
    for result in query_results:
        item = {
            "ISBN": result[0],
            "UserID": result[1],
            "Date": result[2],
            "StarRating": result[3],
            "Text": result[4]
        }
        bookreview.append(item)
    return bookreview

def fetch_bookinfo(isbn) ->dict:
    conn = db.connect()
    query='SELECT * FROM Book where ISBN LIKE "{}";'.format(isbn)
    query_results = conn.execute(query).fetchall()
    conn.close()
    bookinfo = []
    for result in query_results:
        item = {
            "ISBN": result[0],
            "Title": result[1],
            "Author": result[2],
            "ImageURl": result[3],
            "Publisher": result[4]
        }
        bookinfo.append(item)
    return bookinfo

def fetch_bookrate(isbn):
    conn = db.connect()
    query='SELECT ROUND(AVG(StarRating),1) FROM Review where ISBN LIKE "{}";'.format(isbn)
    query_results = conn.execute(query)
    conn.close()
    bookrate=[]
    for result in query_results:
        item = {"rate":result[0]}
    bookrate.append(item)
    return bookrate


def remove_review(isbn,user_id) -> None:
    """ remove entries based on ISBN and UserId """
    conn = db.connect()
    query = 'Delete From Review WHERE ISBN LIKE "{}" AND UserID={};'.format(isbn,user_id)
    conn.execute(query)
    conn.close()

def insert_new_review(isbn,user_id,date,starrating,text)->None:
    '''insert a new review'''
    conn = db.connect()
    query='Insert Into Review VALUES ("{}", {}, "{}", {}, "{}");'.format(isbn,user_id,date,starrating,text)
    conn.execute(query)
    conn.close()

def update_review(isbn,user_id,date,starrating,text)->None:
    conn = db.connect()
    query='Update Review set Date="{}", StarRating={}, Text="{}" where ISBN LIKE "{}" and UserID={};'.format(date,starrating,text,isbn,user_id)
    conn.execute(query)
    conn.close()


def delete_review(user_id, isbn):
    conn = db.connect()
    q = f"DELETE FROM Review WHERE UserID = {user_id} AND ISBN LIKE '{isbn}'"
    conn.execute(q)
    conn.close()
    return True

def fetch_spbook(text, title, author, publisher, isbn, buyable, amount=100):
    conn = db.connect()

    q = "SELECT * FROM Book WHERE"
    text_search = []
    if title:
        text_search.append(f"Title LIKE '%%{text}%%'")
    if isbn:
        text_search.append(f"ISBN LIKE '%%{text}%%'")
    if author:
        text_search.append(f"Author LIKE '%%{text}%%'")
    if publisher:
        text_search.append(f"Publisher LIKE '%%{text}%%'")
    
    text_search = " OR ".join(text_search)
    q = f"{q} ({text_search}) LIMIT {amount}"

    spbook = conn.execute(q)
    spbook = [r for r in spbook]

    if buyable:
        q = "SELECT DISTINCT ISBN FROM LibraryBook WHERE Buyable"
        isbns = conn.execute(q)
        isbns = [r for r in isbns]
        valid_isbns = {i.ISBN for i in isbns}
        spbook = [r for r in spbook if r.ISBN in valid_isbns]
    
    conn.close()
    return spbook

def fetch_splibrary(isbn, zipcode):
    conn = db.connect()
    q = f"SELECT *, ABS(Zipcode - {zipcode}) as zd FROM Library NATURAL JOIN LibraryBook WHERE ISBN LIKE '{isbn}' ORDER BY zd ASC" 
    splibrary = conn.execute(q)
    conn.close()
    return [r for r in splibrary]

def advanced_query_top_books():
    conn = db.connect()
    q = """
        (
            SELECT Title, YEAR(Date) AS Year
            FROM Review NATURAL JOIN Book
            WHERE StarRating=5 AND YEAR(Date)=2021
            GROUP BY ISBN, YEAR(Date)
            ORDER BY COUNT( * ) DESC LIMIT 10
        )
        UNION ALL
        (
            SELECT Title, YEAR(Date) AS Year
            FROM Review NATURAL JOIN Book
            WHERE StarRating=5 AND YEAR(Date)=2020
            GROUP BY ISBN, YEAR(Date)
            ORDER BY COUNT( * ) DESC LIMIT 10
        );
    """
    res = conn.execute(q)
    return [r for r in res]

def advanced_query_top_users():
    conn = db.connect()
    q = """
    (
        SELECT Name, YEAR(Date) AS Year, Count(*) NumReviews
        FROM Review NATURAL JOIN User
        WHERE YEAR(Date)=2021
        GROUP BY Review.UserID, YEAR(Date)
        ORDER BY NumReviews DESC LIMIT 10
    )
    UNION ALL
    (
        SELECT Name, YEAR(Date) AS Year, Count(*) NumReviews
        FROM Review NATURAL JOIN User
        WHERE YEAR(Date)=2020
        GROUP BY Review.UserID, YEAR(Date)
        ORDER BY NumReviews DESC LIMIT 10
    );
    """
    res = conn.execute(q)
    return [r for r in res]

