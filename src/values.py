from .runtime_result import RuntimeResult
from .errors import RuntimeIssue
from .context import ExecutionContext
from .symbol_table import SymbolStorage

class BaseType:
    def __init__(self):
        self.set_position()
        self.set_context()
        
    def set_position(self, start_pos=None, end_pos=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        return self
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def add(self, other):
        return None, self.invalid_operation(other)
        
    def subtract(self, other):
        return None, self.invalid_operation(other)
        
    def multiply(self, other):
        return None, self.invalid_operation(other)
        
    def divide(self, other):
        return None, self.invalid_operation(other)
        
    def compare_equal(self, other):
        return None, self.invalid_operation(other)
        
    def compare_not_equal(self, other):
        return None, self.invalid_operation(other)
        
    def compare_less_than(self, other):
        return None, self.invalid_operation(other)
        
    def compare_greater_than(self, other):
        return None, self.invalid_operation(other)
        
    def compare_less_or_equal(self, other):
        return None, self.invalid_operation(other)
        
    def compare_greater_or_equal(self, other):
        return None, self.invalid_operation(other)
        
    def logical_and(self, other):
        return None, self.invalid_operation(other)
        
    def logical_or(self, other):
        return None, self.invalid_operation(other)
        
    def logical_not(self):
        return None, self.invalid_operation()
        
    def execute(self, args):
        return None, self.invalid_operation()
        
    def is_true(self):
        return False
        
    def copy(self):
        raise Exception('No copy method defined')
        
    def invalid_operation(self, other=None):
        if not other: other = self
        return RuntimeIssue(
            self.start_pos, other.end_pos,
            'Cattywampus! Invalid operation',
            self.context
        )

class NumericValue(BaseType):
    def __init__(self, value):
        super().__init__()
        self.value = value
        
    def add(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value + other.value).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def subtract(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value - other.value).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def multiply(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(self.value * other.value).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def divide(self, other):
        if isinstance(other, NumericValue):
            if other.value == 0:
                return None, RuntimeIssue(
                    other.start_pos, other.end_pos,
                    "Division by zero",
                    self.context
                )
            return NumericValue(self.value / other.value).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def compare_equal(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value == other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def compare_not_equal(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value != other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def compare_less_than(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value < other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def compare_greater_than(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value > other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def compare_less_or_equal(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value <= other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def compare_greater_or_equal(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value >= other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def logical_and(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value and other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def logical_or(self, other):
        if isinstance(other, NumericValue):
            return NumericValue(int(self.value or other.value)).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def logical_not(self):
        return NumericValue(1 if self.value == 0 else 0).set_context(self.context), None
        
    def copy(self):
        copy = NumericValue(self.value)
        copy.set_position(self.start_pos, self.end_pos)
        copy.set_context(self.context)
        return copy
        
    def is_true(self):
        return self.value != 0
        
    def __str__(self):
        return str(self.value)
        
    def __repr__(self):
        return str(self.value)

class TextValue(BaseType):
    def __init__(self, value):
        super().__init__()
        self.value = value
        
    def add(self, other):
        if isinstance(other, TextValue):
            return TextValue(self.value + other.value).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def multiply(self, other):
        if isinstance(other, NumericValue):
            return TextValue(self.value * other.value).set_context(self.context), None
        else:
            return None, self.invalid_operation(other)
            
    def is_true(self):
        return len(self.value) > 0
        
    def copy(self):
        copy = TextValue(self.value)
        copy.set_position(self.start_pos, self.end_pos)
        copy.set_context(self.context)
        return copy
        
    def __str__(self):
        return self.value
        
    def __repr__(self):
        return f'"{self.value}"'

class Collection(BaseType):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        
    def add(self, other):
        new_collection = self.copy()
        new_collection.elements.append(other)
        return new_collection, None
        
    def subtract(self, other):
        if isinstance(other, NumericValue):
            new_collection = self.copy()
            try:
                new_collection.elements.pop(other.value)
                return new_collection, None
            except:
                return None, RuntimeIssue(
                    other.start_pos, other.end_pos,
                    'Cattywampus! Index out of bounds',
                    self.context
                )
        else:
            return None, self.invalid_operation(other)
            
    def multiply(self, other):
        if isinstance(other, Collection):
            new_collection = self.copy()
            new_collection.elements.extend(other.elements)
            return new_collection, None
        else:
            return None, self.invalid_operation(other)
            
    def divide(self, other):
        if isinstance(other, NumericValue):
            try:
                return self.elements[other.value], None
            except:
                return None, RuntimeIssue(
                    other.start_pos, other.end_pos,
                    'Cattywampus! Index out of bounds',
                    self.context
                )
        else:
            return None, self.invalid_operation(other)
            
    def copy(self):
        copy = Collection(self.elements)
        copy.set_position(self.start_pos, self.end_pos)
        copy.set_context(self.context)
        return copy
        
    def __str__(self):
        return '[' + ', '.join(map(str, self.elements)) + ']'
        
    def __repr__(self):
        return '[' + ', '.join(map(repr, self.elements)) + ']'

class CustomFunction(BaseType):
    def __init__(self, name, body_node, param_names):
        super().__init__()
        self.name = name or "<anonymous>"
        self.body_node = body_node
        self.param_names = param_names
    
    def execute(self, args):
        from .interpreter import CodeRunner
        
        result = RuntimeResult()
        runner = CodeRunner()
        exec_context = self.create_context()
        
        result.record(self.check_and_populate_args(self.param_names, args, exec_context))
        if result.error: 
            return result
        
        value = result.record(runner.evaluate(self.body_node, exec_context))
        if result.error: 
            return result
        
        return result.success(value)
    
    def create_context(self):
        new_context = ExecutionContext(self.name, self.context, self.start_pos)
        new_context.symbol_storage = SymbolStorage(new_context.parent.symbol_storage)
        return new_context
    
    def check_and_populate_args(self, param_names, args, context):
        result = RuntimeResult()

        if len(args) > len(param_names):
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                f"Too many arguments passed to '{self.name}'",
                self.context
            ))
        if len(args) < len(param_names):
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                f"Too few arguments passed to '{self.name}'",
                self.context
            ))
        

        for i in range(len(args)):
            arg_name = param_names[i].value if hasattr(param_names[i], 'value') else param_names[i]
            arg_value = args[i]
            arg_value.set_context(context)
            context.symbol_storage.add(arg_name, arg_value)
        
        return result.success(None)
    
    def copy(self):
        copy = CustomFunction(self.name, self.body_node, self.param_names)
        copy.set_context(self.context)
        copy.set_position(self.start_pos, self.end_pos)
        return copy
    
    def __repr__(self):
        return f"<function {self.name}>"

NumericValue.zero = NumericValue(0)
NumericValue.false = NumericValue(0)
NumericValue.true = NumericValue(1)