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
    query='SELECT * FROM Review LIMIT 200;'
    query_results = conn.execute(query).fetchall()
    conn.close()
    allreview = []
    for result in query_results:
        item = {
            "ISBN": result[0],
            "UserID": result[1],
            "Date": result[2],
            "StarTating": result[3],
            "Text": result[4]
        }
        allreview.append(item)
    return allreview

def remove_review(isbn,user_id) -> None:
    """ remove entries based on ISBN and UserId """
    conn = db.connect()
    query = 'Delete From Review where ISBN={} and UserID={};'.format(isbn,user_id)
    conn.execute(query)
    conn.close()


def fetch_TopBook() -> dict:
    """
    Return the Top 10 books that have the most number of 5 stars reviews in recent 2 years.

    Returns:
        A list of dictionaries
    """

    conn = db.connect()
    query='(SELECT Title, YEAR(Date) AS Year \
            FROM Review NATURAL JOIN Book \
            WHERE StarRating=5 AND YEAR(Date)=2021 \
            GROUP BY ISBN, YEAR(Date) \
            ORDER BY COUNT( * ) DESC LIMIT 10) \
            UNION ALL \
            (SELECT Title, YEAR(Date) AS Year \
            FROM Review NATURAL JOIN Book \
            WHERE StarRating=5 AND YEAR(Date)=2020 \
            GROUP BY ISBN, YEAR(Date) \
            ORDER BY COUNT( * ) DESC LIMIT 10);'
    query_results = conn.execute(query).fetchall()
    conn.close()
    TopBook = []
    for result in query_results:
        item = {
            "Title": result[0],
            "Year": result[1]
        }
        TopBook.append(item)
    return TopBook

def fetch_TopUser() -> dict:
    """
    Return the Top 10 Users who have the most number of reviews in recent 2 years.

    Returns:
        A list of dictionaries
    """

    conn = db.connect()
    query='(SELECT Name, YEAR(Date)\
            FROM Review NATURAL JOIN User \
            WHERE YEAR(Date)=2021 \
            GROUP BY Review.UserID, YEAR(Date) \
            ORDER BY COUNT(*) DESC LIMIT 10) \
            UNION ALL \
            (SELECT Name, YEAR(Date) \
            FROM Review NATURAL JOIN User \
            WHERE YEAR(Date)=2020 \
            GROUP BY Review.UserID, YEAR(Date) \
            ORDER BY COUNT(*) DESC LIMIT 10);'
    query_results = conn.execute(query).fetchall()
    conn.close()
    TopUser = []
    for result in query_results:
        item = {
            "Name": result[0],
            "Year": result[1]
        }
        TopUser.append(item)
    return TopUser

def update_rent_librarybook(LibraryID: int, ISBN: str) -> None:
    """
    Update the Quantity after user rent a book

    """
    conn = db.connect()
    Quantity = conn.execute('Select Quantity from LibraryBook where LibraryID = {} and ISBN="{}";'.format(LibraryID,ISBN))
    BookQuantity=int(Quantity)
    query = 'Update LibraryBook set Quantity = {} where LibraryID = {} and ISBN="{}";'.format(BookQuantity-1, LibraryID, ISBN)
    conn.execute(query)
    conn.close()

def update_return_librarybook(LibraryID: int, ISBN: str) -> None:
    """
    Update the Quantity after user return a book

    """
    conn = db.connect()
    Quantity = conn.execute('Select Quantity from LibraryBook where LibraryID = {} and ISBN="{}";'.format(LibraryID,ISBN))
    BookQuantity=int(Quantity)
    query = 'Update LibraryBook set Quantity = {} where LibraryID = {} and ISBN="{}";'.format(BookQuantity+1, LibraryID, ISBN)
    conn.execute(query)
    conn.close()
