from werkzeug.security import generate_password_hash, check_password_hash
import db

def create_user(username, password):
    """Creates a new user into the database."""
    # Hash the password for security
    password_hash = generate_password_hash(password)
    # Insert the new user into the database
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    # Get the user's hashed password from the database
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    # Check if the username exists in the database
    if not result:
        return None

    # Extract user ID and password hash from the query result
    result = result[0]
    user_id = result["id"]
    password_hash = result["password_hash"]

    # Verify the provided password against the stored hash
    if check_password_hash(password_hash, password):
        return user_id
    # Return none if the password is incorrect
    return None

def get_user(user_id):
    """Gets a user from the database based on user id."""
    sql = """SELECT id, username
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_aquariums(user_id):
    """Gets all aquariums from the database that belong to the user."""
    sql = """SELECT id, name, volume
             FROM aquariums
             WHERE user_id = ?
             ORDER BY id DESC"""
    return db.query(sql, [user_id])
