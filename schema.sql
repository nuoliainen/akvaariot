CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE aquariums (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
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
    aquarium_id INTEGER REFERENCES aquariums(id) ON DELETE CASCADE,
    title TEXT,
    value TEXT,
    UNIQUE(aquarium_id, title)
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    aquarium_id INTEGER REFERENCES aquariums(id) ON DELETE CASCADE,
    image BLOB,
    file_type TEXT
);

CREATE TABLE main_images (
    id INTEGER PRIMARY KEY,
    aquarium_id INTEGER REFERENCES aquariums(id) ON DELETE CASCADE,
    image_id INTEGER REFERENCES images(id) ON DELETE CASCADE,
    UNIQUE(aquarium_id)
);

CREATE TABLE critters (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    aquarium_id INTEGER REFERENCES aquariums(id) ON DELETE CASCADE,
    species TEXT,
    count INTEGER,
    UNIQUE (aquarium_id, species)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    aquarium_id INTEGER REFERENCES aquariums ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    content TEXT,
    sent_at TEXT
);

-- Indexes for aquariums
CREATE INDEX idx_aquariums_user_id ON aquariums(user_id);

-- Indexes for images
CREATE INDEX idx_images_aquarium_id ON images(aquarium_id);
CREATE INDEX idx_main_images_aquarium_id ON main_images(aquarium_id);

-- Indexes for critters
CREATE INDEX idx_critters_user_id ON critters(user_id);
CREATE INDEX idx_critters_aquarium_id ON critters(aquarium_id);

-- Indexes for comments
CREATE INDEX idx_comments_aquarium_id ON comments(aquarium_id);

-- Indexes for aquarium_classes
CREATE INDEX idx_aquarium_classes_aquarium_id_title_value
ON aquarium_classes (aquarium_id, title, value);
