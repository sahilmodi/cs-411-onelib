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

def delete_review(user_id, isbn):
    conn = db.connect()
    q = f"DELETE FROM Review WHERE UserID = {user_id} AND ISBN LIKE '{isbn}'"
    conn.execute(q)
    conn.close()
    return True
