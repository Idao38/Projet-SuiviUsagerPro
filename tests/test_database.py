from .test_base import BaseTestCase

class TestDatabaseManager(BaseTestCase):
    def test_connection(self):
        self.assertIsNotNone(self.db_manager.conn)

    def test_create_tables(self):
        tables = self.db_manager.fetch_all("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [table[0] for table in tables]
        self.assertIn('users', table_names)
        self.assertIn('workshops', table_names)

    def test_insert_and_fetch(self):
        self.db_manager.execute_query("INSERT INTO users (nom, prenom, telephone, date_creation) VALUES (?, ?, ?, ?)", ('Doe', 'John', '0123456789', '2023-01-01'))
        result = self.db_manager.fetch_one("SELECT nom, prenom, telephone FROM users WHERE nom = ?", ('Doe',))
        self.assertEqual(result, ('Doe', 'John', '0123456789'))