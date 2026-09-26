import threading
import queue

class STTEngine:
    def __init__(self):
        self.enabled = False
        self.model = None
        self.audio_queue = queue.Queue()
        self.listening = False
        self._thread = None
        
    def initialize_model(self, model_size="tiny"):
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            self.enabled = True
            return True
        except ImportError:
            self.enabled = False
            return False
            
    def start_listening(self, callback):
        if not self.enabled or not self.model: return
        self.listening = True
        
        def _listen_loop():
            # In a real app, PyAudio would feed self.audio_queue here.
            # We mock the loop for safety without PyAudio blocking.
            while self.listening:
                try:
                    audio_chunk = self.audio_queue.get(timeout=1)
                    segments, info = self.model.transcribe(audio_chunk, beam_size=5)
                    text = "".join([segment.text for segment in segments])
                    if text.strip():
                        callback(text.strip())
                except queue.Empty:
                    continue
                except Exception:
                    pass

        self._thread = threading.Thread(target=_listen_loop, daemon=True)
        self._thread.start()
        
    def stop_listening(self):
        self.listening = False
        if self._thread:
            self._thread.join(timeout=1)
