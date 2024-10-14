import unittest
from database.db_manager import DatabaseManager
import os

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Utilisez la base de données temporaire créée dans run_tests.py
        cls.db_path = os.environ.get('TEST_DB_PATH')
        cls.db_manager = DatabaseManager(cls.db_path)

    def setUp(self):
        # Pas besoin de réinitialiser la base de données ici, car elle est déjà configurée
        pass

    def tearDown(self):
        # Nettoyage après chaque test si nécessaire
        pass

    @classmethod
    def tearDownClass(cls):
        # Fermer la connexion à la base de données
        cls.db_manager.close()
