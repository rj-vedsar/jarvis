import subprocess
from actions.registry import ActionRegistry, ActionDef, ActionResult
import os

def handle_git_status(params) -> ActionResult:
    path = params.get("path", os.getcwd())
    try:
        result = subprocess.run(["git", "status", "-s"], cwd=path, capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return ActionResult(success=True, action="git_status", message=f"Git status:\n{result.stdout if result.stdout else 'Clean working tree'}")
        return ActionResult(success=False, action="git_status", message="Not a git repository.")
    except Exception as e:
        return ActionResult(success=False, action="git_status", message=f"Git error: {str(e)}")

ActionRegistry.register(ActionDef("git_status", "Gets git status for a project", handle_git_status))
