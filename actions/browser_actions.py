import webbrowser
from actions.registry import ActionRegistry, ActionDef, ActionResult
from security.validator import Validator

def handle_open_url(params) -> ActionResult:
    url = params.get("url", "")
    if not Validator.is_safe_url(url):
        return ActionResult(success=False, action="open_url", message="Invalid or unsafe URL scheme")
    
    webbrowser.open(url)
    return ActionResult(success=True, action="open_url", message=f"Opened URL: {url}")

ActionRegistry.register(ActionDef("open_url", "Opens a URL in default browser", handle_open_url))
