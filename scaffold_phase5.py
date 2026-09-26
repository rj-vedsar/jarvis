import os
from pathlib import Path

files = {
    "security/policy.py": """class SecurityPolicy:
    RISK_LEVELS = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "BLOCKED": 4}
    
    BLOCKED_ACTIONS = {
        "execute_shell",
        "execute_powershell",
        "execute_python",
        "extract_passwords",
        "disable_antivirus",
        "disable_firewall",
    }
    
    @classmethod
    def is_blocked(cls, action_name: str) -> bool:
        return action_name in cls.BLOCKED_ACTIONS
""",
    "security/confirmations.py": """import time
import uuid

class ConfirmationManager:
    _pending_confirmations = {}
    TIMEOUT_SECONDS = 30
    
    @classmethod
    def create_confirmation(cls, action_name: str, params: dict) -> str:
        token = str(uuid.uuid4())
        cls._pending_confirmations[token] = {
            "action": action_name,
            "params": dict(params),  # Make a copy
            "timestamp": time.time()
        }
        return token
        
    @classmethod
    def validate_and_consume(cls, token: str, action_name: str) -> dict:
        if token not in cls._pending_confirmations:
            return None
            
        pending = cls._pending_confirmations[token]
        
        # Check timeout
        if time.time() - pending["timestamp"] > cls.TIMEOUT_SECONDS:
            del cls._pending_confirmations[token]
            return None
            
        # Ensure action matches
        if pending["action"] != action_name:
            del cls._pending_confirmations[token]
            return None
            
        # Consume token
        params = pending["params"]
        del cls._pending_confirmations[token]
        return params
""",
    "security/validator.py": """import os
from urllib.parse import urlparse
import string

class Validator:
    ALLOWED_SCHEMES = {"http", "https"}
    BLOCKED_PATHS = {"c:\\\\windows", "c:\\\\program files"}
    
    @staticmethod
    def is_safe_url(url: str) -> bool:
        if not url: return False
        try:
            parsed = urlparse(url)
            return parsed.scheme.lower() in Validator.ALLOWED_SCHEMES
        except:
            return False

    @staticmethod
    def is_safe_path(path: str) -> bool:
        if not path: return False
        
        # Normalize path
        normalized = os.path.normpath(path).lower()
        
        # Block directory traversal
        if ".." in normalized: return False
        
        # Block sensitive directories
        for blocked in Validator.BLOCKED_PATHS:
            if normalized.startswith(blocked):
                return False
                
        return True
""",
    "actions/registry.py": """import dataclasses
from typing import Callable, Dict, Any, Optional
from security.policy import SecurityPolicy
from security.confirmations import ConfirmationManager
from database.repositories import AuditRepository

@dataclasses.dataclass
class ActionResult:
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confirmation_required: bool = False
    confirmation_token: Optional[str] = None

@dataclasses.dataclass
class ActionDef:
    name: str
    description: str
    handler: Callable[[Dict[str, Any]], ActionResult]
    requires_confirmation: bool = False
    risk_level: str = "LOW"

class ActionRegistry:
    _registry: Dict[str, ActionDef] = {}
    audit_repo = AuditRepository()

    @classmethod
    def register(cls, action_def: ActionDef):
        cls._registry[action_def.name] = action_def

    @classmethod
    def execute(cls, name: str, params: Dict[str, Any], confirmation_token: str = None) -> ActionResult:
        # Check if permanently blocked
        if SecurityPolicy.is_blocked(name):
            cls.audit_repo.log_audit(name, "BLOCKED", False)
            return ActionResult(success=False, action=name, message="Action is permanently blocked.")
            
        if name not in cls._registry:
            cls.audit_repo.log_audit(name, "UNKNOWN", False)
            return ActionResult(success=False, action=name, message="Unknown action", error="Action not found")
            
        action_def = cls._registry[name]
        
        # Confirmation logic
        actual_params = params
        if action_def.requires_confirmation:
            if not confirmation_token:
                token = ConfirmationManager.create_confirmation(name, params)
                cls.audit_repo.log_audit(name, "CONFIRMATION_REQUESTED", False)
                return ActionResult(
                    success=False, 
                    action=name, 
                    message="Confirmation required to proceed.", 
                    confirmation_required=True,
                    confirmation_token=token
                )
            
            validated_params = ConfirmationManager.validate_and_consume(confirmation_token, name)
            if validated_params is None:
                cls.audit_repo.log_audit(name, "CONFIRMATION_FAILED", False)
                return ActionResult(success=False, action=name, message="Confirmation invalid, expired, or mismatch.")
            actual_params = validated_params
            
        # Execution
        try:
            result = action_def.handler(actual_params)
            cls.audit_repo.log_audit(name, "EXECUTED", result.success)
            return result
        except Exception as e:
            cls.audit_repo.log_audit(name, "EXECUTION_ERROR", False)
            return ActionResult(success=False, action=name, message="Action execution failed", error=str(e))
""",
    "database/repositories.py": """from database.db import Database
import time

class SettingsRepository:
    def __init__(self):
        self.db = Database()
        
    def get(self, key, default=None):
        cursor = self.db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else default
        
    def set(self, key, value):
        self.db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))

class ConversationRepository:
    def __init__(self):
        self.db = Database()
        
    def add_message(self, role, content):
        self.db.execute("INSERT INTO conversation_history (role, content) VALUES (?, ?)", (role, content))
        
    def get_history(self, limit=50):
        cursor = self.db.execute("SELECT role, content, timestamp FROM conversation_history ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()][::-1]

class AuditRepository:
    def __init__(self):
        self.db = Database()
        # Initialize table if not exists (putting here for simplicity)
        self.db.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            status TEXT,
            success BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
    def log_audit(self, action, status, success):
        self.db.execute("INSERT INTO audit_logs (action, status, success) VALUES (?, ?, ?)", 
                        (action, status, success))
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
        self.pending_confirmation_token = None
        self.pending_action_name = None
    
    def process_command(self, text):
        # Handle active confirmation
        if self.pending_confirmation_token:
            if text.lower() in ['yes', 'y', 'confirm']:
                token = self.pending_confirmation_token
                action_name = self.pending_action_name
                self.pending_confirmation_token = None
                self.pending_action_name = None
                
                result = ActionRegistry.execute(action_name, {}, confirmation_token=token)
                return result.message
            else:
                self.pending_confirmation_token = None
                self.pending_action_name = None
                return "Action cancelled."
                
        # Parse intent
        intent = self.rule_engine.parse(text)
        if isinstance(intent, dict) and 'action' in intent:
            # AI/Rule Engine tries to pass arbitrary params. ActionRegistry ignores _confirmed hack.
            result = ActionRegistry.execute(intent['action'], intent.get('params', {}))
            
            if result.confirmation_required:
                self.pending_confirmation_token = result.confirmation_token
                self.pending_action_name = intent['action']
                return result.message + " Type 'yes' to confirm."
                
            return result.message
        
        return str(intent)
""",
    "tests/test_security.py": """import unittest
from security.policy import SecurityPolicy
from security.confirmations import ConfirmationManager
from security.validator import Validator
from actions.registry import ActionRegistry
import time

class TestSecurity(unittest.TestCase):
    def test_blocked_actions(self):
        self.assertTrue(SecurityPolicy.is_blocked("execute_shell"))
        res = ActionRegistry.execute("execute_shell", {})
        self.assertFalse(res.success)
        self.assertEqual(res.message, "Action is permanently blocked.")

    def test_confirmation_manager(self):
        token = ConfirmationManager.create_confirmation("restart", {"test": 123})
        
        # Valid consume
        params = ConfirmationManager.validate_and_consume(token, "restart")
        self.assertEqual(params["test"], 123)
        
        # Replay fails
        params2 = ConfirmationManager.validate_and_consume(token, "restart")
        self.assertIsNone(params2)

    def test_confirmation_mismatch(self):
        token = ConfirmationManager.create_confirmation("restart", {})
        # Action name mismatch
        params = ConfirmationManager.validate_and_consume(token, "shutdown")
        self.assertIsNone(params)

    def test_path_validation(self):
        self.assertFalse(Validator.is_safe_path("C:\\\\Windows\\\\System32"))
        self.assertFalse(Validator.is_safe_path("..\\\\..\\\\Windows"))
        self.assertTrue(Validator.is_safe_path("D:\\\\Projects\\\\Jarvis"))

    def test_url_validation(self):
        self.assertTrue(Validator.is_safe_url("https://example.com"))
        self.assertFalse(Validator.is_safe_url("javascript:alert(1)"))
        self.assertFalse(Validator.is_safe_url("file:///etc/passwd"))

if __name__ == '__main__':
    unittest.main()
"""
}

for path_str, content in files.items():
    path = Path("e:/local-server/www/jarvis") / path_str
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Phase 5 files created.")
