import unittest
from .test_base import BaseTestCase
from models.user import User
from models.workshop import Workshop
from utils.date_utils import get_current_date
from datetime import datetime

class TestUser(BaseTestCase):
    def test_user_creation(self):
        user = User(nom="Dupont", prenom="Marie", date_naissance="1990-01-01", telephone="0123456789", date_creation=datetime.now().strftime('%Y-%m-%d'))
        user.save(self.db_manager)
        
        fetched_user = User.get_by_id(self.db_manager, 1)
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user.nom, "Dupont")
        self.assertEqual(fetched_user.prenom, "Marie")
        self.assertEqual(fetched_user.telephone, "0123456789")

    def test_user_update(self):
        user = User(nom="Dupont", prenom="Marie", date_naissance="1990-01-01", telephone="0123456789")
        user.save(self.db_manager)
        
        user.nom = "Martin"
        user.save(self.db_manager)
        
        updated_user = User.get_by_id(self.db_manager, user.id)
        self.assertEqual(updated_user.nom, "Martin")

    def test_user_delete(self):
        user = User(nom="Dupont", prenom="Marie", date_naissance="1990-01-01", telephone="0123456789")
        user.save(self.db_manager)
        
        User.delete(self.db_manager, user.id)
        
        self.assertIsNone(User.get_by_id(self.db_manager, user.id))

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

    def test_workshop_update(self):
        user = User(nom="Dupont", prenom="Marie", telephone="0123456789")
        user.save(self.db_manager)

        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Individuel")
        workshop.save(self.db_manager)

        workshop.description = "Updated Workshop"
        workshop.save(self.db_manager)

        updated_workshop = Workshop.get_by_id(self.db_manager, workshop.id)
        self.assertEqual(updated_workshop.description, "Updated Workshop")

    def test_workshop_delete(self):
        user = User(nom="Dupont", prenom="Marie", telephone="0123456789")
        user.save(self.db_manager)

        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Individuel")
        workshop.save(self.db_manager)

        Workshop.delete(self.db_manager, workshop.id)

        self.assertIsNone(Workshop.get_by_id(self.db_manager, workshop.id))

if __name__ == '__main__':
    unittest.main()
