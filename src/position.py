class TextPosition:
    def __init__(self, index, line, column, filename, filetext):
        self.index = index
        self.line = line
        self.column = column
        self.filename = filename
        self.filetext = filetext
        
    def advance(self, current_char=None):
        self.index += 1
        self.column += 1
        
        if current_char == '\n':
            self.line += 1
            self.column = 0
            
        return self
        
    def copy(self):
        return TextPosition(self.index, self.line, self.column, self.filename, self.filetext)