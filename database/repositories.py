from database.db import Database

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
