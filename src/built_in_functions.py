from .values import BaseType, NumericValue, TextValue, Collection
from .runtime_result import RuntimeResult
from .errors import RuntimeIssue
from .context import ExecutionContext
from .symbol_table import SymbolStorage

class PredefinedFunction(BaseType):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def execute(self, args):
        result = RuntimeResult()
        method_name = f'run_{self.name}'
        method = getattr(self, method_name, self.no_method)
        
        if method == self.no_method:
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                f"No such built-in function: '{self.name}'",
                self.context
            ))
    
        if len(args) != len(method.arg_names):
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                f"Cattywampus! '{self.name}' wants {len(method.arg_names)} arguments but got {len(args)}",
                self.context
        ))
        exec_context = ExecutionContext(self.name, self.context, self.start_pos)
        exec_context.symbol_storage = SymbolStorage(self.context.symbol_storage)
        
        for i in range(len(args)):
            arg_name = method.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_context)
            exec_context.symbol_storage.add(arg_name, arg_value)
        
        method_result = method(exec_context)
        if method_result.error:
            return result.failure(method_result.error)
        return result.success(method_result.value)
    
    def no_method(self, node, context):
        raise Exception(f'No handler for {self.name}')
    
    def copy(self):
        copy = PredefinedFunction(self.name)
        copy.set_context(self.context)
        copy.set_position(self.start_pos, self.end_pos)
        return copy
    
    def __repr__(self):
        return f"<built-in function {self.name}>"
    
    def run_HOLLER(self, exec_context):
        value = exec_context.symbol_storage.get('value')
        print(str(value))
        return RuntimeResult().success(NumericValue.zero)
    run_HOLLER.arg_names = ['value']
    
    def run_SPEAKUP(self, exec_context):
        text = input()
        try:
            number = int(text)
            return RuntimeResult().success(NumericValue(number))
        except ValueError:
            try:
                number = float(text)
                return RuntimeResult().success(NumericValue(number))
            except ValueError:
                return RuntimeResult().success(TextValue(text))
    run_SPEAKUP.arg_names = []
    
    def run_SHOVE(self, exec_context):
        collection = exec_context.symbol_storage.get("collection")
        value = exec_context.symbol_storage.get("value")
        
        if not isinstance(collection, Collection):
            return RuntimeResult().failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                "First argument must be a collection",
                exec_context
            ))
            
        collection.elements.append(value)
        return RuntimeResult().success(NumericValue.zero)
    run_SHOVE.arg_names = ['collection', 'value']
    
    def run_YANK(self, exec_context):
        collection = exec_context.symbol_storage.get("collection")
        index = exec_context.symbol_storage.get("index")
        
        if not isinstance(collection, Collection):
            return RuntimeResult().failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                "First argument must be a collection",
                exec_context
            ))
            
        if not isinstance(index, NumericValue):
            return RuntimeResult().failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                "Second argument must be a number",
                exec_context
            ))
            
        try:
            value = collection.elements.pop(index.value)
            return RuntimeResult().success(value)
        except IndexError:
            return RuntimeResult().failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                f"Index {index.value} out of range",
                exec_context
            ))
    run_YANK.arg_names = ['collection', 'index']
    
    def run_STACKON(self, exec_context):
        collectionA = exec_context.symbol_storage.get("collectionA")
        collectionB = exec_context.symbol_storage.get("collectionB")
        
        if not isinstance(collectionA, Collection):
            return RuntimeResult().failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                "First argument must be a collection",
                exec_context
            ))
            
        if not isinstance(collectionB, Collection):
            return RuntimeResult().failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                "Second argument must be a collection",
                exec_context
            ))
            
        new_collection = Collection(collectionA.elements + collectionB.elements)
        return RuntimeResult().success(new_collection)
    run_STACKON.arg_names = ["collectionA", "collectionB"]