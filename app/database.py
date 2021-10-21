from app import db

def test():
    with db.begin() as conn:
        res = conn.execute("Select * from User;").fetchmany(5);
        print(res)
    return res

def search(keyword, table)