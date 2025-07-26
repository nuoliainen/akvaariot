import db

def add_aquarium(user_id, name, l, d, h, volume, description):
    sql = "INSERT INTO aquariums (user_id, name, length, depth, height, volume, description) VALUES (?, ?, ?, ?, ?, ?, ?)"
    db.execute(sql, [user_id, name, l, d, h, volume, description])