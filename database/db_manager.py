import sqlite3
import os
import logging
from contextlib import contextmanager
from models.user import User
from models.workshop import Workshop
import sys

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def initialize(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Déterminer le chemin correct vers schema.sql
                if getattr(sys, 'frozen', False):
                    # Si l'application est "gelée" (exécutable)
                    application_path = sys._MEIPASS
                else:
                    # Si l'application est en cours d'exécution à partir du script
                    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                schema_path = os.path.join(application_path, 'database', 'schema.sql')
                
                logging.info(f"Chemin du schéma SQL : {schema_path}")
                if not os.path.exists(schema_path):
                    logging.error(f"Le fichier schema.sql n'existe pas à l'emplacement : {schema_path}")
                    raise FileNotFoundError(f"schema.sql non trouvé : {schema_path}")
                
                with open(schema_path, 'r') as schema_file:
                    schema = schema_file.read()
                cursor.executescript(schema)
            logging.info("Base de données initialisée avec succès.")
        except Exception as e:
            logging.error(f"Erreur détaillée lors de l'initialisation de la base de données : {str(e)}")
            logging.error(f"Chemin de la base de données : {self.db_path}")
            raise

    @contextmanager
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            conn.close()

    def execute(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor

    def fetch_one(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()

    def fetch_all(self, query, params=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
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

    def commit(self):
        with self.get_connection() as conn:
            conn.commit()

    def rollback(self):
        with self.get_connection() as conn:
            conn.rollback()

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.ProgrammingError:
                logging.warning("Tentative de fermeture d'une connexion déjà fermée.")
            finally:
                self.connection = None
        logging.info("Connexion à la base de données fermée.")

    def get_connection(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
            except sqlite3.OperationalError as e:
                logging.error(f"Erreur lors de la connexion à la base de données : {e}")
                # Vérifier si le dossier parent existe
                parent_dir = os.path.dirname(self.db_path)
                if not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir)
                        logging.info(f"Dossier créé : {parent_dir}")
                        # Réessayer la connexion
                        self.connection = sqlite3.connect(self.db_path)
                        self.connection.row_factory = sqlite3.Row
                    except Exception as e:
                        logging.error(f"Impossible de créer le dossier de la base de données : {e}")
                        raise
                else:
                    raise
        return self.connection

    def begin_transaction(self):
        self.connection.execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        self.connection.commit()

    def rollback_transaction(self):
        self.connection.rollback()
