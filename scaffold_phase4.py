import os
from pathlib import Path

files = {
    "actions/registry.py": """import dataclasses
from typing import Callable, Dict, Any, Optional

@dataclasses.dataclass
class ActionResult:
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confirmation_required: bool = False

@dataclasses.dataclass
class ActionDef:
    name: str
    description: str
    handler: Callable[[Dict[str, Any]], ActionResult]
    requires_confirmation: bool = False
    risk_level: str = "LOW"

class ActionRegistry:
    _registry: Dict[str, ActionDef] = {}

    @classmethod
    def register(cls, action_def: ActionDef):
        cls._registry[action_def.name] = action_def

    @classmethod
    def execute(cls, name: str, params: Dict[str, Any]) -> ActionResult:
        if name not in cls._registry:
            return ActionResult(success=False, action=name, message="Unknown action", error="Action not found")
        action_def = cls._registry[name]
        
        # If the action requires confirmation and it's not explicitly confirmed in params
        if action_def.requires_confirmation and not params.get("_confirmed"):
            return ActionResult(
                success=False, 
                action=name, 
                message="Confirmation required to proceed.", 
                confirmation_required=True
            )
            
        try:
            return action_def.handler(params)
        except Exception as e:
            return ActionResult(success=False, action=name, message="Action execution failed", error=str(e))
""",
    "security/validator.py": """import os
from urllib.parse import urlparse

class Validator:
    @staticmethod
    def is_safe_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https")
        except:
            return False

    @staticmethod
    def is_safe_path(path: str) -> bool:
        # Prevent arbitrary path traversal or execution of risky extensions if needed
        # In a real app, this would be more robust.
        if not path: return False
        if ".." in path: return False
        return True
""",
    "actions/windows_actions.py": """import os
import ctypes
import subprocess
from actions.registry import ActionRegistry, ActionDef, ActionResult
from security.validator import Validator

def handle_lock_workstation(params) -> ActionResult:
    # Lock workstation: rundll32.exe user32.dll,LockWorkStation
    ctypes.windll.user32.LockWorkStation()
    return ActionResult(success=True, action="lock_workstation", message="Workstation locked.")

def handle_shutdown(params) -> ActionResult:
    # Mocking actual shutdown for safety during testing
    # os.system("shutdown /s /t 1")
    return ActionResult(success=True, action="shutdown", message="System shutdown initiated (Mocked).")

def handle_restart(params) -> ActionResult:
    # Mocking actual restart
    # os.system("shutdown /r /t 1")
    return ActionResult(success=True, action="restart", message="System restart initiated (Mocked).")

ActionRegistry.register(ActionDef("lock_workstation", "Locks the PC", handle_lock_workstation, requires_confirmation=True, risk_level="MEDIUM"))
ActionRegistry.register(ActionDef("shutdown", "Shuts down the PC", handle_shutdown, requires_confirmation=True, risk_level="HIGH"))
ActionRegistry.register(ActionDef("restart", "Restarts the PC", handle_restart, requires_confirmation=True, risk_level="HIGH"))
""",
    "actions/app_actions.py": """import os
import subprocess
from actions.registry import ActionRegistry, ActionDef, ActionResult
import shutil

COMMON_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "terminal": "wt.exe",
}

def handle_open_app(params) -> ActionResult:
    app_name = params.get("app_name", "").lower()
    
    if app_name in COMMON_APPS:
        exe_name = COMMON_APPS[app_name]
        if shutil.which(exe_name) or os.path.exists(f"C:\\\\Windows\\\\System32\\\\{exe_name}"):
            subprocess.Popen(exe_name, shell=False)
            return ActionResult(success=True, action="open_app", message=f"Opened {app_name}")
        
    return ActionResult(success=False, action="open_app", message=f"Application {app_name} not found.")

def handle_open_terminal(params) -> ActionResult:
    if shutil.which("wt.exe"):
        subprocess.Popen("wt.exe", shell=False)
        return ActionResult(success=True, action="open_terminal", message="Opened Windows Terminal")
    elif shutil.which("cmd.exe"):
        subprocess.Popen("cmd.exe", shell=False)
        return ActionResult(success=True, action="open_terminal", message="Opened Command Prompt fallback")
    return ActionResult(success=False, action="open_terminal", message="No terminal emulator found")

ActionRegistry.register(ActionDef("open_app", "Opens a common application", handle_open_app))
ActionRegistry.register(ActionDef("open_terminal", "Opens Windows Terminal", handle_open_terminal))
""",
    "actions/file_actions.py": """import os
from actions.registry import ActionRegistry, ActionDef, ActionResult
from security.validator import Validator

def handle_open_folder(params) -> ActionResult:
    path = params.get("path", "")
    if not Validator.is_safe_path(path) or not os.path.isdir(path):
        return ActionResult(success=False, action="open_folder", message="Invalid or missing directory path")
    
    os.startfile(path)
    return ActionResult(success=True, action="open_folder", message=f"Opened folder: {path}")

def handle_open_file(params) -> ActionResult:
    path = params.get("path", "")
    if not Validator.is_safe_path(path) or not os.path.isfile(path):
        return ActionResult(success=False, action="open_file", message="Invalid or missing file path")
    
    os.startfile(path)
    return ActionResult(success=True, action="open_file", message=f"Opened file: {path}")

ActionRegistry.register(ActionDef("open_folder", "Opens a folder", handle_open_folder))
ActionRegistry.register(ActionDef("open_file", "Opens a file", handle_open_file))
""",
    "actions/browser_actions.py": """import webbrowser
from actions.registry import ActionRegistry, ActionDef, ActionResult
from security.validator import Validator

def handle_open_url(params) -> ActionResult:
    url = params.get("url", "")
    if not Validator.is_safe_url(url):
        return ActionResult(success=False, action="open_url", message="Invalid or unsafe URL scheme")
    
    webbrowser.open(url)
    return ActionResult(success=True, action="open_url", message=f"Opened URL: {url}")

ActionRegistry.register(ActionDef("open_url", "Opens a URL in default browser", handle_open_url))
""",
    "core/assistant.py": """from ai.rule_engine import RuleEngine
from actions.registry import ActionRegistry
import actions.windows_actions
import actions.app_actions
import actions.file_actions
import actions.browser_actions

class Assistant:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.pending_confirmation = None
    
    def process_command(self, text):
        if self.pending_confirmation:
            if text.lower() in ['yes', 'y', 'confirm']:
                action_name = self.pending_confirmation['action']
                params = self.pending_confirmation['params']
                params['_confirmed'] = True
                self.pending_confirmation = None
                result = ActionRegistry.execute(action_name, params)
                return result.message
            else:
                self.pending_confirmation = None
                return "Action cancelled."
                
        intent = self.rule_engine.parse(text)
        if isinstance(intent, dict) and 'action' in intent:
            result = ActionRegistry.execute(intent['action'], intent.get('params', {}))
            if result.confirmation_required:
                self.pending_confirmation = {
                    'action': intent['action'],
                    'params': intent.get('params', {})
                }
                return result.message + " Type 'yes' to confirm."
            return result.message
        
        return str(intent)
""",
    "ai/rule_engine.py": """class RuleEngine:
    def parse(self, text):
        text = text.lower()
        if "cpu" in text or "ram" in text or "disk" in text:
            from system.monitor import SystemMonitorWorker
            import psutil
            return f"CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%"
        elif "open notepad" in text:
            return {"action": "open_app", "params": {"app_name": "notepad"}}
        elif "open calculator" in text:
            return {"action": "open_app", "params": {"app_name": "calculator"}}
        elif "open terminal" in text:
            return {"action": "open_terminal", "params": {}}
        elif "restart computer" in text:
            return {"action": "restart", "params": {}}
        elif "lock computer" in text:
            return {"action": "lock_workstation", "params": {}}
        elif "open google" in text:
            return {"action": "open_url", "params": {"url": "https://google.com"}}
        else:
            return "I don't understand that command in offline rule mode."
""",
    "tests/test_actions.py": """import unittest
from actions.registry import ActionRegistry
from security.validator import Validator
import actions.windows_actions
import actions.app_actions
import actions.file_actions
import actions.browser_actions

class TestActions(unittest.TestCase):
    def test_unknown_action(self):
        res = ActionRegistry.execute("non_existent_action", {})
        self.assertFalse(res.success)
        self.assertEqual(res.message, "Unknown action")

    def test_validator_url(self):
        self.assertTrue(Validator.is_safe_url("https://example.com"))
        self.assertFalse(Validator.is_safe_url("ftp://example.com"))
        self.assertFalse(Validator.is_safe_url("file:///C:/Windows/System32/cmd.exe"))

    def test_validator_path(self):
        self.assertTrue(Validator.is_safe_path("C:\\\\Temp"))
        self.assertFalse(Validator.is_safe_path("..\\\\..\\\\Windows"))

    def test_confirmation_required(self):
        # Restart requires confirmation
        res = ActionRegistry.execute("restart", {})
        self.assertFalse(res.success)
        self.assertTrue(res.confirmation_required)
        
        # Now with confirmation
        res2 = ActionRegistry.execute("restart", {"_confirmed": True})
        self.assertTrue(res2.success)

if __name__ == '__main__':
    unittest.main()
"""
}

for path_str, content in files.items():
    path = Path("e:/local-server/www/jarvis") / path_str
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Phase 4 files created.")
