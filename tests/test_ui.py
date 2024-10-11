import unittest
from .test_base import BaseTestCase
import customtkinter as ctk
from ui.main_window import MainWindow
from ui.user_management import UserManagement

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

if __name__ == '__main__':
    unittest.main()
