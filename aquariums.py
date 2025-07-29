import db

def add_aquarium(user_id, name, dims, volume, description):
    """Adds a new aquarium into the database."""
    sql = """INSERT INTO aquariums (user_id, name, length, depth, height, volume, description)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, name, dims[0], dims[1], dims[2], volume, description])

def get_aquariums():
    """Gets all aquariums from the database."""
    sql = "SELECT id, name, volume FROM aquariums ORDER BY id DESC"
    return db.query(sql)

def get_aquarium(aquarium_id):
    """Gets an aquarium from the database based on aquarium id."""
    sql = """SELECT a.id,
                    a.name,
                    a.length,
                    a.depth,
                    a.height,
                    a.volume,
                    a.description,
                    u.username,
                    u.id user_id
             FROM aquariums a, users u
             WHERE a.user_id = u.id AND a.id = ?"""
    result = db.query(sql, [aquarium_id])
    return result[0] if result else None

def update_aquarium(name, dims, volume, description, aquarium_id):
    """Updates the information of an aquarium into the database."""
    sql = """UPDATE aquariums SET name = ?,
                                  length = ?,
                                  depth = ?,
                                  height = ?,
                                  volume = ?,
                                  description = ?
                              WHERE id = ?"""
    return db.execute(sql, [name, dims[0], dims[1], dims[2], volume, description, aquarium_id])

def remove_aquarium(aquarium_id):
    """Removes a specific aquarium from the database."""
    sql = "DELETE FROM aquariums WHERE id = ?"
    return db.execute(sql, [aquarium_id])

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
                   a.description LIKE ? OR
                   u.username LIKE ?
             ORDER BY a.id DESC"""
    return db.query(sql, ["%" + query + "%"]*7)
