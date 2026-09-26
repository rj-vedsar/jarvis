import os
from pathlib import Path

files = {
    "requirements.txt": "PySide6>=6.5.0\npsutil>=5.9.0\npyttsx3>=2.90\nSpeechRecognition>=3.10.0\npython-dotenv>=1.0.0\nopenai>=1.0.0\n",
    ".env.example": "OPENAI_API_KEY=your_api_key_here\nLLM_PROVIDER=openai\n",
    "main.py": """import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.assistant import Assistant

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JARVIS")
    
    assistant = Assistant()
    window = MainWindow(assistant)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
""",
    "core/assistant.py": """import asyncio
from windows.system_monitor import SystemMonitor

class Assistant:
    def __init__(self):
        self.monitor = SystemMonitor()
    
    def process_text_command(self, text):
        return f"Processed: {text}"
""",
    "windows/system_monitor.py": """import psutil

class SystemMonitor:
    def get_stats(self):
        return {
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
""",
    "ui/main_window.py": """from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import QTimer

class MainWindow(QMainWindow):
    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant
        self.setWindowTitle("JARVIS")
        self.resize(800, 600)
        
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        self.stats_label = QLabel("CPU: 0% | RAM: 0% | DISK: 0%")
        layout.addWidget(self.stats_label)
        
        self.chat_display = QLabel("JARVIS is ready.")
        layout.addWidget(self.chat_display)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Jarvis...")
        self.input_field.returnPressed.connect(self.handle_input)
        layout.addWidget(self.input_field)
        
        self.voice_btn = QPushButton("🎤 Start Listening")
        layout.addWidget(self.voice_btn)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)
        
    def update_stats(self):
        stats = self.assistant.monitor.get_stats()
        self.stats_label.setText(f"CPU: {stats['cpu']}% | RAM: {stats['ram']}% | DISK: {stats['disk']}%")
        
    def handle_input(self):
        text = self.input_field.text()
        if text:
            response = self.assistant.process_text_command(text)
            self.chat_display.setText(self.chat_display.text() + f"\\nUser: {text}\\nJARVIS: {response}")
            self.input_field.clear()
"""
}

for path_str, content in files.items():
    path = Path("e:/local-server/www/jarvis") / path_str
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffolding complete.")
