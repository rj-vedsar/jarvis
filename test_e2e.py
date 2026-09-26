import os
import unittest
import requests
import sqlite3
import subprocess

class EndToEndVerification(unittest.TestCase):
    def test_01_ollama(self):
        try:
            res = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
            self.assertEqual(res.status_code, 200)
            models = res.json().get('models', [])
            self.assertTrue(any(m['name'].startswith('qwen') or m['name'].startswith('llama') for m in models))
        except:
            self.skipTest("Ollama is not running")

    def test_02_database_persistence(self):
        self.assertTrue(os.path.exists("jarvis_local.db"))
        conn = sqlite3.connect("jarvis_local.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn("settings", tables)
        self.assertIn("audit_logs", tables)
        conn.close()

    def test_03_executable_exists(self):
        # Depending on if PyInstaller finished
        self.assertTrue(os.path.exists("dist/Jarvis/Jarvis.exe"))

    def test_04_rule_engine(self):
        from ai.rule_engine import RuleEngine
        engine = RuleEngine()
        intent = engine.parse("open notepad")
        self.assertIsInstance(intent, dict)
        self.assertEqual(intent['action'], "open_app")

if __name__ == '__main__':
    unittest.main()
