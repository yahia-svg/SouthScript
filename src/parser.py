from .nodes import *
from .tokens import Token
from .errors import SyntaxIssue
from .constants import *

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.step_count = 0
        
    def record_step(self):
        self.step_count += 1
        
    def record_result(self, res):
        self.last_step_count = res.step_count
        self.step_count += res.step_count
        if res.error: self.error = res.error
        return res.node
        
    def success(self, node):
        self.node = node
        return self
        
    def failure(self, error):
        if not self.error or self.step_count == 0:
            self.error = error
        return self

class CodeParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.current_token = None
        self.advance()
        self.start_pos = None
        self.end_pos = None
        
    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token
        
    def parse(self):
        result = self.parse_expression()
        if not result.error and self.current_token.type != TT_EOF:
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected number, text, name, '+', '-', '(', '[', 'RECKON', 'TROT', 'WHILES', 'FIXIN''"
            ))
        return result
        
    def parse_logical(self):
        result = ParseResult()
        left = result.record_result(self.parse_comparison())
        if result.error: return result

        while (self.current_token.matches(TT_KEYWORD, 'AN\'') or 
            self.current_token.matches(TT_KEYWORD, 'OR')):
            op_token = self.current_token
            result.record_step()
            self.advance()
            right = result.record_result(self.parse_comparison())
            if result.error: return result
            left = BinaryOperationNode(left, op_token, right)

        return result.success(left)

    def parse_expression(self):
        result = ParseResult()
        
        if self.current_token.matches(TT_KEYWORD, 'THANG'):
            result.record_step()
            self.advance()
            
            if self.current_token.type != TT_IDENTIFIER:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected name"
                ))
                
            name_token = self.current_token
            result.record_step()
            self.advance()
            
            if self.current_token.type != TT_EQ:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected '='"
                ))
                
            result.record_step()
            self.advance()
            expr = result.record_result(self.parse_expression())
            if result.error: return result
            return result.success(VariableAssignmentNode(name_token, expr))
            
        node = result.record_result(self.parse_logical())  # Changed from parse_comparison()
        
        if result.error:
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected 'THANG','RECKON','TROT','WHILES','FIXIN'', number, text, name, '+', '-' '(' '[' or 'AIN\'T'"
            ))
            
        return result.success(node)
        
    def parse_function_call(self):
        result = ParseResult()
        atom = result.record_result(self.parse_atom())
        if result.error: return result

        if self.current_token.type == TT_LPAREN:
            result.record_step()
            self.advance()
            arguments = []

            if self.current_token.type == TT_RPAREN:
                result.record_step()
                self.advance()
            else:
                arguments.append(result.record_result(self.parse_expression()))
                if result.error:
                    return result.failure(SyntaxIssue(
                        self.current_token.start_pos, self.current_token.end_pos,
                        "Expected ')', 'THANG', 'RECKON', 'TROT', 'WHILES', 'FIXIN'', number, text, name, '+', '-', '(', '[' or 'AIN’T'"
                    ))
                    
                while self.current_token.type == TT_COMMA:
                    result.record_step()
                    self.advance()
                    arguments.append(result.record_result(self.parse_expression()))
                    if result.error: return result
                    
                if self.current_token.type != TT_RPAREN:
                    return result.failure(SyntaxIssue(
                        self.current_token.start_pos, self.current_token.end_pos,
                        f"Expected ',' or ')'"
                    ))
                    
                result.record_step()
                self.advance()
                
            return result.success(FunctionCallNode(atom, arguments))
        return result.success(atom)
        
    def parse_atom(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_INT, TT_FLOAT):
            result.record_step()
            self.advance()
            return result.success(NumericLiteralNode(token))
            
        elif token.type == TT_STRING:
            result.record_step()
            self.advance()
            return result.success(TextLiteralNode(token))

        elif token.type == TT_IDENTIFIER:
            result.record_step()
            self.advance()
            return result.success(VariableAccessNode(token))

        elif token.type == TT_LPAREN:
            result.record_step()
            self.advance()
            expr = result.record_result(self.parse_expression())
            if result.error: return result
            
            if self.current_token.type == TT_RPAREN:
                result.record_step()
                self.advance()
                return result.success(expr)
            else:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected ')'"
                ))
                
        elif token.type == TT_LSQUARE:
            list_expr = result.record_result(self.parse_list())
            if result.error: return result
            return result.success(list_expr)
            
        elif token.matches(TT_KEYWORD, 'RECKON'):
            if_expr = result.record_result(self.parse_conditional())
            if result.error: return result
            return result.success(if_expr)
            
        elif token.matches(TT_KEYWORD, 'TROT'):
            for_expr = result.record_result(self.parse_loop())
            if result.error: return result
            return result.success(for_expr)
            
        elif token.matches(TT_KEYWORD, 'WHILES'):
            while_expr = result.record_result(self.parse_while_loop())
            if result.error: return result
            return result.success(while_expr)
            
        elif token.matches(TT_KEYWORD, 'FIXIN\''):
            func_def = result.record_result(self.parse_function_definition())
            if result.error: return result
            return result.success(func_def)
            
        return result.failure(SyntaxIssue(
            token.start_pos, token.end_pos,
            "Expected number, text, name, '+', '-', '(', 'RECKON', 'TROT','WHILES','FIXIN''"
        ))
        
    def parse_list(self):
        result = ParseResult()
        elements = []
        start_pos = self.current_token.start_pos.copy()
        
        if self.current_token.type != TT_LSQUARE:
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected '['"
            ))
            
        result.record_step()
        self.advance()
        
        if self.current_token.type == TT_RSQUARE:
            result.record_step()
            self.advance()
        else:
            elements.append(result.record_result(self.parse_expression()))
            if result.error:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    "Expected ']', 'THANG', 'RECKON', 'TROT', 'WHILES', 'FIXIN'', number, text, name, '+', '-', '(', '[' or 'AIN’T'"
                ))
                
            while self.current_token.type == TT_COMMA:
                result.record_step()
                self.advance()
                elements.append(result.record_result(self.parse_expression()))
                if result.error: return result
                
            if self.current_token.type != TT_RSQUARE:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected ',' or ']'"
                ))
                
            result.record_step()
            self.advance()
            
        return result.success(CollectionNode(
            elements,
            start_pos,
            self.current_token.end_pos.copy()
        ))
        
    def parse_conditional(self):
        result = ParseResult()
        cases = []
        default_case = None

        if not self.current_token.matches(TT_KEYWORD, 'RECKON'):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'RECKON'"
            ))
        
        result.record_step()
        self.advance()
        
        condition = result.record_result(self.parse_expression())
        if result.error: return result
        
        if not self.current_token.matches(TT_KEYWORD, 'THEN'):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'THEN'"
            ))
        
        result.record_step()
        self.advance()
        expr = result.record_result(self.parse_expression())
        if result.error: return result
        cases.append((condition, expr))
        
        while self.current_token.matches(TT_KEYWORD, 'MIGHTCOULD'):
            result.record_step()
            self.advance()
            condition = result.record_result(self.parse_expression())
            if result.error: return result
            
            if not self.current_token.matches(TT_KEYWORD, 'THEN'):
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected 'THEN'"
                ))
                
            result.record_step()
            self.advance()
            expr = result.record_result(self.parse_expression())
            if result.error: return result
            cases.append((condition, expr))
            
        if self.current_token.matches(TT_KEYWORD, 'ELSE'):
            result.record_step()
            self.advance()
            expr = result.record_result(self.parse_expression())
            if result.error: return result
            default_case = expr
            
        return result.success(ConditionalNode(cases, default_case))
        
    def parse_loop(self):
        result = ParseResult()
        
        if not self.current_token.matches(TT_KEYWORD, 'TROT'):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'TROT'"
            ))
            
        result.record_step()
        self.advance()
        
        if self.current_token.type != TT_IDENTIFIER:
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected variable name"
            ))
            
        var_token = self.current_token
        result.record_step()
        self.advance()
        
        if self.current_token.type != TT_EQ:
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected '='"
            ))
            
        result.record_step()
        self.advance()
        start_val = result.record_result(self.parse_expression())
        if result.error: return result
        
        if not self.current_token.matches(TT_KEYWORD, "T'"):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'T''"
            ))
            
        result.record_step()
        self.advance()
        end_val = result.record_result(self.parse_expression())
        if result.error: return result
        
        if self.current_token.matches(TT_KEYWORD, 'BY_A_PEICE'):
            result.record_step()
            self.advance()
            step_val = result.record_result(self.parse_expression())
            if result.error: return result
        else:
            step_val = None
            
        if not self.current_token.matches(TT_KEYWORD, 'THEN'):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'THEN'"
            ))
            
        result.record_step()
        self.advance()
        body = result.record_result(self.parse_expression())
        if result.error: return result
        
        return result.success(LoopNode(
            var_token,    
            start_val,    
            end_val,     
            step_val,     
            body          
        ))
    def parse_while_loop(self):
        result = ParseResult()
        
        if not self.current_token.matches(TT_KEYWORD, 'WHILES'):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'WHILES'"
            ))
            
        result.record_step()
        self.advance()
        condition = result.record_result(self.parse_expression())
        if result.error: return result
        
        if not self.current_token.matches(TT_KEYWORD, 'THEN'):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'THEN'"
            ))
            
        result.record_step()
        self.advance()
        body_nodes = []
        while (self.current_token.type != TT_EOF and 
            not self.current_token.matches(TT_KEYWORD, 'WHILES') and
            not self.current_token.matches(TT_KEYWORD, 'RECKON') and
            not self.current_token.matches(TT_KEYWORD, 'TROT')):
            body_node = result.record_result(self.parse_expression())
            if result.error: return result
            body_nodes.append(body_node)
            if self.current_token.type == TT_COMMA:
                result.record_step()
                self.advance()
        if len(body_nodes) > 1:
            body = CollectionNode(body_nodes, body_nodes[0].start_pos, body_nodes[-1].end_pos)
        else:
            body = body_nodes[0] if body_nodes else None
            
        return result.success(WhileLoopNode(condition, body))
    def parse_factor(self):
        result = ParseResult()
        token = self.current_token

        if token.type in (TT_PLUS, TT_MINUS):
            result.record_step()
            self.advance()
            factor = result.record_result(self.parse_factor())
            if result.error: return result
            return result.success(UnaryOperationNode(token, factor))
            
        return self.parse_function_call()
        
    def parse_term(self):
        return self.binary_operation(self.parse_factor, (TT_MUL, TT_DIV))
        
    def parse_arithmetic(self):
        return self.binary_operation(self.parse_term, (TT_PLUS, TT_MINUS))
        
    def parse_comparison(self):
        result = ParseResult()
        if self.current_token.matches(TT_KEYWORD, 'AIN\'T'):
            op_token = self.current_token
            result.record_step()
            self.advance()
            expr = result.record_result(self.parse_comparison())
            if result.error: return result
            
            return result.success(UnaryOperationNode(op_token, expr))
        node = result.record_result(self.binary_operation(
            self.parse_arithmetic, 
            (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)
        ))
        
        if result.error:
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                "Expected number, text, name, '+', '-', '(', '[' or 'AIN\'T'"
            ))
        
        return result.success(node)        
    def parse_function_definition(self):
        result = ParseResult()

        if not self.current_token.matches(TT_KEYWORD, 'FIXIN\''):
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected 'FIXIN''"
            ))

        result.record_step()
        self.advance()

        if self.current_token.type == TT_IDENTIFIER:
            func_name_token = self.current_token
            result.record_step()
            self.advance()
            if self.current_token.type != TT_LPAREN:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected '('"
                ))
        else:
            func_name_token = None
            if self.current_token.type != TT_LPAREN:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected name or '('"
                ))
        
        result.record_step()
        self.advance()
        param_names = []

        if self.current_token.type == TT_IDENTIFIER:
            param_names.append(self.current_token)
            result.record_step()
            self.advance()
            
            while self.current_token.type == TT_COMMA:
                result.record_step()
                self.advance()

                if self.current_token.type != TT_IDENTIFIER:
                    return result.failure(SyntaxIssue(
                        self.current_token.start_pos, self.current_token.end_pos,
                        f"Expected name"
                    ))

                param_names.append(self.current_token)
                result.record_step()
                self.advance()
            
            if self.current_token.type != TT_RPAREN:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_token.type != TT_RPAREN:
                return result.failure(SyntaxIssue(
                    self.current_token.start_pos, self.current_token.end_pos,
                    f"Expected name or ')'"
                ))

        result.record_step()
        self.advance()

        if self.current_token.type != TT_ARROW:
            return result.failure(SyntaxIssue(
                self.current_token.start_pos, self.current_token.end_pos,
                f"Expected '->'"
            ))

        result.record_step()
        self.advance()
        return_expr = result.record_result(self.parse_expression())
        if result.error: return result

        return result.success(FunctionDefinitionNode(
            func_name_token,
            param_names,
            return_expr
        ))
        
    def binary_operation(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
            
        result = ParseResult()
        left = result.record_result(func_a())
        if result.error: return result
        
        while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
            op_token = self.current_token
            result.record_step()
            self.advance()
            right = result.record_result(func_b())
            if result.error: return result
            left = BinaryOperationNode(left, op_token, right)
            
        return result.success(left)