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
        try:
            with self.get_connection() as conn:
                self.create_tables(conn)
                self._add_columns()
            logging.info(f"Base de données initialisée avec succès : {self.db_path}")
        except Exception as e:
            logging.error(f"Erreur lors de l'initialisation de la base de données : {e}")
            raise

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params or ())
                conn.commit()
                return cursor
            except sqlite3.Error as e:
                logging.error(f"Erreur d'exécution de la requête : {e}")
                conn.rollback()
                raise

    def fetch_one(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()

    def fetch_all(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def create_tables(self, connection):
        with open('database/schema.sql', 'r') as schema_file:
            schema = schema_file.read()
        connection.executescript(schema)

    def get_last_insert_id(self):
        return self.fetch_one("SELECT last_insert_rowid()")[0]

    # Méthodes pour les utilisateurs
    def get_all_users(self):
        rows = self.fetch_all("SELECT * FROM users")
        return [User.from_db(row) for row in rows]

    def search_users(self, search_term):
        query = """
        SELECT * FROM users 
        WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ? OR email LIKE ?
        """
        search_pattern = f"%{search_term}%"
        rows = self.fetch_all(query, (search_pattern,) * 4)
        return [User.from_db(row) for row in rows]

    # Méthodes pour les ateliers
    def get_all_workshops(self):
        rows = self.fetch_all("SELECT * FROM workshops")
        return [Workshop.from_db(row) for row in rows]

    # Méthodes privées pour l'ajout de colonnes
    def _add_columns(self):
        self._add_last_activity_date_column()
        self._add_last_payment_date_column()
        self._add_paid_today_column()

    def _add_last_activity_date_column(self):
        self._add_column_if_not_exists('users', 'last_activity_date', 'TEXT')

    def _add_last_payment_date_column(self):
        self._add_column_if_not_exists('users', 'last_payment_date', 'TEXT')

    def _add_paid_today_column(self):
        self._add_column_if_not_exists('workshops', 'paid_today', 'INTEGER DEFAULT 0')

    def _add_column_if_not_exists(self, table, column, data_type):
        columns = self.fetch_all(f"PRAGMA table_info({table});")
        if column not in [col['name'] for col in columns]:
            self.execute(f"ALTER TABLE {table} ADD COLUMN {column} {data_type};")
            logging.info(f"Colonne {column} ajoutée avec succès à la table {table}.")
        else:
            logging.info(f"La colonne {column} existe déjà dans la table {table}.")

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.ProgrammingError:
                logging.warning("Tentative de fermeture d'une connexion déjà fermée.")
            finally:
                self.connection = None
        logging.info("Connexion à la base de données fermée.")
