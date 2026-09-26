import unittest
from ai.ollama_provider import OllamaProvider
from voice.tts import TTSEngine

class TestRemainingPhases(unittest.TestCase):
    def test_ollama_fallback(self):
        prov = OllamaProvider()
        # Mock URL to fail
        prov.base_url = "http://localhost:99999"
        res = prov.process_command("open notepad")
        # Should fallback to rule engine which returns a dict
        self.assertIsInstance(res, dict)
        self.assertEqual(res['action'], 'open_app')

    def test_tts_initialization(self):
        tts = TTSEngine()
        self.assertTrue(tts.enabled)

if __name__ == '__main__':
    unittest.main()
