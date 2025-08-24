from flask import g
import db
import helpers as h

def count_aquariums():
    """Gets the number of all aquariums in the database."""
    sql = "SELECT COUNT(*) FROM aquariums"
    return db.query(sql)[0][0]

def get_aquariums_page(page, page_size):
    """Gets the details of all aquariums in a page."""
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
             GROUP BY a.id
             ORDER BY a.id DESC
             LIMIT ? OFFSET ?"""
    limit = page_size
    offset = page_size * (page - 1)

    aquariums = db.query(sql, [limit, offset])
    aquariums_dicts = [dict(row) for row in aquariums]

    # Calculate age for each aquarium
    for aquarium in aquariums_dicts:
        years, days = h.date_difference(aquarium["date"])
        aquarium["age_years"] = years
        aquarium["age_days"] = days

    return aquariums_dicts

def get_aquarium(aquarium_id):
    """Gets the details of an aquarium from the database."""
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
    aquarium = db.query(sql, [aquarium_id])

    if not aquarium:
        return None
    aquarium_dict = dict(aquarium[0])

    years, days = h.date_difference(aquarium_dict["date"])
    aquarium_dict["age_years"] = years
    aquarium_dict["age_days"] = days

    return aquarium_dict

def update_aquarium(name, dims, volume, date, description, aquarium_id, classes):
    """Updates the information of an aquarium into the database."""
    sql_commands = []
    sql = """UPDATE aquariums
             SET name = ?,
                 length = ?,
                 depth = ?,
                 height = ?,
                 volume = ?,
                 date = ?,
                 description = ?
             WHERE id = ?"""
    params = [name, dims[0], dims[1], dims[2], volume, date, description, aquarium_id]
    sql_commands.append((sql, params))

    # Delete old classes
    sql = "DELETE FROM aquarium_classes WHERE aquarium_id = ?"
    params = [aquarium_id]
    sql_commands.append((sql, params))

    # Insert new classes
    sql = """INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)"""
    for title, value in classes:
        sql_commands.append((sql, [aquarium_id, title, value]))

    db.execute_multiple(sql_commands)

def remove_aquarium(aquarium_id):
    """Removes a specific aquarium from the database."""
    sql = "DELETE FROM aquariums WHERE id = ?"
    db.execute(sql, [aquarium_id])

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

def get_selected_classes(aquarium_id):
    """Gets all class titles and values of a specific aquarium that are currently selected."""
    sql = "SELECT title, value FROM aquarium_classes WHERE aquarium_id = ?"
    return db.query(sql, [aquarium_id])

def add_aquarium(user_id, name, dims, volume, date, description, classes):
    """Adds a new aquarium into the database."""
    con = db.get_connection()
    try:
        sql = """INSERT INTO aquariums (user_id, name, length, depth, height, volume, date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        result = con.execute(sql, [user_id, name, dims[0], dims[1], dims[2], volume, date, description])
        aquarium_id = result.lastrowid

        sql = "INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)"
        for title, value in classes:
            con.execute(sql, [aquarium_id, title, value])

        con.commit()
        return aquarium_id
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def add_critter(user_id, aquarium_id, species, count):
    """Adds a new animal into the aquarium."""
    sql = """INSERT INTO critters (user_id, aquarium_id, species, count)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [user_id, aquarium_id, species, count])

def get_critters(aquarium_id):
    """Gets all the critters within an aquarium."""
    sql = """SELECT id, species, count
             FROM critters
             WHERE aquarium_id = ?
             ORDER BY species"""
    return db.query(sql, [aquarium_id])

def get_critter(critter_id):
    """Gets the details of a specific critter."""
    sql = """SELECT id, species, count, aquarium_id, user_id
             FROM critters
             WHERE id = ?"""
    result = db.query(sql, [critter_id])
    return result[0] if result else None

def update_critter(species, count, aquarium_id, critter_id):
    """Updates the information of a critter into the database."""
    sql = """UPDATE critters
             SET species = ?,
                 count = ?,
                 aquarium_id = ?
             WHERE id = ?"""
    db.execute(sql, [species, count, aquarium_id, critter_id])

def remove_critter(critter_id):
    """Detele a critter from the database."""
    sql = "DELETE FROM critters WHERE id = ?"
    db.execute(sql, [critter_id])

def remove_critters(aquarium_id):
    """Detele all critters from the aquarium."""
    sql = "DELETE FROM critters WHERE aquarium_id = ?"
    db.execute(sql, [aquarium_id])

def add_comment(aquarium_id, user_id, content):
    """Adds a new comment into the database."""
    sql = """INSERT INTO comments (aquarium_id, user_id, content, sent_at)
             VALUES (?, ?, ?, datetime('now', 'localtime'))"""
    db.execute(sql, [aquarium_id, user_id, content])

def get_newest_comments(aquarium_id, limit):
    """Gets the newest comments related to a specific aquarium."""
    sql = """SELECT comments.id,
                    comments.content,
                    comments.sent_at,
                    users.id AS user_id,
                    users.username
             FROM comments
             JOIN users ON comments.user_id = users.id
             WHERE comments.aquarium_id = ?
             ORDER BY comments.id DESC LIMIT ?"""
    return db.query(sql, [aquarium_id, limit])

def count_comments(aquarium_id):
    """Gets the number of comments for a specific aquarium."""
    sql = "SELECT COUNT(*) FROM comments WHERE aquarium_id = ?"
    return db.query(sql, [aquarium_id])[0][0]

def get_comments_page(aquarium_id, page, page_size):
    """Gets all comments related to a specific aquarium in a page."""
    limit = page_size
    offset = page_size * (page - 1)
    sql = """SELECT comments.id,
                    comments.content,
                    comments.sent_at,
                    users.id AS user_id,
                    users.username
             FROM comments
             JOIN users ON comments.user_id = users.id
             WHERE comments.aquarium_id = ?
             ORDER BY comments.id DESC LIMIT ? OFFSET ?"""
    return db.query(sql, [aquarium_id, limit, offset])

def get_comment(comment_id):
    """Gets the details of a specific comment."""
    sql = """SELECT id, content, sent_at, aquarium_id, user_id
             FROM comments
             WHERE id = ?"""
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def remove_comment(comment_id):
    """Removes a comment from the database."""
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])

def add_image(aquarium_id, image, file_type):
    """Adds an image into the database."""
    sql = "INSERT INTO images (aquarium_id, image, file_type) VALUES (?, ?, ?)"
    db.execute(sql, [aquarium_id, image, file_type])

def count_images(aquarium_id):
    """Counts how many images an aquarium currently has."""
    sql = "SELECT COUNT(id) FROM images WHERE aquarium_id = ?"
    return db.query(sql, [aquarium_id])[0][0]

def get_image_ids(aquarium_id):
    """Gets a list of all id's of an aquarium."""
    sql = "SELECT id FROM images WHERE aquarium_id = ?"
    results = db.query(sql, [aquarium_id])
    return [row["id"] for row in results]

def get_image_data(image_id):
    """Gets the data of an image."""
    sql = "SELECT image, file_type FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    if result:
        row = result[0]
        return row["image"], row["file_type"]
    return None, None

def get_image(image_id):
    """Gets the id and aquarium id of an image."""
    sql = "SELECT id, aquarium_id FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0] if result else None

def remove_images(image_ids, aquarium_id):
    """Removes one or multiple images from the database."""
    if not image_ids:
        return

    placeholders = ",".join("?" for _ in image_ids)
    sql = f"DELETE FROM images WHERE id IN ({placeholders}) AND aquarium_id = ?"
    db.execute(sql, image_ids + [aquarium_id])

def remove_all_images(aquarium_id):
    """Removes all images of an aquarium."""
    sql = "DELETE FROM images WHERE aquarium_id = ?"
    db.execute(sql, [aquarium_id])

def set_main_image(aquarium_id, image_id):
    """Sets the chosen image as the main image.
    Updates the main image if the aquarium already has one.
    """
    sql = """INSERT INTO main_images (aquarium_id, image_id)
             VALUES(?, ?)
             ON CONFLICT(aquarium_id) DO UPDATE SET image_id=excluded.image_id"""
    db.execute(sql, [aquarium_id, image_id])

def get_main_image(aquarium_id):
    """Gets the main image of an aquarium."""
    sql = """SELECT image_id
             FROM main_images
             WHERE aquarium_id = ?"""
    result = db.query(sql, [aquarium_id])
    return result[0][0] if result else None

def remove_main_image(aquarium_id):
    """Removes the main image of an aquarium."""
    sql = "DELETE FROM main_images WHERE aquarium_id = ?"
    db.execute(sql, [aquarium_id])

def get_oldest_image(aquarium_id):
    sql = """SELECT id FROM images
             WHERE aquarium_id = ?
             ORDER BY id
             LIMIT 1"""
    result = db.query(sql, [aquarium_id])
    return result[0][0] if result else None

def create_filter_sql(filters):
    """Creates SQL filter clause and parameters from given filters."""
    sql_parts = []
    params = []

    query = filters.get("query")
    if query:
        sql_parts.append(""" AND (a.name LIKE ? OR
                             a.description LIKE ? OR
                             u.username LIKE ?)""")
        params.extend(["%" + query + "%"] * 3)

    species_query = filters.get("species_query")
    if species_query:
        sql_parts.append(""" AND EXISTS (SELECT 1
                                        FROM critters c
                                        WHERE c.aquarium_id = a.id
                                        AND c.species LIKE ?)""")
        params.append("%" + species_query + "%")

    if filters.get("volume_min"):
        sql_parts.append(" AND a.volume >= ?")
        params.append(filters["volume_min"])
    if filters.get("volume_max"):
        sql_parts.append(" AND a.volume <= ?")
        params.append(filters["volume_max"])

    if filters.get("date_min"):
        sql_parts.append(" AND date(a.date) >= date(?)")
        params.append(filters["date_min"])
    if filters.get("date_max"):
        sql_parts.append(" AND date(a.date) <= date(?)")
        params.append(filters["date_max"])

    # Class filters
    for key, value in filters.items():
        if key.startswith("class_") and value:
            # Get the class title (the part that comes after "class_")
            class_title = key[len("class_"):]
            sql_parts.append(""" AND EXISTS (SELECT 1
                                            FROM aquarium_classes ac
                                            WHERE ac.aquarium_id = a.id
                                            AND ac.title = ?
                                            AND ac.value = ?)""")
            params.extend([class_title, value])

    if sql_parts:
        sql = "".join(sql_parts)
        return sql, params
    return "", params

def count_search_results(filters):
    """Gets the number of aquariums that match the filter conditions."""
    sql = """SELECT COUNT(*)
             FROM aquariums a
             JOIN users u ON a.user_id = u.id
             WHERE 1=1"""

    filter_sql, params = create_filter_sql(filters)
    sql += filter_sql

    return db.query(sql, params)[0][0]

def search_page(filters, page, page_size):
    """Selects all aquariums that match the filter conditions."""
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
             WHERE 1=1"""

    filter_sql, params = create_filter_sql(filters)
    sql += filter_sql

    sql += " GROUP BY a.id ORDER BY a.id DESC LIMIT ? OFFSET ?"
    limit = page_size
    offset = page_size * (page - 1)
    params.extend([limit, offset])

    aquariums = db.query(sql, params)
    aquariums_dicts = [dict(row) for row in aquariums]

    # Calculate age for each aquarium
    for aquarium in aquariums_dicts:
        years, days = h.date_difference(aquarium["date"])
        aquarium["age_years"] = years
        aquarium["age_days"] = days

    return aquariums_dicts
