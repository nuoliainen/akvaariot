import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM aquariums")
db.execute("DELETE FROM critters")
db.execute("DELETE FROM aquarium_classes")
db.execute("DELETE FROM comments")

user_count = 1000
aquarium_count = 10**5
comment_count = 10**6
critter_count = 10**6

# Add users
for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)])

# Add aquariums
for i in range(1, aquarium_count + 1):
    user_id = random.randint(1, user_count)
    db.execute("""INSERT INTO aquariums (name, user_id, length, depth, height, volume)
                  VALUES (?, ?, 130, 50, 50, 325)""",
               ["tank" + str(i), user_id])

# Add critters
for i in range(1, critter_count + 1):
    aquarium_id = random.randint(1, aquarium_count)
    user_id = db.execute("SELECT user_id FROM aquariums WHERE id = ?",
                         [aquarium_id]).fetchone()[0]
    count = random.randint(1, 30)
    db.execute("INSERT INTO critters (species, count, aquarium_id, user_id) VALUES (?, ?, ?, ?)",
               ["fish" + str(i), count, aquarium_id, user_id])

# Add comments
for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    aquarium_id = random.randint(1, aquarium_count)
    db.execute("""INSERT INTO comments (aquarium_id, user_id, content, sent_at)
                  VALUES (?, ?, ?, datetime('now'))""",
               [aquarium_id, user_id, "message" + str(i)])

db.commit()
db.close()
