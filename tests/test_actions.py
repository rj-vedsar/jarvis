import unittest
from actions.registry import ActionRegistry
from security.validator import Validator
from security.confirmations import ConfirmationManager
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
        # Restart requires confirmation, AI passes {}
        res = ActionRegistry.execute("restart", {})
        self.assertFalse(res.success)
        self.assertTrue(res.confirmation_required)
        
        token = res.confirmation_token
        self.assertIsNotNone(token)
        
        # Now with proper token
        res2 = ActionRegistry.execute("restart", {}, confirmation_token=token)
        self.assertTrue(res2.success)

if __name__ == '__main__':
    unittest.main()
