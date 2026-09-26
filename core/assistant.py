from ai.rule_engine import RuleEngine
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
