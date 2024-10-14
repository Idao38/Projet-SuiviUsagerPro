CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_naissance TEXT,
    telephone TEXT NOT NULL,
    email TEXT,
    adresse TEXT,
    date_creation TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    last_activity_date TEXT
);

CREATE TABLE IF NOT EXISTS workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    description TEXT,
    categorie TEXT,
    payant BOOLEAN,
    date TEXT,
    conseiller TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
