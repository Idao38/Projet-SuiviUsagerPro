import unittest
import tempfile
import os
from database.db_manager import DatabaseManager

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Créer un fichier temporaire pour la base de données
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Initialiser le DatabaseManager avec le fichier temporaire
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.connect()
        self.db_manager.create_tables()

    def tearDown(self):
        # Fermer la connexion à la base de données
        self.db_manager.close()
        
        # Supprimer le fichier de base de données temporaire
        os.unlink(self.temp_db.name)