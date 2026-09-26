import os
from pathlib import Path

files = {
    "database/db.py": """import sqlite3
import threading
from pathlib import Path

class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _init_db(self):
        self.db_path = Path("jarvis_local.db")
        self.local_thread = threading.local()
        self.create_tables()
        
    def _get_connection(self):
        if not hasattr(self.local_thread, "conn") or self.local_thread.conn is None:
            self.local_thread.conn = sqlite3.connect(str(self.db_path))
            self.local_thread.conn.row_factory = sqlite3.Row
        return self.local_thread.conn

    def create_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            path TEXT,
            type TEXT
        )
        ''')
        conn.commit()

    def execute(self, query, params=()):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
""",
    "database/repositories.py": """from database.db import Database

class SettingsRepository:
    def __init__(self):
        self.db = Database()
        
    def get(self, key, default=None):
        cursor = self.db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else default
        
    def set(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

class ConversationRepository:
    def __init__(self):
        self.db = Database()
        
    def add_message(self, role, content):
        self.db.execute("INSERT INTO conversation_history (role, content) VALUES (?, ?)", (role, content))
        
    def get_history(self, limit=50):
        cursor = self.db.execute("SELECT role, content, timestamp FROM conversation_history ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()][::-1]
""",
    "system/monitor.py": """import psutil
import time
from PySide6.QtCore import QObject, Signal, QThread

class SystemMonitorWorker(QThread):
    stats_updated = Signal(dict)
    alert_triggered = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        while self.running:
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            try:
                battery = psutil.sensors_battery()
                battery_percent = battery.percent if battery else None
            except:
                battery_percent = None

            stats = {
                'cpu': cpu,
                'ram': ram,
                'disk': disk,
                'battery': battery_percent
            }
            
            self.stats_updated.emit(stats)
            
            # Simple threshold logic
            if ram > 85: self.alert_triggered.emit(f"High RAM Usage: {ram}%")
            if cpu > 90: self.alert_triggered.emit(f"High CPU Usage: {cpu}%")
            if disk > 90: self.alert_triggered.emit(f"High Disk Usage: {disk}%")
            if battery_percent is not None and battery_percent < 20:
                self.alert_triggered.emit(f"Low Battery: {battery_percent}%")
                
            time.sleep(2)
            
    def stop(self):
        self.running = False
        self.wait()
""",
    "ui/main_window.py": """from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit
from core.assistant import Assistant
from system.monitor import SystemMonitorWorker
from database.repositories import ConversationRepository

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.assistant = Assistant()
        self.conv_repo = ConversationRepository()
        self.setWindowTitle("JARVIS - Offline Mode")
        self.resize(800, 600)
        
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        self.stats_label = QLabel("Initializing monitor...")
        layout.addWidget(self.stats_label)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.load_history()
        layout.addWidget(self.chat_display)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Jarvis...")
        self.input_field.returnPressed.connect(self.handle_input)
        layout.addWidget(self.input_field)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        self.monitor_worker = SystemMonitorWorker()
        self.monitor_worker.stats_updated.connect(self.update_stats)
        self.monitor_worker.alert_triggered.connect(self.handle_alert)
        self.monitor_worker.start()
        
    def load_history(self):
        self.chat_display.append("JARVIS: Ready. Running in Local Offline Mode.")
        history = self.conv_repo.get_history(limit=5)
        for msg in history:
            self.chat_display.append(f"{msg['role'].upper()}: {msg['content']}")
        
    def update_stats(self, stats):
        batt_str = f" | BATT: {stats['battery']}%" if stats['battery'] is not None else ""
        self.stats_label.setText(f"CPU: {stats['cpu']}% | RAM: {stats['ram']}% | DISK: {stats['disk']}%{batt_str}")
        
    def handle_alert(self, alert_msg):
        # We append directly to chat for visibility, but could use a status bar or popup
        self.chat_display.append(f"SYSTEM ALERT: {alert_msg}")

    def handle_input(self):
        text = self.input_field.text()
        if text:
            self.chat_display.append(f"\\nUSER: {text}")
            self.conv_repo.add_message("user", text)
            
            response = self.assistant.process_command(text)
            self.chat_display.append(f"JARVIS: {response}")
            self.conv_repo.add_message("jarvis", response)
            
            self.input_field.clear()
            
    def closeEvent(self, event):
        self.monitor_worker.stop()
        super().closeEvent(event)
""",
    "tests/test_database.py": """import unittest
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
""",
    "tests/test_system_monitor.py": """import unittest
from system.monitor import SystemMonitorWorker

class TestSystemMonitor(unittest.TestCase):
    def test_worker_initialization(self):
        worker = SystemMonitorWorker()
        self.assertTrue(worker.running)
        # We won't start the thread in test to avoid blocking, just test it constructs
        worker.stop()
        self.assertFalse(worker.running)

if __name__ == '__main__':
    unittest.main()
"""
}

for path_str, content in files.items():
    path = Path("e:/local-server/www/jarvis") / path_str
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Phase 2 & 3 files created.")
