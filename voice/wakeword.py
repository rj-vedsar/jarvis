import os
import threading
import queue

class WakeWordEngine:
    def __init__(self):
        self.enabled = False
        self.listening = False
        self._thread = None
        self.model = None
        self.model_path = os.path.join(os.path.dirname(__file__), "..", "models", "hey_jarvis_v0.1.onnx")
        
    def initialize(self):
        # We enforce a local model directory for the ONNX file
        if not os.path.exists(self.model_path):
            print("Wake-word model not installed. Please place hey_jarvis_v0.1.onnx in the models/ directory.")
            self.enabled = False
            return False

        try:
            import openwakeword
            from openwakeword.model import Model
            # Load explicitly from the local path
            self.model = Model(wakeword_models=[self.model_path], inference_framework="onnx")
            self.enabled = True
            return True
        except Exception as e:
            print(f"WakeWord Init Error: {e}")
            self.enabled = False
            return False
            
    def start_listening(self, on_wake_callback):
        if not self.enabled: return
        self.listening = True
        
        def _listen_loop():
            # In a real app, PyAudio would feed frames here
            import time
            while self.listening:
                time.sleep(0.1)
                
        self._thread = threading.Thread(target=_listen_loop, daemon=True)
        self._thread.start()
        
    def stop_listening(self):
        self.listening = False
