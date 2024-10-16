import unittest
from database.db_manager import DatabaseManager
import os
import logging
import tempfile

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Utilisez la base de données temporaire créée dans run_tests.py
        cls.db_path = os.environ.get('TEST_DB_PATH')
        cls.db_manager = DatabaseManager(cls.db_path)

    def setUp(self):
        # Créer un fichier temporaire pour la base de données de test
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.initialize()
        logging.info(f"Base de données de test initialisée : {self.temp_db.name}")
        self.addCleanup(self.db_manager.close)

    def tearDown(self):
        self.db_manager.close()
        os.unlink(self.temp_db.name)  # Supprimer le fichier temporaire

    @classmethod
    def tearDownClass(cls):
        # Fermer la connexion à la base de données
        cls.db_manager.close()
