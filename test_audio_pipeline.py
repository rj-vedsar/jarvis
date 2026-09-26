import os
import numpy as np
import time

def test_stt():
    print("Testing STT...")
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
        audio = np.zeros(16000, dtype=np.float32)
        segments, info = model.transcribe(audio, beam_size=1)
        text = "".join([segment.text for segment in segments])
        print(f"STT Test Passed. Output: '{text}'")
        return True
    except Exception as e:
        print(f"STT Test Failed: {e}")
        return False

def test_wakeword():
    print("Testing Wake Word...")
    try:
        from openwakeword.model import Model
        model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        audio = np.zeros(16000, dtype=np.int16)
        for i in range(0, len(audio), 1280):
            frame = audio[i:i+1280]
            if len(frame) == 1280:
                prediction = model.predict(frame)
        print(f"Wake Word Test Passed. Output classes: {list(model.models.keys())}")
        return True
    except Exception as e:
        print(f"Wake Word Test Failed: {e}")
        return False

if __name__ == "__main__":
    stt_ok = test_stt()
    ww_ok = test_wakeword()
    if stt_ok and ww_ok:
        print("AUDIO_PIPELINE_SUCCESS")
    else:
        print("AUDIO_PIPELINE_FAILURE")
