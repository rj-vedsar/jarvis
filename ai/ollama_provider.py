import requests
from ai.rule_engine import RuleEngine

class OllamaProvider:
    def __init__(self):
        self.base_url = "http://127.0.0.1:11434"
        self.rule_engine = RuleEngine()
        
    def check_health(self):
        try:
            res = requests.get(f"{self.base_url}/api/version", timeout=1)
            return res.status_code == 200
        except:
            return False
            
    def get_models(self):
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=1)
            if res.status_code == 200:
                return [m['name'] for m in res.json().get('models', [])]
            return []
        except:
            return []
            
    def process_command(self, text, model="qwen2.5-coder:1.5b-base"):
        # Since local LLM parsing to strict JSON intent is complex and prone to hallucinations,
        # we try rule engine first for deterministic tasks.
        rule_intent = self.rule_engine.parse(text)
        if isinstance(rule_intent, dict) and 'action' in rule_intent:
            return rule_intent
            
        if not self.check_health():
            return rule_intent # fallback to rule engine completely
            
        # If we reach here, we could use Ollama to parse intent.
        # For MVP, if rule engine doesn't understand, we ask Ollama for a conversational response.
        try:
            payload = {
                "model": model,
                "prompt": f"User said: {text}. Reply concisely.",
                "stream": False
            }
            res = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=5)
            if res.status_code == 200:
                return res.json().get("response", "I understood, but response is empty.")
        except:
            pass
            
        return rule_intent
