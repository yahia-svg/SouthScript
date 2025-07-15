from .runtime_result import RuntimeResult
from .errors import RuntimeIssue
from .values import TextValue, NumericValue

class ScriptExecutor:
    def __init__(self):
        self.start_pos = None
        self.end_pos = None
        self.context = None
        
    def set_position(self, start_pos=None, end_pos=None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        return self
        
    def set_context(self, context=None):
        self.context = context
        return self
        
    def execute(self, args):
        from .init import execute
        
        result = RuntimeResult()
        if not hasattr(self, 'context') or not self.context:
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                "No execution context available",
                None
            ))
            
        if len(args) != 1 or not isinstance(args[0], TextValue):
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                "Expected single text argument",
                self.context
            ))
            
        filename = args[0].value
        try:
            with open(filename, "r") as f:
                script = f.read()
        except Exception as e:
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                f"Failed to load script '{filename}': {str(e)}",
                self.context
            ))
            
        _, error = execute(filename, script, self.context)
        if error:
            return result.failure(RuntimeIssue(
                self.start_pos, self.end_pos,
                f"Script execution failed:\n{error.display_error()}",
                self.context
            ))
            
        return result.success(NumericValue.zero)
    
    def copy(self):
        copy = ScriptExecutor()
        copy.set_context(self.context)
        copy.set_position(self.start_pos, self.end_pos)
        return copy
    
    @property
    def arg_names(self):
        return ["filename"]