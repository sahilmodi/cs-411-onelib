from app import db

current_user_id = None
current_user = None

def set_current_user_id(new_id):
    global current_user_id, current_user
    current_user_id = new_id
    if new_id is not None:
        with db.begin() as conn:
            current_user = conn.execute(f"SELECT * FROM User WHERE UserID={new_id}").fetchone()
    else:
        current_user = None

def get_current_user_id():
    global current_user_id
    return current_user_id

def get_current_user():
    global current_user
    return current_user

def login(email, password):
    with db.begin() as conn:
        users = conn.execute("""SELECT * FROM User WHERE email LIKE '{}' AND password LIKE '{}'""".format(email,password))
    users = [u for u in users]
    if users is None:
        return None
    if len(users) != 1:
        return None
    user = users[0]
    set_current_user_id(user.UserID)
    return user

def logout():
    set_current_user_id(None)

def create_user(name, age, zipcode, payment_number, password, email):
    with db.begin() as conn:
        id = int(conn.execute('SELECT MAX(UserID) uid from User').fetchone().uid) + 1
        age_str = f"'{age}'"
        if not age:
            age_str = "NULL"
        q = f"INSERT INTO User VALUES ({id}, '{name}', {age_str}, '{zipcode}', '{payment_number}', '{password}', '{email}')"
        conn.execute(q)
