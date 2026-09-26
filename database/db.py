import sqlite3
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
