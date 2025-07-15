from .position import TextPosition

class Token:
    def __init__(self, type_, value=None, start_pos=None, end_pos=None):
        self.type = type_
        self.value = value
        
        if start_pos:
            self.start_pos = start_pos.copy()
            self.end_pos = start_pos.copy()
            self.end_pos.advance()
            
        if end_pos:
            self.end_pos = end_pos.copy()
            
    def matches(self, type_, value):
        return self.type == type_ and self.value == value
        
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'