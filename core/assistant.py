from ai.rule_engine import RuleEngine

class Assistant:
    def __init__(self):
        self.rule_engine = RuleEngine()
    
    def process_command(self, text):
        return self.rule_engine.parse(text)
