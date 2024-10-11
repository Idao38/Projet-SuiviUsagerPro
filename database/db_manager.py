import sqlite3
from models.user import User

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            date_naissance TEXT,
            telephone TEXT NOT NULL,
            email TEXT,
            adresse TEXT,
            date_creation TEXT NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS workshops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            description TEXT,
            categorie TEXT,
            payant BOOLEAN,
            date TEXT NOT NULL,
            conseiller TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        self.conn.commit()

    def execute_query(self, query, params=None):
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor.lastrowid

    def fetch_all(self, query, params=None):
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        if params is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def search_users(self, search_term):
        query = """
        SELECT * FROM users
        WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ? OR email LIKE ?
        """
        params = ('%' + search_term + '%',) * 4
        results = self.fetch_all(query, params)
        return [User.from_db(row) for row in results]

    def get_all_users(self):
        query = "SELECT * FROM users"
        results = self.fetch_all(query)
        return [User.from_db(row) for row in results]
