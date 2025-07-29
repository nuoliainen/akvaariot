import db

def get_user(user_id):
    """Gets an aquarium grom the database based on aquarium id."""
    sql = """SELECT id, username
             FROM users
             WHERE id = ?"""
    result = db.query(sql, [user_id])
    return result[0] if result else None