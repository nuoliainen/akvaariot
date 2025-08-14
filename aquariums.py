import db

def aquarium_count():
    sql = "SELECT COUNT(*) FROM aquariums"
    return db.query(sql)[0][0]

def get_all_classes():
    """Gets all titles and possible values of classes from the database as a dictionary."""
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        if title not in classes:
            classes[title] = []
        classes[title].append(value)

    return classes

def get_aquarium_classes(aquarium_id):
    """Gets all classes of a specific aquarium."""
    sql = "SELECT title, value FROM aquarium_classes WHERE aquarium_id = ?"
    return db.query(sql, [aquarium_id])

def add_aquarium(user_id, name, dims, volume, date, description, classes):
    """Adds a new aquarium into the database."""
    sql = """INSERT INTO aquariums (user_id, name, length, depth, height, volume, date, description)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, name, dims[0], dims[1], dims[2], volume, date, description])

    aquarium_id = db.last_insert_id()
    sql = "INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [aquarium_id, title, value])

def get_aquariums():
    """Gets the details of all aquariums from the database."""
    sql = "SELECT id, name, volume FROM aquariums ORDER BY id DESC"
    return db.query(sql)

def get_aquariums_page(page, page_size):
    """Gets the details of all aquariums in a page."""
    sql = "SELECT id, name, volume FROM aquariums ORDER BY id DESC LIMIT ? OFFSET ?"
    limit = page_size
    offset = page_size * (page - 1)
    return db.query(sql, [limit, offset])

def get_aquarium(aquarium_id):
    """Gets the details of an aquarium from the database based on aquarium id."""
    sql = """SELECT a.id,
                    a.name,
                    a.length,
                    a.depth,
                    a.height,
                    a.volume,
                    a.date,
                    a.description,
                    u.username,
                    u.id user_id
             FROM aquariums a, users u
             WHERE a.user_id = u.id AND a.id = ?"""
    result = db.query(sql, [aquarium_id])
    return result[0] if result else None

def update_aquarium(name, dims, volume, date, description, aquarium_id, classes):
    """Updates the information of an aquarium into the database."""
    sql = """UPDATE aquariums SET name = ?,
                                  length = ?,
                                  depth = ?,
                                  height = ?,
                                  volume = ?,
                                  date = ?,
                                  description = ?
                              WHERE id = ?"""
    db.execute(sql, [name, dims[0], dims[1], dims[2], volume, date, description, aquarium_id])

    sql = "DELETE FROM aquarium_classes WHERE aquarium_id = ?"
    db.execute(sql, [aquarium_id])
    sql = "INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [aquarium_id, title, value])

def remove_aquarium(aquarium_id):
    """Removes a specific aquarium from the database based on aquarium id."""
    sql = "DELETE FROM aquarium_classes WHERE aquarium_id = ?"
    db.execute(sql, [aquarium_id])
    sql = "DELETE FROM aquariums WHERE id = ?"
    db.execute(sql, [aquarium_id])

def add_critter(user_id, aquarium_id, species, count):
    """Adds a new animal into the aquarium."""
    sql = """INSERT INTO critters (user_id, aquarium_id, species, count)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [user_id, aquarium_id, species, count])

def get_critters(critter_id):
    """Gets the critters within an aquarium."""
    sql = """SELECT id, species, count
             FROM critters
             WHERE aquarium_id = ?
             ORDER BY species;"""
    return db.query(sql, [critter_id])

def get_critter(critter_id):
    """Gets a specific critter."""
    sql = """SELECT id, species, count, aquarium_id, user_id
             FROM critters
             WHERE id = ?"""
    result = db.query(sql, [critter_id])
    return result[0] if result else None

def remove_critter(critter_id):
    """Detele a critter from the database."""
    sql = "DELETE FROM critters WHERE id = ?"
    db.execute(sql, [critter_id])

def search(query):
    """Selects all aquariums that contain a keyword in any column."""
    sql = """SELECT a.id,
                    a.name,
                    a.volume
             FROM aquariums a
             JOIN users u ON a.user_id = u.id
             WHERE a.name LIKE ? OR
                   a.length LIKE ? OR
                   a.depth LIKE ? OR
                   a.height LIKE ? OR
                   a.volume LIKE ? OR
                   a.date LIKE ? OR
                   a.description LIKE ? OR
                   u.username LIKE ?
             ORDER BY a.id DESC"""
    return db.query(sql, ["%" + query + "%"]*8)

def add_comment(aquarium_id, user_id, content):
    """Adds a new comment into the database."""
    sql = """INSERT INTO comments (aquarium_id, user_id, content, sent_at)
             VALUES (?, ?, ?, datetime('now'))"""
    db.execute(sql, [aquarium_id, user_id, content])

def get_comments(aquarium_id):
    """Gets all comments related to a specific aquarium."""
    sql = """SELECT comments.id,
                    comments.content,
                    comments.sent_at,
                    users.id AS user_id,
                    users.username
             FROM comments
             JOIN users ON comments.user_id = users.id
             WHERE comments.aquarium_id = ?
             ORDER BY comments.id DESC;"""
    return db.query(sql, [aquarium_id])

def get_comment(comment_id):
    """Gets a specific comment."""
    sql = """SELECT id, content, sent_at, aquarium_id, user_id
             FROM comments
             WHERE id = ?"""
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def remove_comment(comment_id):
    """Deletes a comment from the database."""
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])

def add_image(aquarium_id, image):
    sql = "INSERT INTO images (aquarium_id, image) VALUES (?, ?)"
    db.execute(sql, [aquarium_id, image])

def get_images(aquarium_id):
    sql = "SELECT id FROM images WHERE aquarium_id = ?"
    return db.query(sql, [aquarium_id])

def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return  result[0][0] if result else None

def remove_image(image_id, aquarium_id):
    sql = "DELETE FROM images WHERE id = ? AND aquarium_id = ?"
    db.execute(sql, [image_id, aquarium_id])