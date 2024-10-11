import unittest
import tempfile
import os
from database.db_manager import DatabaseManager

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager(':memory:')
        self.db_manager.connect()
        self.db_manager.create_tables()

    def tearDown(self):
        if self.db_manager:
            self.db_manager.close()