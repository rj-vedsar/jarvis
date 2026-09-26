import os
from urllib.parse import urlparse
import string

class Validator:
    ALLOWED_SCHEMES = {"http", "https"}
    BLOCKED_PATHS = {"c:\\windows", "c:\\program files"}
    
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
