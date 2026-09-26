import os
from pathlib import Path

# Phase 1: Re-scaffolding with offline-first local architecture

files = {
    "requirements.txt": "PySide6>=6.5.0\npsutil>=5.9.0\npyttsx3>=2.90\nSpeechRecognition>=3.10.0\nrequests>=2.31.0\n",
    "README.md": "# JARVIS - Offline Windows 11 AI Assistant\nZero API Key, Local First.\n",
    "main.py": """import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
""",
    "core/assistant.py": """from ai.rule_engine import RuleEngine

class Assistant:
    def __init__(self):
        self.rule_engine = RuleEngine()
    
    def process_command(self, text):
        return self.rule_engine.parse(text)
""",
    "ai/rule_engine.py": """class RuleEngine:
    def parse(self, text):
        text = text.lower()
        if "cpu" in text or "ram" in text or "disk" in text:
            from system.monitor import SystemMonitor
            stats = SystemMonitor().get_stats()
            return f"CPU: {stats['cpu']}%, RAM: {stats['ram']}%, Disk: {stats['disk']}%"
        elif "open chrome" in text:
            return "Opening Chrome... (Mocked)"
        elif "lock" in text:
            return "Locking computer... (Mocked)"
        else:
            return "I don't understand that command in offline rule mode."
""",
    "system/monitor.py": """import psutil

class SystemMonitor:
    def get_stats(self):
        return {
            'cpu': psutil.cpu_percent(interval=0.1),
            'ram': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
""",
    "ui/main_window.py": """from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PySide6.QtCore import QTimer
from core.assistant import Assistant
from system.monitor import SystemMonitor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.assistant = Assistant()
        self.monitor = SystemMonitor()
        self.setWindowTitle("JARVIS - Offline Mode")
        self.resize(800, 600)
        
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        self.stats_label = QLabel("Initializing monitor...")
        layout.addWidget(self.stats_label)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append("JARVIS: Ready. Running in Local Offline Mode.")
        layout.addWidget(self.chat_display)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Jarvis...")
        self.input_field.returnPressed.connect(self.handle_input)
        layout.addWidget(self.input_field)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)
        
    def update_stats(self):
        stats = self.monitor.get_stats()
        self.stats_label.setText(f"CPU: {stats['cpu']}% | RAM: {stats['ram']}% | DISK: {stats['disk']}%")
        
    def handle_input(self):
        text = self.input_field.text()
        if text:
            self.chat_display.append(f"\\nUSER: {text}")
            response = self.assistant.process_command(text)
            self.chat_display.append(f"JARVIS: {response}")
            self.input_field.clear()
"""
}

dirs_to_create = ["core", "ai", "security", "actions", "system", "voice", "files", "developer", "database", "ui", "utils", "tests"]

for d in dirs_to_create:
    Path(f"e:/local-server/www/jarvis/{d}").mkdir(parents=True, exist_ok=True)
    Path(f"e:/local-server/www/jarvis/{d}/__init__.py").touch(exist_ok=True)

for path_str, content in files.items():
    path = Path("e:/local-server/www/jarvis") / path_str
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffolding complete.")
