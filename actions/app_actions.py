import os
import subprocess
from actions.registry import ActionRegistry, ActionDef, ActionResult
import shutil

COMMON_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "terminal": "wt.exe",
}

def handle_open_app(params) -> ActionResult:
    app_name = params.get("app_name", "").lower()
    
    if app_name in COMMON_APPS:
        exe_name = COMMON_APPS[app_name]
        if shutil.which(exe_name) or os.path.exists(f"C:\\Windows\\System32\\{exe_name}"):
            subprocess.Popen(exe_name, shell=False)
            return ActionResult(success=True, action="open_app", message=f"Opened {app_name}")
        
    return ActionResult(success=False, action="open_app", message=f"Application {app_name} not found.")

def handle_open_terminal(params) -> ActionResult:
    if shutil.which("wt.exe"):
        subprocess.Popen("wt.exe", shell=False)
        return ActionResult(success=True, action="open_terminal", message="Opened Windows Terminal")
    elif shutil.which("cmd.exe"):
        subprocess.Popen("cmd.exe", shell=False)
        return ActionResult(success=True, action="open_terminal", message="Opened Command Prompt fallback")
    return ActionResult(success=False, action="open_terminal", message="No terminal emulator found")

ActionRegistry.register(ActionDef("open_app", "Opens a common application", handle_open_app))
ActionRegistry.register(ActionDef("open_terminal", "Opens Windows Terminal", handle_open_terminal))
