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

def add_borrowed_book(user_id, library_id, isbn):
    conn = db.connect()
    conn.execute("TRUNCATE BorrowedBook")
    res = conn.execute(f"SELECT Quantity, TimeLimitDays FROM LibraryBook WHERE LibraryID={library_id} AND ISBN LIKE '{isbn}'").fetchone()
    if res is None:
        return False
    quantity, time_limit_days = res
    if quantity == 0:
        return False
    quantity -= 1
    due_date = datetime.datetime.today().date() + datetime.timedelta(days=time_limit_days)
    q = f"Insert INTO BorrowedBook VALUES ({user_id}, {library_id}, '{isbn}', '{due_date}')"
    print(q)
    conn.execute(q)
    conn.close()
    return True

def read_from_table(table, amount=5):
    assert table in tables
    with db.begin() as conn:
        res = conn.execute(f"SELECT * FROM {table}").fetchmany(amount)
    return res


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