from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit
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
            self.chat_display.append(f"\nUSER: {text}")
            self.conv_repo.add_message("user", text)
            
            response = self.assistant.process_command(text)
            self.chat_display.append(f"JARVIS: {response}")
            self.conv_repo.add_message("jarvis", response)
            
            self.input_field.clear()
            
    def closeEvent(self, event):
        self.monitor_worker.stop()
        super().closeEvent(event)
