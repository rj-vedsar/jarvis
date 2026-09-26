import os
from pathlib import Path

files = {
    "ai/ollama_provider.py": """import requests
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
""",
    "developer/git.py": """import subprocess
from actions.registry import ActionRegistry, ActionDef, ActionResult
import os

def handle_git_status(params) -> ActionResult:
    path = params.get("path", os.getcwd())
    try:
        result = subprocess.run(["git", "status", "-s"], cwd=path, capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return ActionResult(success=True, action="git_status", message=f"Git status:\\n{result.stdout if result.stdout else 'Clean working tree'}")
        return ActionResult(success=False, action="git_status", message="Not a git repository.")
    except Exception as e:
        return ActionResult(success=False, action="git_status", message=f"Git error: {str(e)}")

ActionRegistry.register(ActionDef("git_status", "Gets git status for a project", handle_git_status))
""",
    "files/search.py": """import os
import glob
from actions.registry import ActionRegistry, ActionDef, ActionResult

def handle_search_file(params) -> ActionResult:
    query = params.get("query", "")
    directory = params.get("directory", os.path.expanduser("~"))
    
    if not query:
        return ActionResult(success=False, action="search_file", message="No query provided")
        
    results = []
    try:
        # Shallow search for MVP to avoid freezing
        for root, dirs, files in os.walk(directory):
            for file in files:
                if query.lower() in file.lower():
                    results.append(os.path.join(root, file))
            break # only one level for safety
            
        return ActionResult(success=True, action="search_file", message=f"Found {len(results)} files", data={"files": results})
    except Exception as e:
        return ActionResult(success=False, action="search_file", message=str(e))

ActionRegistry.register(ActionDef("search_file", "Search for a file", handle_search_file))
""",
    "voice/tts.py": """import pyttsx3
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
""",
    "build_windows.ps1": """# PyInstaller build script
pip install pyinstaller
pyinstaller --noconfirm --windowed --name "Jarvis" main.py
Write-Output "Build complete in dist/Jarvis/"
""",
    "tests/test_all_phases.py": """import unittest
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
"""
}

# Update Assistant to use Ollama provider and TTS
assistant_update = """from ai.ollama_provider import OllamaProvider
from actions.registry import ActionRegistry
from voice.tts import TTSEngine
import actions.windows_actions
import actions.app_actions
import actions.file_actions
import actions.browser_actions
import developer.git
import files.search

class Assistant:
    def __init__(self):
        self.ai = OllamaProvider()
        self.tts = TTSEngine()
        self.pending_confirmation_token = None
        self.pending_action_name = None
    
    def process_command(self, text):
        if self.pending_confirmation_token:
            if text.lower() in ['yes', 'y', 'confirm']:
                token = self.pending_confirmation_token
                action_name = self.pending_action_name
                self.pending_confirmation_token = None
                self.pending_action_name = None
                
                result = ActionRegistry.execute(action_name, {}, confirmation_token=token)
                self.tts.speak(result.message)
                return result.message
            else:
                self.pending_confirmation_token = None
                self.pending_action_name = None
                self.tts.speak("Action cancelled.")
                return "Action cancelled."
                
        intent = self.ai.process_command(text)
        if isinstance(intent, dict) and 'action' in intent:
            result = ActionRegistry.execute(intent['action'], intent.get('params', {}))
            
            if result.confirmation_required:
                self.pending_confirmation_token = result.confirmation_token
                self.pending_action_name = intent['action']
                msg = result.message + " Type 'yes' to confirm."
                self.tts.speak(msg)
                return msg
                
            self.tts.speak(result.message)
            return result.message
        
        self.tts.speak(str(intent))
        return str(intent)
"""
files["core/assistant.py"] = assistant_update


for path_str, content in files.items():
    path = Path("e:/local-server/www/jarvis") / path_str
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Phases 6-22 core files created.")
