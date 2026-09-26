from ai.ollama_provider import OllamaProvider
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
