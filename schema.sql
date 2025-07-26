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
    description TEXT
);

CREATE TABLE critters (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    aquarium INTEGER REFERENCES aquariums,
    species TEXT,
    group_size INTEGER
);