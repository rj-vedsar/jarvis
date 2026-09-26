import pyttsx3
import threading

class TTSEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.enabled = True
        
    def speak(self, text):
        if not self.enabled: return
        def run():
            self.engine.say(text)
            self.engine.runAndWait()
        threading.Thread(target=run, daemon=True).start()
