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
    sql = """SELECT a.id,
                    a.name,
                    a.length,
                    a.depth,
                    a.height,
                    a.volume,
                    a.date,
                    u.id AS user_id,
                    u.username,
                    m.image_id as main_image_id
             FROM aquariums a
             JOIN users u ON a.user_id = u.id
             LEFT JOIN main_images m ON a.id = m.aquarium_id
             WHERE a.user_id = ?
             ORDER BY a.id DESC
             """
    return db.query(sql, [user_id])

def get_aquariums_page(user_id, page, page_size):
    """Gets the details of all aquariums in a page that belong to the user."""
    sql = """SELECT a.id,
                    a.name,
                    a.length,
                    a.depth,
                    a.height,
                    a.volume,
                    a.date,
                    u.id AS user_id,
                    u.username,
                    m.image_id as main_image_id,
                    GROUP_CONCAT(ac.title || ': ' || ac.value, ', ') AS selected_classes,
                    (SELECT COUNT(*) FROM comments c WHERE c.aquarium_id = a.id) AS comment_count,
                    (SELECT COUNT(DISTINCT species) FROM critters cr WHERE cr.aquarium_id = a.id) AS species_count,
                    (SELECT COALESCE(SUM(count), 0) FROM critters cr WHERE cr.aquarium_id = a.id) AS total_individuals
             FROM aquariums a
             JOIN users u ON a.user_id = u.id
             LEFT JOIN main_images m ON a.id = m.aquarium_id
             LEFT JOIN aquarium_classes ac ON a.id = ac.aquarium_id
             WHERE a.user_id = ?
             GROUP BY a.id
             ORDER BY a.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [user_id, limit, offset])

def count_aquariums(user_id):
    """Counts the number and total volume of aquariums user has."""
    sql = """SELECT COUNT(*), SUM(volume)
             FROM aquariums
             WHERE user_id = ?"""
    result = db.query(sql, [user_id])
    if result:
        species_count, critter_count = result[0]
        return {
            "count": species_count,
            "volume": critter_count
        }
    return {"count": 0, "volume": 0}

def count_critters(user_id):
    """Counts the number of species and individuals that belong to a user."""
    sql = """SELECT COUNT(DISTINCT species), SUM(count)
             FROM critters
             WHERE user_id = ?"""
    result = db.query(sql, [user_id])
    if result:
        species_count, critter_count = result[0]
        return {
            "species": species_count,
            "individuals": critter_count
        }
    return {"species": 0, "individuals": 0}
