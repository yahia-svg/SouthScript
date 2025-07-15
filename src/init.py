from .lexer import TokenMaker
from .parser import CodeParser
from .interpreter import CodeRunner
from .context import ExecutionContext
from .symbol_table import SymbolStorage
from .values import NumericValue
from .built_in_functions import PredefinedFunction
from .run_function import ScriptExecutor

def setup_global_symbols():
    storage = SymbolStorage()
    storage.add("NULL", NumericValue.zero)
    storage.add("TRUE", NumericValue.true)
    storage.add("FALSE", NumericValue.false)
    storage.add("HOLLER", PredefinedFunction("HOLLER"))
    storage.add("SPEAKUP", PredefinedFunction("SPEAKUP"))
    storage.add("SHOVE", PredefinedFunction("SHOVE"))
    storage.add("YANK", PredefinedFunction("YANK"))
    storage.add("STACKON", PredefinedFunction("STACKON"))
    storage.add("FIREUP", ScriptExecutor())
    
    return storage

def execute(filename, source_code, context=None):
    if context is None:
        symbols = setup_global_symbols()
        context = ExecutionContext('<main>')
        context.symbol_storage = symbols
    tokenizer = TokenMaker(filename, source_code)
    tokens, issue = tokenizer.generate_tokens()
    if issue: return None, issue
    parser = CodeParser(tokens)
    syntax_tree = parser.parse()
    if syntax_tree.error: return None, syntax_tree.error
    runner = CodeRunner()
    final_result = runner.evaluate(syntax_tree.node, context)
    return final_result.value, final_result.error