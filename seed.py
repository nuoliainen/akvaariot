import random
import datetime
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM aquariums")
db.execute("DELETE FROM critters")
db.execute("DELETE FROM aquarium_classes")
db.execute("DELETE FROM comments")
db.execute("DELETE FROM images")
db.execute("DELETE FROM main_images")

user_count = 1000
aquarium_count = 10**5
comment_count = 10**6
critter_count = 10**6

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

# Add users
for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)])

# Add aquariums
for i in range(1, aquarium_count + 1):
    user_id = random.randint(1, user_count)

    l = random.randrange(20, 301, 5)
    d = random.randrange(20, 101, 5)
    h = random.randrange(20, 101, 5)
    volume = l*d*h // 1000

    start_date = datetime.date(2010, 8, 20)
    end_date = datetime.date(2025, 8, 20)
    num_days   = (end_date - start_date).days
    rand_days   = random.randint(1, num_days)
    random_date = start_date + datetime.timedelta(days=rand_days)

    db.execute("""INSERT INTO aquariums (name, user_id, length, depth, height, volume, date, description)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
               ["tank" + str(i), user_id, l, d, h, volume, str(random_date), "description "*random.randint(1, 100)])

    # Assign some classes
    if random.random() < 0.95:
        db.execute("INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)",
                [i, "Vesi", random.choices(["makea vesi", "murtovesi", "merivesi"], weights=(10, 1, 5))[0]])
    if random.random() < 0.9:
        db.execute("INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)",
                [i, "Lämpötila", random.choices(["trooppinen", "lauhkea", "kylmä"], weights=(10, 3, 1))[0]])
    if random.random() < 0.6:
        db.execute("INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)",
                    [i, "Tyyppi", random.choices(["vain kaloja", "vain selkärangattomia", "lajiakvaario",
                                                "riutta-akvaario", "kasviakvaario", "biotooppi", "aquascape"],
                                                weights=(2, 0.5, 1, 5, 15, 2, 3))[0]])
    if random.random() < 0.5:
        db.execute("INSERT INTO aquarium_classes (aquarium_id, title, value) VALUES (?, ?, ?)",
                [i, "Tekniikka", random.choices(["high tech", "low tech"], weights=(1, 3))[0]])

# Add critters
for i in range(1, critter_count + 1):
    aquarium_id = random.randint(1, aquarium_count)
    row = db.execute("SELECT user_id, volume FROM aquariums WHERE id = ?",
                         [aquarium_id]).fetchone()
    user_id, volume = row
    species = random.choice(animals)
    count = random.randint(1, 30)
    db.execute("INSERT INTO critters (species, count, aquarium_id, user_id) VALUES (?, ?, ?, ?)",
               [species, count, aquarium_id, user_id])

# Add comments
for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    aquarium_id = random.randint(1, aquarium_count)
    db.execute("""INSERT INTO comments (aquarium_id, user_id, content, sent_at)
                  VALUES (?, ?, ?, datetime('now'))""",
               [aquarium_id, user_id, "message" + str(i)])

db.commit()
db.close()
