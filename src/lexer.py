from .tokens import Token
from .errors import BadCharacterError, MissingCharacterError
from .position import TextPosition
from .constants import *

class TokenMaker:
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text
        self.position = TextPosition(-1, 0, -1, filename, text)
        self.current_char = None
        self.move_next()

    def move_next(self):
        self.position.advance(self.current_char)
        self.current_char = self.text[self.position.index] if self.position.index < len(self.text) else None
    
    def generate_tokens(self):
        token_list = []
        
        while self.current_char is not None:
            if self.current_char in ' \t':
                self.move_next()
            elif self.current_char == '#':
                self.skip_comment()
            elif self.current_char in DIGITS:
                token_list.append(self.create_number())
            elif self.current_char in LETTERS:
                token_list.append(self.create_identifier())
            elif self.current_char == '"':
                token_list.append(self.create_string())
            elif self.current_char == '+':
                token_list.append(Token(TT_PLUS, start_pos=self.position))
                self.move_next()
            elif self.current_char == '-':
                token_list.append(self.create_minus_or_arrow())
            elif self.current_char == '*':
                token_list.append(Token(TT_MUL, start_pos=self.position))
                self.move_next()
            elif self.current_char == '/':
                token_list.append(Token(TT_DIV, start_pos=self.position))
                self.move_next()
            elif self.current_char == '(':
                token_list.append(Token(TT_LPAREN, start_pos=self.position))
                self.move_next()
            elif self.current_char == ')':
                token_list.append(Token(TT_RPAREN, start_pos=self.position))
                self.move_next()
            elif self.current_char == '[':
                token_list.append(Token(TT_LSQUARE, start_pos=self.position))
                self.move_next()
            elif self.current_char == ']':
                token_list.append(Token(TT_RSQUARE, start_pos=self.position))
                self.move_next()
            elif self.current_char == '!':
                token, issue = self.create_not_equals()
                if issue: return [], issue
                token_list.append(token)
            elif self.current_char == '=':
                token_list.append(self.create_equals())
            elif self.current_char == '<':
                token_list.append(self.create_less_than())
            elif self.current_char == '>':
                token_list.append(self.create_greater_than())
            elif self.current_char == ',':
                token_list.append(Token(TT_COMMA, start_pos=self.position))
                self.move_next()
            else:
                start_pos = self.position.copy()
                char = self.current_char
                self.move_next()
                return [], BadCharacterError(start_pos, self.position, "'" + char + "'")
        token_list.append(Token(TT_EOF, start_pos=self.position))
        return token_list, None
    
    def create_number(self):
        num_str = ''
        decimal_count = 0
        start_pos = self.position.copy()
        
        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if decimal_count == 1: break 
                decimal_count += 1 
                num_str += '.'
            else:
                num_str += self.current_char
            self.move_next()
            
        if decimal_count == 0:
            return Token(TT_INT, int(num_str), start_pos, self.position)
        else:
            return Token(TT_FLOAT, float(num_str), start_pos, self.position)
            
    def create_string(self):
        string_value = ''
        start_pos = self.position.copy()
        escaping = False
        self.move_next()
        
        escape_chars = {
            'n': '\n',
            't': '\t'
        }
        
        while self.current_char is not None and (self.current_char != '"' or escaping):
            if escaping:
                string_value += escape_chars.get(self.current_char, self.current_char)
            else:
                if self.current_char == '\\':
                    escaping = True
                else:
                    string_value += self.current_char
            self.move_next()
            escaping = False
            
        self.move_next()
        return Token(TT_STRING, string_value, start_pos, self.position)
        
    def create_identifier(self):
        name = ''
        start_pos = self.position.copy()

        if self.current_char == 'T' and self.peek() == "'":
            name = "T'"
            self.move_next()
            self.move_next()
            return Token(TT_KEYWORD, name, start_pos, self.position)

        while self.current_char is not None and self.current_char in LETTER_DIGITS + "_'":
            name += self.current_char
            self.move_next()
        
        token_type = TT_KEYWORD if name in KEYWORDS else TT_IDENTIFIER
        return Token(token_type, name, start_pos, self.position)

    def peek(self):
        """Look at next character without consuming it"""
        if self.position.index + 1 < len(self.text):
            return self.text[self.position.index + 1]
        return None
            
    def create_minus_or_arrow(self):
        token_type = TT_MINUS
        start_pos = self.position.copy()
        self.move_next()
        
        if self.current_char == '>':
            self.move_next()
            token_type = TT_ARROW
            
        return Token(token_type, start_pos=start_pos, end_pos=self.position)
        
    def create_not_equals(self):
        start_pos = self.position.copy()
        self.move_next()
        if self.current_char == '=':
            self.move_next()
            return Token(TT_NE, start_pos=start_pos, end_pos=self.position), None
            
        self.move_next()
        return None, MissingCharacterError(start_pos, self.position, "'=' after '!'")
        
    def create_equals(self):
        token_type = TT_EQ
        start_pos = self.position.copy()
        self.move_next()
        if self.current_char == '=':
            self.move_next()
            token_type = TT_EE
        return Token(token_type, start_pos=start_pos, end_pos=self.position)
        
    def create_less_than(self):
        token_type = TT_LT
        start_pos = self.position.copy()
        self.move_next()
        if self.current_char == '=':
            self.move_next()
            token_type = TT_LTE
        return Token(token_type, start_pos=start_pos, end_pos=self.position)
        
    def create_greater_than(self):
        token_type = TT_GT
        start_pos = self.position.copy()
        self.move_next()
        if self.current_char == '=':
            self.move_next()
            token_type = TT_GTE
        return Token(token_type, start_pos=start_pos, end_pos=self.position)
        
    def skip_comment(self):
        self.move_next()
        while self.current_char and self.current_char != '\n':
            self.move_next()  
        self.move_next()  
