# Role: cleaner

## CC Reduction in Python — BoolOp/IfExp Branch Points

When reducing cyclomatic complexity using `or`/`and` (BoolOp) or ternary `if/else` (IfExp) in Python, verify the CC score with crap4py BEFORE committing — each BoolOp and IfExp adds a branch point to CC. A refactor that looks simpler can leave CC unchanged or higher. (cleaner e8692053)
