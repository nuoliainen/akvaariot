import random
import datetime
import sqlite3
import time

user_count = 1000
aquarium_count = 10**6
comment_count = 10**7
critter_count = 10**6
batch_size = 100000

animals = [
    "Neontetra",
    "Miljoonakala",
    "Platy",
    "Kultakala",
    "Tiikerinuoliainen",
    "Seeprakala",
    "Rasbora",
    "Kardinaalitetra",
    "Piikkisilmä",
    "Tummapiikkislmä",
    "Lehtikala",
    "Taistelukala",
    "Käärmekala",
    "Juovaokamonni",
    "Leväbarbi",
    "Partamonni",
    "Keltabarbi",
    "Kiekkokala",
    "Helmirihmakala",
    "Sinikirjoahven",
    "Mustaveitsikala",
    "Perhostoka",
    "Sateenkaarikala",
    "Oto",
    "Severum",
    "Kääpiökynsisammakko",
    "Nauhanuoliainen",
    "Kiekkokotilo",
    "Sukarapu",
    "Haarniskamonni"
]

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM aquariums")
db.execute("DELETE FROM critters")
db.execute("DELETE FROM aquarium_classes")
db.execute("DELETE FROM comments")
db.execute("DELETE FROM images")
db.execute("DELETE FROM main_images")

# Add users
start = time.time()
db.executemany("INSERT INTO users (username) VALUES (?)",
                [("user" + str(i),) for i in range(1, user_count + 1)])
print("users done in", time.time() - start, "seconds")

# Add aquariums
start = time.time()
aquarium_data = []
class_data = []

start_date = datetime.date(2010, 8, 20)
end_date = datetime.date(2025, 8, 20)
num_days   = (end_date - start_date).days

for i in range(1, aquarium_count + 1):
    user_id = random.randint(1, user_count)

    l = random.randrange(20, 301, 5)
    d = random.randrange(20, 101, 5)
    h = random.randrange(20, 101, 5)
    volume = l*d*h // 1000

    random_date = start_date + datetime.timedelta(days=random.randint(1, num_days))
    random_date_str = random_date.isoformat()
    desc = "description " * random.randint(1, 100)

    aquarium_data.append((f"tank{i}", user_id, l, d, h, volume, random_date_str, desc))

    # Assign some classes
    if random.random() < 0.95:
        class_data.append((i, "Vesi", random.choices(["makea vesi", "murtovesi", "merivesi"], weights=(10, 1, 5))[0]))
    if random.random() < 0.9:
        class_data.append((i, "Lämpötila", random.choices(["trooppinen", "lauhkea", "kylmä"], weights=(10, 3, 1))[0]))
    if random.random() < 0.6:
        class_data.append((i, "Tyyppi", random.choices(["vain kaloja", "vain selkärangattomia", "lajiakvaario",
                                                        "riutta-akvaario", "kasviakvaario", "biotooppi", "aquascape"],
                                                        weights=(2, 0.5, 1, 5, 15, 2, 3))[0]))
    if random.random() < 0.5:
        class_data.append((i, "Tekniikka", random.choices(["high tech", "low tech"], weights=(1, 3))[0]))

    # Insert in batches
    if len(aquarium_data) >= batch_size:
        db.executemany("""INSERT INTO aquariums (name, user_id, length, depth, height, volume, date, description)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", aquarium_data)
        aquarium_data.clear()  # Clear the list after insertion
    if len(class_data) >= batch_size:
        db.executemany("INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)", class_data)
        class_data.clear()  # Clear the list after insertion

# Insert any remaining aquariums
if aquarium_data:
    db.executemany("""INSERT INTO aquariums (name, user_id, length, depth, height, volume, date, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", aquarium_data)
# Insert any remaining aquarium classes
if class_data:
    db.executemany("INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)", class_data)
print("aquariums done in", time.time() - start, "seconds")

# Add critters
start = time.time()
aquariums = db.execute("SELECT id, user_id FROM aquariums").fetchall()
critter_data = []
for i in range(1, critter_count + 1):
    aquarium = random.choice(aquariums)
    aquarium_id, user_id = aquarium
    species = random.choice(animals)
    count = random.randint(1, 30)
    critter_data.append((species, count, aquarium_id, user_id))

    # Insert in batches
    if len(critter_data) >= batch_size:
        db.executemany("INSERT OR IGNORE INTO critters (species, count, aquarium_id, user_id) VALUES (?, ?, ?, ?)",
                       critter_data)
        critter_data.clear()  # Clear the list after insertion

# Insert any remaining critters
if critter_data:
    db.executemany("INSERT OR IGNORE INTO critters (species, count, aquarium_id, user_id) VALUES (?, ?, ?, ?)",
                    critter_data)
print("critters done in", time.time() - start, "seconds")

# Add comments
start = time.time()
now = datetime.datetime.now().isoformat()
comment_data = []
for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    aquarium_id = random.randint(1, aquarium_count)
    comment_data.append((aquarium_id, user_id, "message" + str(i), now))

    # Insert in batches
    if len(comment_data) >= batch_size:
        db.executemany("""INSERT INTO comments (aquarium_id, user_id, content, sent_at)
                       VALUES (?, ?, ?, ?)""", comment_data)
        comment_data.clear()  # Clear the list after insertion

# Insert any remaining comments
if comment_data:
    db.executemany("""INSERT INTO comments (aquarium_id, user_id, content, sent_at)
                   VALUES (?, ?, ?, ?)""", comment_data)
print("comments done in", time.time() - start, "seconds")

db.commit()
db.close()
