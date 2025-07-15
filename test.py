from interpreter.init import execute, setup_global_symbols
from interpreter.context import ExecutionContext
from interpreter.symbol_table import SymbolStorage
from interpreter.values import Collection

global_symbols = setup_global_symbols()
main_context = ExecutionContext('<repl>')
main_context.symbol_storage = SymbolStorage(global_symbols)

while True:
    try:
        code = input('SouthScript > ').strip()
        if not code:
            continue
            
        outcome, issue = execute('<stdin>', code, main_context)
        
        if issue:
            print(issue.display_error())
        elif outcome is not None and not isinstance(outcome, Collection):
            print(outcome)
            
    except KeyboardInterrupt:
        print("\nQuittin'")
        break
    except Exception as e:
        print(f"Whoops, something broke: {e}")