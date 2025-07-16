# SouthScript 🤠

**The most rootin'-tootin' programming language in the West!**

A Southern-themed programming language that combines coding with cowboy charm. Y'all ready to program?
Website: https://yahiaaa.pythonanywhere.com/
```southscript
# ===== VARIABLES =====
THANG x = 5                 # Number variable
THANG name = "Billy Bob"    # String variable
THANG is_cowboy = TRUE      # Boolean variable
THANG items = [1, "rope", TRUE]  # List variable

# ===== OPERATORS =====
THANG sum = 5 + 3           # Arithmetic: 5 + 3 = 8
THANG is_adult = age >= 18   # Comparison: TRUE if age ≥ 18
THANG ready = TRUE AN' AIN'T FALSE  # Logical: TRUE AND NOT FALSE

# ===== CONTROL FLOW =====
RECKON temp > 90 THEN               # IF statement
    HOLLER("Hotter than a pepper sprout!")
MIGHTCOULD temp > 70 THEN           # ELSE IF
    HOLLER("Pleasant as a peach")
ELSE                                # ELSE
    HOLLER("Colder than a well digger's toe")

# ===== LOOPS =====
TROT i = 1 T' 3 THEN                # FOR loop (1 to 3)
    HOLLER("Trot #" + i)

THANG count = 0
WHILES count < 3 THEN               # WHILE loop
    HOLLER("Count: " + count)
    count = count + 1

# ===== FUNCTIONS =====
FIXIN' drawl(text) ->               # Regular function
    HOLLER(text + ", y'all!")

THANG square = FIXIN'(n) -> n * n   # Anonymous function
drawl("Howdy")                      # Function call
HOLLER(square(4))                   # Prints 16

# ===== COLLECTIONS =====
THANG supplies = ["lasso", "hat"]
SHOVE(supplies, "boots")           # Add to list
THANG item = YANK(supplies, 0)      # Remove first item
THANG all = STACKON(supplies, ["saddle", "spurs"])  # Combine lists

# ===== BUILT-INS =====
HOLLER("Hello frontier!")          # Print output
THANG input = SPEAKUP()             # Get user input
FIREUP("other.ss")                 # Run another script

# ===== ERROR HANDLING =====
# Example runtime error message:
# "Cattywampus! Runtime Problem: 'x' ain't defined"
# "File example.ss, line 5, in <main>"
