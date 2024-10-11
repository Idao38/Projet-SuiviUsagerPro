import unittest
from .test_base import BaseTestCase
import customtkinter as ctk
from ui.main_window import MainWindow
from ui.user_management import UserManagement
from ui.add_user import AddUser
from models.user import User

class TestUI(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.main_window = MainWindow(self.root, db_manager=self.db_manager)

    def tearDown(self):
        super().tearDown()
        self.root.destroy()

    def test_main_window_creation(self):
        self.assertIsInstance(self.main_window, MainWindow)
        self.assertIsNotNone(self.main_window.dashboard)
        self.assertIsNotNone(self.main_window.user_management)
        self.assertIsNotNone(self.main_window.workshop_history)
        self.assertIsNotNone(self.main_window.settings)

    def test_user_management_creation(self):
        user_management = self.main_window.user_management
        self.assertIsInstance(user_management, UserManagement)
        # Ajoutez d'autres assertions si nécessaire

    def test_add_user(self):
        add_user = AddUser(self.root, self.db_manager)
        add_user.nom_entry.insert(0, "Dupont")
        add_user.prenom_entry.insert(0, "Jean")
        add_user.telephone_entry.insert(0, "0123456789")
        add_user.date_naissance_entry.insert(0, "01/01/1990")

        add_user.add_user()

        users = User.get_all(self.db_manager)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].nom, "Dupont")
        self.assertEqual(users[0].prenom, "Jean")

    def test_user_management_search(self):
        user = User(nom="Dupont", prenom="Jean", telephone="0123456789")
        user.save(self.db_manager)

        user_management = UserManagement(self.root, self.db_manager, self.main_window)
        user_management.search_entry.insert(0, "Dupont")
        user_management.search_users()

        # Vérifiez que l'utilisateur est affiché dans la liste des résultats
        # Cela peut nécessiter d'ajouter une méthode pour accéder aux résultats de recherche dans UserManagement
        self.assertEqual(len(user_management.search_results), 1)
        self.assertEqual(user_management.search_results[0].nom, "Dupont")

if __name__ == '__main__':
    unittest.main()
