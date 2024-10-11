import sqlite3
import logging
from contextlib import contextmanager

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
            logging.info(f"Database initialized successfully: {self.db_path}")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise

    @contextmanager
    def get_connection(self):
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            yield connection
        finally:
            if connection:
                connection.close()

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
        return self.fetch_all(query)

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
