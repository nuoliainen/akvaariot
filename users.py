from werkzeug.security import generate_password_hash, check_password_hash
import db

def create_user(username, password):
    """Creates a new user into the database."""
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    """Authenticate user by verifying their username and password.
    Returns the user id if login is successful."""
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    # If username does not exist
    if not result:
        return None

    result = result[0]
    user_id = result["id"]
    password_hash = result["password_hash"]

    if check_password_hash(password_hash, password):
        return user_id
    # If the password is incorrect
    return None

def get_user(user_id):
    """Gets user details from the database based on user id."""
    sql = """SELECT id, username
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_aquariums(user_id):
    """Gets the details of all aquariums from the database that belong to the user."""
    sql = """SELECT id, name, volume
             FROM aquariums
             WHERE user_id = ?
             ORDER BY id DESC"""
    return db.query(sql, [user_id])
