from .tokens import Token
from .position import TextPosition

class NumericLiteralNode:
    def __init__(self, token):
        self.token = token
        self.start_pos = self.token.start_pos
        self.end_pos = self.token.end_pos
        
    def __repr__(self):
        return f'{self.token}'

class TextLiteralNode:
    def __init__(self, token):
        self.token = token
        self.start_pos = self.token.start_pos
        self.end_pos = self.token.end_pos
        
    def __repr__(self):
        return f'{self.token}'

class CollectionNode:
    def __init__(self, items, start_pos, end_pos):
        self.items = items
        self.start_pos = start_pos
        self.end_pos = end_pos

class VariableAccessNode:
    def __init__(self, token):
        self.token = token
        self.start_pos = self.token.start_pos
        self.end_pos = self.token.end_pos

class VariableAssignmentNode:
    def __init__(self, token, value_node):
        self.token = token
        self.value_node = value_node
        self.start_pos = self.token.start_pos
        self.end_pos = self.value_node.end_pos

class BinaryOperationNode:
    def __init__(self, left_node, op_token, right_node):
        self.left_node = left_node
        self.op_token = op_token
        self.right_node = right_node
        self.start_pos = self.left_node.start_pos
        self.end_pos = self.right_node.end_pos
        
    def __repr__(self):
        return f'({self.left_node},{self.op_token},{self.right_node})'

class UnaryOperationNode:
    def __init__(self, op_token, node):
        self.op_token = op_token
        self.node = node
        self.start_pos = self.op_token.start_pos
        self.end_pos = node.end_pos
        
    def __repr__(self):
        return f'({self.op_token}, {self.node})'

class ConditionalNode:
    def __init__(self, cases, default_case):
        self.cases = cases
        self.default_case = default_case
        self.start_pos = self.cases[0][0].start_pos
        self.end_pos = (self.default_case or self.cases[-1][0]).end_pos

class LoopNode:
    def __init__(self, var_token, start_value, end_value, step_value, body):
        self.var_token = var_token
        self.start_value = start_value
        self.end_value = end_value
        self.step_value = step_value
        self.body = body
        self.start_pos = self.var_token.start_pos
        self.end_pos = self.body.end_pos
    def __repr__(self):
        step_str = f", step={self.step_value}" if self.step_value else ""
        return f"(Loop: {self.var_token.value} from {self.start_value} to {self.end_value}{step_str} do {self.body})"


class WhileLoopNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
        self.start_pos = self.condition.start_pos
        self.end_pos = self.body.end_pos

class FunctionDefinitionNode:
    def __init__(self, func_name_token, param_tokens, body_node):
        self.func_name_token = func_name_token
        self.param_tokens = param_tokens
        self.body_node = body_node
        
        if self.func_name_token:
            self.start_pos = self.func_name_token.start_pos
        elif self.param_tokens:
            self.start_pos = self.param_tokens[0].start_pos
        else:
            self.start_pos = self.body_node.start_pos
            
        self.end_pos = self.body_node.end_pos

class FunctionCallNode:
    def __init__(self, func_node, arg_nodes):
        self.func_node = func_node
        self.arg_nodes = arg_nodes
        self.start_pos = self.func_node.start_pos
        
        if self.arg_nodes:
            self.end_pos = self.arg_nodes[-1].end_pos
        else:
            self.end_pos = self.func_node.end_pos