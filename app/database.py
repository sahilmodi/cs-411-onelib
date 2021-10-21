from app import db

def test():
    db.connect()
    res = db.execute("Select * from User;").fetchmany(5);
    print(res)
    return res