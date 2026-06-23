# Role: cleaner

## CC Reduction in Python — BoolOp/IfExp Branch Points

When reducing cyclomatic complexity using `or`/`and` (BoolOp) or ternary `if/else` (IfExp) in Python, verify the CC score with crap4py BEFORE committing — each BoolOp and IfExp adds a branch point to CC. A refactor that looks simpler can leave CC unchanged or higher. (cleaner e8692053)

## mutmut has no scan/count mode — estimate site counts instead

The role prompt's mutation-site count gate assumes a `--scan` mode (count sites without running tests). mutmut has none. Interim estimates without a full test run: `uv run mutmut run --max-children 1` to generate the mutant list, then count entries under the `mutants/` tree; or read `mutants/mutmut-stats.json`; or fall back to AST node count when no manifest exists yet. The proper `--scan` arrives with `mutate4py` (todo). Do not trigger a full mutation *test* run just to count. (cleaner e8692053, bd628b3f)

## mutmut state goes stale after a cleaner refactor

Extracted helpers are new functions absent from the manifest, so their mutants are not tracked. Downstream roles must re-run coverage + `uv run mutmut run` before reading results on refactored (C4) files. (cleaner bd628b3f)
