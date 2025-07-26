import db

def add_aquarium(user_id, name, l, d, h, volume, description):
    sql = "INSERT INTO aquariums (user_id, name, length, depth, height, volume, description) VALUES (?, ?, ?, ?, ?, ?, ?)"
    db.execute(sql, [user_id, name, l, d, h, volume, description])

def get_aquariums():
    sql = "SELECT id, name, volume FROM aquariums ORDER BY id DESC"
    return db.query(sql)

def get_aquarium(aquarium_id):
    sql = """SELECT a.name, a.volume, a.length, a.depth, a.height, a.description, u.username 
             FROM aquariums a, users u
             WHERE a.user_id = u.id AND a.id = ?"""
    return db.query(sql, [aquarium_id])[0]