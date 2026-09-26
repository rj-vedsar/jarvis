import time
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
