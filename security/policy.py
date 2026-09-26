class SecurityPolicy:
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
