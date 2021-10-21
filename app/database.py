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