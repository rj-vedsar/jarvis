import os
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
