import dataclasses
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
