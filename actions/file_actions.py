import os
from actions.registry import ActionRegistry, ActionDef, ActionResult
from security.validator import Validator

def handle_open_folder(params) -> ActionResult:
    path = params.get("path", "")
    if not Validator.is_safe_path(path) or not os.path.isdir(path):
        return ActionResult(success=False, action="open_folder", message="Invalid or missing directory path")
    
    os.startfile(path)
    return ActionResult(success=True, action="open_folder", message=f"Opened folder: {path}")

def handle_open_file(params) -> ActionResult:
    path = params.get("path", "")
    if not Validator.is_safe_path(path) or not os.path.isfile(path):
        return ActionResult(success=False, action="open_file", message="Invalid or missing file path")
    
    os.startfile(path)
    return ActionResult(success=True, action="open_file", message=f"Opened file: {path}")

ActionRegistry.register(ActionDef("open_folder", "Opens a folder", handle_open_folder))
ActionRegistry.register(ActionDef("open_file", "Opens a file", handle_open_file))
