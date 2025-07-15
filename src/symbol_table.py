class SymbolStorage:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
        
    def get(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent:
            return self.parent.get(name)
        return value
        
    def add(self, name, value):
        self.symbols[name] = value