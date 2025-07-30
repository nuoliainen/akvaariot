import db

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