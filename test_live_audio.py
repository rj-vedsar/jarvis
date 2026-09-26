import os
import time
import pyaudio
import numpy as np

def test_microphone():
    print("Testing physical microphone capture via PyAudio...")
    p = pyaudio.PyAudio()
    try:
        info = p.get_default_input_device_info()
        print(f"Microphone detected: {info['name']}")
        print(f"Sample Rate: {info['defaultSampleRate']}")
        print(f"Channels: {info['maxInputChannels']}")
        
        # Test 1 second of actual capture
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1280)
        print("Listening for 1 second...")
        frames = []
        for _ in range(0, int(16000 / 1280)):
            data = stream.read(1280, exception_on_overflow=False)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        print("Physical microphone capture successful!")
        return True
    except Exception as e:
        print(f"Microphone capture failed: {e}")
        return False
    finally:
        p.terminate()

def test_stt():
    print("\\nTesting STT Inference...")
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        audio = np.zeros(16000, dtype=np.float32)
        segments, info = model.transcribe(audio, beam_size=1)
        text = "".join([segment.text for segment in segments])
        print("STT Inference passed.")
        return True
    except Exception as e:
        print(f"STT Inference failed: {e}")
        return False

def test_wakeword():
    print("\\nTesting Wake Word...")
    from voice.wakeword import WakeWordEngine
    engine = WakeWordEngine()
    if engine.initialize():
        print("Wake Word Initialized successfully.")
        return True
    else:
        print("Wake Word Initialization failed or model missing.")
        return False

if __name__ == "__main__":
    mic = test_microphone()
    stt = test_stt()
    ww = test_wakeword()
    
    print("\\n--- Pipeline Report ---")
    print(f"Microphone Capture: {'OK' if mic else 'FAILED'}")
    print(f"STT Inference:      {'OK' if stt else 'FAILED'}")
    print(f"Wake Word Logic:    {'OK' if ww else 'MISSING MODEL'}")
