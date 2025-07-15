class ExecutionContext:
    def __init__(self, name, parent=None, entry_pos=None):
        self.name = name
        self.parent = parent
        self.entry_pos = entry_pos
        self.symbol_storage = None