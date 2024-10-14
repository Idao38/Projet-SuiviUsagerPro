import sqlite3
import logging
from contextlib import contextmanager
from models.user import User
from models.workshop import Workshop

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def initialize(self):
        """Initialize the database connection and create tables if they don't exist."""
        try:
            with self.get_connection() as conn:
                self.create_tables(conn)
                self.add_last_activity_date_column()  # Ajoutez cette ligne
            logging.info(f"Database initialized successfully: {self.db_path}")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        yield conn

    def execute(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor
            except sqlite3.Error as e:
                logging.error(f"Error executing query: {e}")
                conn.rollback()
                raise

    def fetch_one(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchone()
            except sqlite3.Error as e:
                logging.error(f"Error fetching one: {e}")
                raise

    def fetch_all(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
            except sqlite3.Error as e:
                logging.error(f"Error fetching all: {e}")
                raise

    def get_all_users(self):
        query = "SELECT * FROM users"
        rows = self.fetch_all(query)
        return [User.from_db(row) for row in rows]

    def get_all_workshops(self):
        query = "SELECT * FROM workshops"
        rows = self.fetch_all(query)
        return [Workshop.from_db(row) for row in rows]

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.ProgrammingError:
                logging.warning("Tentative de fermeture d'une connexion dans un thread différent.")
            self.connection = None
            self.cursor = None
            logging.info("Database connection closed")

    def create_tables(self, connection):
        with open('database/schema.sql', 'r') as schema_file:
            schema = schema_file.read()
        
        connection.executescript(schema)

    # Ajoutez d'autres méthodes spécifiques si nécessaire

    def search_users(self, search_term):
        query = """
        SELECT * FROM users 
        WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ? OR email LIKE ?
        """
        search_pattern = f"%{search_term}%"
        rows = self.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern))
        return [User.from_db(row) for row in rows]

    def add_last_activity_date_column(self):
        try:
            # Vérifier si la colonne existe déjà
            check_query = "PRAGMA table_info(users);"
            columns = self.fetch_all(check_query)
            column_names = [column['name'] for column in columns]
            
            if 'last_activity_date' not in column_names:
                query = "ALTER TABLE users ADD COLUMN last_activity_date TEXT;"
                self.execute(query)
                logging.info("Colonne last_activity_date ajoutée avec succès.")
            else:
                logging.info("La colonne last_activity_date existe déjà.")
        except Exception as e:
            logging.error(f"Erreur lors de la vérification/ajout de la colonne last_activity_date : {e}")

def initialize(self):
    try:
        with self.get_connection() as conn:
            self.create_tables(conn)
            self.add_last_activity_date_column() 
        logging.info(f"Database initialized successfully: {self.db_path}")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise
