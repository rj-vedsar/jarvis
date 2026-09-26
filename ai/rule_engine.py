class RuleEngine:
    def parse(self, text):
        text = text.lower()
        if "cpu" in text or "ram" in text or "disk" in text:
            from system.monitor import SystemMonitor
            stats = SystemMonitor().get_stats()
            return f"CPU: {stats['cpu']}%, RAM: {stats['ram']}%, Disk: {stats['disk']}%"
        elif "open chrome" in text:
            return "Opening Chrome... (Mocked)"
        elif "lock" in text:
            return "Locking computer... (Mocked)"
        else:
            return "I don't understand that command in offline rule mode."
