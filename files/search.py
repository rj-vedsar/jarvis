import os
import glob
from actions.registry import ActionRegistry, ActionDef, ActionResult

def handle_search_file(params) -> ActionResult:
    query = params.get("query", "")
    directory = params.get("directory", os.path.expanduser("~"))
    
    if not query:
        return ActionResult(success=False, action="search_file", message="No query provided")
        
    results = []
    try:
        # Shallow search for MVP to avoid freezing
        for root, dirs, files in os.walk(directory):
            for file in files:
                if query.lower() in file.lower():
                    results.append(os.path.join(root, file))
            break # only one level for safety
            
        return ActionResult(success=True, action="search_file", message=f"Found {len(results)} files", data={"files": results})
    except Exception as e:
        return ActionResult(success=False, action="search_file", message=str(e))

ActionRegistry.register(ActionDef("search_file", "Search for a file", handle_search_file))
