CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE aquariums (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    name TEXT,
    length INTEGER,
    depth INTEGER,
    height INTEGER,
    volume INTEGER,
    date TEXT,
    description TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE aquarium_classes (
    id INTEGER PRIMARY KEY,
    aquarium_id INTEGER REFERENCES aquariums,
    title TEXT,
    value TEXT
);

CREATE TABLE critters (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    aquarium_id INTEGER REFERENCES aquariums,
    species TEXT,
    count INTEGER
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    aquarium_id INTEGER REFERENCES aquariums,
    user_id INTEGER REFERENCES users,
    content TEXT,
    sent_at TEXT
);
