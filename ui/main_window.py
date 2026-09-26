from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
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
            self.chat_display.append(f"\nUSER: {text}")
            response = self.assistant.process_command(text)
            self.chat_display.append(f"JARVIS: {response}")
            self.input_field.clear()
