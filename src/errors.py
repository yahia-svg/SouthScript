from .position import TextPosition
class Issue:
    def __init__(self, start_pos, end_pos, issue_type, details):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.issue_type = issue_type
        self.details = details
        
    def display_error(self):
        result = f'Cattywampus! {self.issue_type}: {self.details}\n'
        result += f'File {self.start_pos.filename}, line {self.start_pos.line + 1}'
        return result

class BadCharacterError(Issue):
    def __init__(self, start_pos, end_pos, details):
        super().__init__(start_pos, end_pos, 'Bad Character', details)

class MissingCharacterError(Issue):
    def __init__(self, start_pos, end_pos, details):
        super().__init__(start_pos, end_pos, 'Missing Character', details)

class SyntaxIssue(Issue):
    def __init__(self, start_pos, end_pos, details=''):
        super().__init__(start_pos, end_pos, 'Syntax Problem', details)

class RuntimeIssue(Issue):
    def __init__(self, start_pos, end_pos, details, context):
        super().__init__(start_pos, end_pos, 'Runtime Problem', details)
        self.context = context
        
    def display_error(self):
        result = self.generate_traceback()
        result += f'Cattywampus! {self.issue_type}: {self.details}'
        return result
        
    def generate_traceback(self):
        result = ''
        pos = self.start_pos
        ctx = self.context
        
        while ctx:
            result = f'File {pos.filename}, line {pos.line + 1}, in {ctx.name}\n' + result
            pos = ctx.entry_pos
            ctx = ctx.parent
            
        return result