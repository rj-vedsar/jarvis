import unittest
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
        self.assertFalse(Validator.is_safe_path("C:\\Windows\\System32"))
        self.assertFalse(Validator.is_safe_path("..\\..\\Windows"))
        self.assertTrue(Validator.is_safe_path("D:\\Projects\\Jarvis"))

    def test_url_validation(self):
        self.assertTrue(Validator.is_safe_url("https://example.com"))
        self.assertFalse(Validator.is_safe_url("javascript:alert(1)"))
        self.assertFalse(Validator.is_safe_url("file:///etc/passwd"))

if __name__ == '__main__':
    unittest.main()
