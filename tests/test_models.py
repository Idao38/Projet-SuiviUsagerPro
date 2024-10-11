import unittest
from .test_base import BaseTestCase
from models.user import User
from models.workshop import Workshop

class TestUser(BaseTestCase):
    def test_user_creation(self):
        user = User(nom="Dupont", prenom="Marie", date_naissance="1990-01-01", telephone="0123456789")
        user.save(self.db_manager)
        
        fetched_user = User.get_by_id(self.db_manager, 1)
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.nom, "Dupont")
        self.assertEqual(fetched_user.prenom, "Marie")
        self.assertEqual(fetched_user.telephone, "0123456789")

class TestWorkshop(BaseTestCase):
    def test_workshop_creation(self):
        user = User(nom="Dupont", prenom="Marie", telephone="0123456789")
        user.save(self.db_manager)

        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Individuel")
        workshop.save(self.db_manager)

        fetched_workshop = Workshop.get_by_id(self.db_manager, 1)
        self.assertIsNotNone(fetched_workshop)
        self.assertEqual(fetched_workshop.description, "Test Workshop")
        self.assertEqual(fetched_workshop.categorie, "Individuel")

if __name__ == '__main__':
    unittest.main()
