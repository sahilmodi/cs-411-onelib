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

def get_borrowed_books(user_id=None, amount=10):
    query = "SELECT User.Name UserName, UserID, DueDate, ImageURL, Library.Name LibraryName, Title, Author, ISBN, LibraryID FROM BorrowedBook NATURAL JOIN Book NATURAL JOIN User JOIN Library USING (LibraryID)"
    if user_id is not None:
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
    due_date = datetime.datetime.today().date() + datetime.timedelta(days=time_limit_days)
    q = f"Insert INTO BorrowedBook VALUES ({user_id}, {library_id}, '{isbn}', '{due_date}')"
    print(q)
    conn.execute(q)
    conn.execute(f"UPDATE LibraryBook SET Quantity = Quantity-1 WHERE LibraryID={library_id} AND ISBN LIKE '{isbn}'")
    conn.close()
    return True

def return_book(user_id, library_id, isbn):
    conn = db.connect()
    conn.execute(f"DELETE FROM BorrowedBook WHERE UserID={user_id} AND LibraryID={library_id} AND ISBN LIKE '{isbn}'")
    conn.execute(f"UPDATE LibraryBook SET Quantity = Quantity+1 WHERE LibraryID={library_id} AND ISBN LIKE '{isbn}'")
    conn.close()
    return True


def read_from_table(table, amount=5):
    assert table in tables
    with db.begin() as conn:
        res = conn.execute(f"SELECT * FROM {table}").fetchmany(amount)
    return [r for r in res]

def fetch_allreview() ->dict:
    conn = db.connect()
    query='SELECT * FROM Review where ISBN LIKE "842332251";'
    query_results = conn.execute(query).fetchall()
    conn.close()
    allreview = []
    for result in query_results:
        item = {
            "ISBN": result[0],
            "UserID": result[1],
            "Date": result[2],
            "StarRating": result[3],
            "Text": result[4]
        }
        allreview.append(item)
    return allreview

def fetch_bookreview(isbn) ->dict:
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

def fetch_spbook(input_text):
    conn = db.connect()
    #print(input_text)
    q = f"SELECT * FROM Book WHERE Title LIKE '%%{input_text}%%'"  # cuz python will interpret % as a printf-like format character
    spbook = conn.execute(q)
    # print(spbook)
    conn.close()
    return [r for r in spbook]

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

