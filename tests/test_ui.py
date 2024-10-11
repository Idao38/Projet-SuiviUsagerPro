import unittest
import threading
from .test_base import BaseTestCase
import customtkinter as ctk
from ui.main_window import MainWindow
from ui.user_management import UserManagement
from ui.add_user import AddUser
from models.user import User
import tkinter as tk
import logging
import signal

logging.basicConfig(level=logging.DEBUG)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Test timed out")

class TestUI(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.main_window = MainWindow(self.root, db_manager=self.db_manager)

    def tearDown(self):
        super().tearDown()
        if self.root:
            self.root.update()
            self.root.destroy()

    def test_with_timeout(self, seconds=5):
        def test_function():
            self.test_add_user()

        thread = threading.Thread(target=test_function)
        thread.start()
        thread.join(seconds)
        if thread.is_alive():
            self.fail("Test timed out")

    def test_add_user(self):
        # Le contenu de votre test ici
        pass

    # Autres méthodes de test...

if __name__ == '__main__':
    unittest.main()
