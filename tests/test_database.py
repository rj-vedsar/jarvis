import unittest
import os
from database.db import Database
from database.repositories import SettingsRepository, ConversationRepository

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use an in-memory db for tests by overriding path
        db = Database()
        db.db_path = ":memory:"
        db.create_tables()

    def test_settings(self):
        repo = SettingsRepository()
        repo.set("theme", "dark")
        self.assertEqual(repo.get("theme"), "dark")
        self.assertIsNone(repo.get("nonexistent"))

    def test_conversations(self):
        repo = ConversationRepository()
        repo.add_message("user", "Hello")
        repo.add_message("jarvis", "Hi")
        history = repo.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['content'], "Hello")
        self.assertEqual(history[1]['content'], "Hi")

if __name__ == '__main__':
    unittest.main()
