from .runtime_result import RuntimeResult
from .values import NumericValue, TextValue, Collection
from .values import CustomFunction
from .errors import RuntimeIssue
from .constants import *

class CodeRunner:
    def evaluate(self, node, context):
        method_name = f'process_{type(node).__name__}'
        method = getattr(self, method_name, self.no_method_found)
        return method(node, context)
        
    def no_method_found(self, node, context):
        raise Exception(f'No handler for {type(node).__name__}')
    
    def process_NumericLiteralNode(self, node, context):
        return RuntimeResult().success(
            NumericValue(node.token.value)
            .set_context(context)
            .set_position(node.start_pos, node.end_pos)
        )
        
    def process_TextLiteralNode(self, node, context):
        return RuntimeResult().success(
            TextValue(node.token.value)
            .set_context(context)
            .set_position(node.start_pos, node.end_pos)
        )
        
    def process_CollectionNode(self, node, context):
        result = RuntimeResult()
        items = []
        
        for item_node in node.items:
            items.append(result.record(self.evaluate(item_node, context)))
            if result.error: return result
            
        return result.success(
            Collection(items)
            .set_context(context)
            .set_position(node.start_pos, node.end_pos)
        )
        
    def process_VariableAccessNode(self, node, context):
        result = RuntimeResult()
        var_name = node.token.value
        value = context.symbol_storage.get(var_name)
        
        if not value:
            return result.failure(RuntimeIssue(
                node.start_pos, node.end_pos,
                f"'{var_name}' ain't defined",
                context
            ))
        return result.success(value.copy().set_position(node.start_pos, node.end_pos).set_context(context))
        
    def process_VariableAssignmentNode(self, node, context):
        result = RuntimeResult()
        var_name = node.token.value
        value = result.record(self.evaluate(node.value_node, context))
        if result.error: return result
        context.symbol_storage.add(var_name, value.copy())
        return result.success(value)
        
    def process_BinaryOperationNode(self, node, context):
        result = RuntimeResult()
        left = result.record(self.evaluate(node.left_node, context))
        if result.error: return result
        
        right = result.record(self.evaluate(node.right_node, context))
        if result.error: return result

        if node.op_token.type == TT_PLUS:
            outcome, issue = left.add(right)
        elif node.op_token.type == TT_MINUS:
            outcome, issue = left.subtract(right)
        elif node.op_token.type == TT_MUL:
            outcome, issue = left.multiply(right)
        elif node.op_token.type == TT_DIV:
            outcome, issue = left.divide(right)
        elif node.op_token.type == TT_EE:
            outcome, issue = left.compare_equal(right)
        elif node.op_token.type == TT_NE:
            outcome, issue = left.compare_not_equal(right)
        elif node.op_token.type == TT_LT:
            outcome, issue = left.compare_less_than(right)
        elif node.op_token.type == TT_GT:
            outcome, issue = left.compare_greater_than(right)
        elif node.op_token.type == TT_LTE:
            outcome, issue = left.compare_less_or_equal(right)
        elif node.op_token.type == TT_GTE:
            outcome, issue = left.compare_greater_or_equal(right)
        elif node.op_token.matches(TT_KEYWORD, 'AN\''):
            outcome, issue = left.logical_and(right)
        elif node.op_token.matches(TT_KEYWORD, 'OR'):
            outcome, issue = left.logical_or(right)
        else:
            return result.failure(RuntimeIssue(
                node.start_pos, node.end_pos,
                f"Unknown operator: {node.op_token}",
                context
            ))
            
        if issue:
            return result.failure(issue)
        else:
            return result.success(outcome.set_position(node.start_pos, node.end_pos))            
    def process_UnaryOperationNode(self, node, context):
        result = RuntimeResult()
        number = result.record(self.evaluate(node.node, context))
        if result.error: return result
        
        issue = None
        if node.op_token.type == TT_MINUS:
            number, issue = number.multiply(NumericValue(-1))
        elif node.op_token.matches(TT_KEYWORD, 'AIN\'T'):
            number, issue = number.logical_not()
            
        if issue:
            return result.failure(issue)
        else:
            return result.success(number.set_position(node.start_pos, node.end_pos))
            
    def process_ConditionalNode(self, node, context):
        result = RuntimeResult()
        
        for condition, expr in node.cases:
            condition_value = result.record(self.evaluate(condition, context))
            if result.error: return result
            
            if condition_value.is_true():
                expr_value = result.record(self.evaluate(expr, context))
                if result.error: return result
                return result.success(expr_value)
                
        if node.default_case:
            default_value = result.record(self.evaluate(node.default_case, context))
            if result.error: return result
            return result.success(default_value)
            
        return result.success(None)
        
    def process_LoopNode(self, node, context):
        result = RuntimeResult()
        items = []
        start_val = result.record(self.evaluate(node.start_value, context))
        if result.error: return result
        
        end_val = result.record(self.evaluate(node.end_value, context))
        if result.error: return result
        
        step_val = (result.record(self.evaluate(node.step_value, context)) 
                if node.step_value else NumericValue(1))
        if result.error: return result
        
        if step_val.value == 0:
            return result.failure(RuntimeIssue(
                node.start_pos, node.end_pos,
                "Step value cannot be zero",
                context
            ))
        
        current = start_val.value
        
        def should_continue():
            return (current <= end_val.value) if step_val.value > 0 else (current >= end_val.value)
        
        while should_continue():
            context.symbol_storage.add(node.var_token.value, NumericValue(current))
            value = result.record(self.evaluate(node.body, context))
            if result.error: return result
            items.append(value)
            current += step_val.value
        return result.success(
            Collection(items)
            .set_context(context)
            .set_position(node.start_pos, node.end_pos)
        )
    
    def process_WhileLoopNode(self, node, context):
        result = RuntimeResult()
        items = []
        
        while True:
            condition = result.record(self.evaluate(node.condition, context))
            if result.error: return result
            if not condition.is_true(): break
            items.append(result.record(self.evaluate(node.body, context)))
            if result.error: return result
        return result.success(
        Collection(items) if items else Collection([])
        .set_context(context)
        .set_position(node.start_pos, node.end_pos)
        )   

    def process_FunctionDefinitionNode(self, node, context):
        result = RuntimeResult()
        func_name = node.func_name_token.value if node.func_name_token else None
        param_names = [param.value for param in node.param_tokens]
        
        func_value = CustomFunction(func_name, node.body_node, param_names)
        func_value.set_context(context)
        func_value.set_position(node.start_pos, node.end_pos)
        
        if node.func_name_token:
            context.symbol_storage.add(func_name, func_value)
            
        return result.success(func_value)
        
    def process_FunctionCallNode(self, node, context):
        result = RuntimeResult()
        args = []
        
        func_to_call = result.record(self.evaluate(node.func_node, context))
        if result.error: return result
        
        func_to_call = func_to_call.copy().set_position(node.start_pos, node.end_pos)
        
        for arg_node in node.arg_nodes:
            args.append(result.record(self.evaluate(arg_node, context)))
            if result.error: return result
            
        return_value = result.record(func_to_call.execute(args))
        if result.error: return result
        
        return_value = return_value.copy().set_position(node.start_pos, node.end_pos).set_context(context)
        return result.success(return_value)