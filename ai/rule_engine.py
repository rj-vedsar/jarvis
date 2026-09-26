class RuleEngine:
    def parse(self, text):
        text = text.lower()
        if "cpu" in text or "ram" in text or "disk" in text:
            from system.monitor import SystemMonitorWorker
            import psutil
            return f"CPU: {psutil.cpu_percent()}%, RAM: {psutil.virtual_memory().percent}%"
        elif "open notepad" in text:
            return {"action": "open_app", "params": {"app_name": "notepad"}}
        elif "open calculator" in text:
            return {"action": "open_app", "params": {"app_name": "calculator"}}
        elif "open terminal" in text:
            return {"action": "open_terminal", "params": {}}
        elif "restart computer" in text:
            return {"action": "restart", "params": {}}
        elif "lock computer" in text:
            return {"action": "lock_workstation", "params": {}}
        elif "open google" in text:
            return {"action": "open_url", "params": {"url": "https://google.com"}}
        else:
            return "I don't understand that command in offline rule mode."
