from app import db

current_user_id = None

def set_current_user_id(new_id):
    global current_user_id
    current_user_id = new_id

def get_current_user_id():
    global current_user_id
    return current_user_id

def get_current_user():
    user_id = get_current_user_id()
    with db.begin() as conn:
        user = conn.execute(f"SELECT * FROM User WHERE UserID={user_id}").fetchone()
    return user