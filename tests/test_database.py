from .test_base import BaseTestCase
from models.user import User
from models.workshop import Workshop
from datetime import datetime

class TestDatabaseManager(BaseTestCase):
    def test_connection(self):
        # Vérifiez simplement que la connexion peut être établie
        with self.db_manager.get_connection() as conn:
            self.assertIsNotNone(conn)

    def test_create_tables(self):
        # Ce test reste inchangé
        pass

    def test_insert_and_fetch(self):
        self.db_manager.execute("INSERT INTO users (nom, prenom, telephone, date_creation) VALUES (?, ?, ?, ?)", 
                                ('Doe', 'John', '0123456789', datetime.now().strftime("%Y-%m-%d")))
        
        result = self.db_manager.fetch_one("SELECT * FROM users WHERE nom = ?", ('Doe',))
        self.assertIsNotNone(result)
        self.assertEqual(result['nom'], 'Doe')
        self.assertEqual(result['prenom'], 'John')

    def test_create_user(self):
        user = User(nom="Doe", prenom="John", telephone="0123456789")
        user.save(self.db_manager)
        
        retrieved_user = User.get_by_id(self.db_manager, user.id)
        self.assertEqual(retrieved_user.nom, "Doe")
        self.assertEqual(retrieved_user.prenom, "John")

    def test_create_workshop(self):
        user = User(nom="Doe", prenom="John", telephone="0123456789")
        user.save(self.db_manager)
        
        workshop = Workshop(user_id=user.id, categorie="Atelier individuel", date="2023-01-01", conseiller="Test Conseiller")
        workshop.save(self.db_manager)
        
        retrieved_workshop = Workshop.get_by_id(self.db_manager, workshop.id)
        self.assertEqual(retrieved_workshop.categorie, "Atelier individuel")
        self.assertEqual(retrieved_workshop.date, "2023-01-01")
        self.assertEqual(retrieved_workshop.conseiller, "Test Conseiller")
