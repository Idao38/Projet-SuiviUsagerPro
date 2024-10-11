CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_naissance TEXT,
    telephone TEXT NOT NULL,
    email TEXT,
    adresse TEXT,
    date_creation TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT,
    categorie TEXT NOT NULL,
    payant BOOLEAN NOT NULL DEFAULT 0,
    date TEXT NOT NULL,
    conseiller TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);