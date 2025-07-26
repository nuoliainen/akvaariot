CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE aquariums (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    name TEXT,
    volume INTEGER,
    length INTEGER,
    depth INTEGER,
    height INTEGER,
    volume INTEGER,
    setup_date TEXT
);

CREATE TABLE critters (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    aquarium INTEGER REFERENCES aquariums,
    species INTEGER,
    group_size INTEGER
);