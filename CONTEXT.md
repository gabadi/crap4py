# crap4py — Context & Glossary

crap4py is a command-line tool that computes a **CRAP score** per function for
Python source files. It is a Python port of `unclebob/crap4go` and
`unclebob/crap4clj`. Complexity comes from Python's `ast`; coverage comes from
an LCOV file produced by `coverage.py`.

Architecture decisions live in `docs/adr/`. Use the vocabulary below in issues,
specs, test names, and code.

## Glossary

- **CRAP** (Change Risk Anti-Pattern) — a per-function risk metric combining
  complexity and test coverage:
  `CRAP = CC² × (1 − coverage)³ + CC`, where `coverage` is a fraction in
  `[0, 1]`. Higher means riskier to change. Canonical "crappy" threshold is 30.

- **Cyclomatic complexity (CC)** — the number of independent paths through a
  function: decision points + 1, minimum 1. Computed from the `ast`. See
  [ADR 0001](docs/adr/0001-cyclomatic-complexity-model.md) for the exact rules.

- **Decision point** — an `ast` node that forks control flow and so adds 1 to
  CC. The counted set (ADR 0001): `if`, `elif`, `for`, `while`, loop `else`,
  each `except`, each extra boolean operand, ternary, each comprehension
  `for`/`if` clause, each non-wildcard `match` case, and `assert`. `with`,
  `else`, `try`, `finally`, and bare `case _:` are **not** decision points.

- **Function entry** — one scored unit: a `def` or `async def`, including
  methods and nested/inner functions. Each entry is named and has its CC
  computed in its own scope; a nested function's decision points do not count
  toward the enclosing function.

- **Qualified name** — a function entry's display name: the `def` name qualified
  by every enclosing **class**. A module-level function is its own name; a method
  is `Class.method`; a method on a nested class is `Outer.Inner.method`; a
  nested/inner `def` is named by its own `def` name (enclosing *functions* do not
  qualify, only classes do). Decorators (`@property`, `@overload`, …) never change
  the name, and each `@overload` stub is its own entry. See
  [ADR 0003](docs/adr/0003-function-discovery-and-naming.md).

- **Module label** — the report's per-function module column: the source file
  path **relative to the invocation working directory** (e.g.
  `src/crap4py/complexity.py`). No dotted-import inference. See ADR 0003.

- **Discovery / skip rules** — crap4py walks the given source paths and emits one
  entry per `def`/`async def`. A path ignored by the project's `.gitignore` is not
  scored (the drywall strategy), and test files (`test_*.py`, `*_test.py`) are
  always skipped on top of that. See ADR 0003.

- **Line range** — a function entry's `[start, end]` source-line span, taken from
  its `ast` node (`lineno`..`end_lineno`); for a decorated function it starts at
  the `def` line, not the decorator. C3 intersects this range with LCOV `BRDA`
  records to resolve coverage.

- **Coverage** — the fraction (`[0, 1]`) of a function's branches exercised by
  tests: `(# in-range BRDA with taken ≥ 1) / (# in-range BRDA)`, over the `BRDA`
  records that fall in the function's line range. A `taken` of `-` or `0` is
  uncovered; both still count toward the denominator. See
  [ADR 0002](docs/adr/0002-coverage-is-branch-based.md).

- **N/A coverage** — coverage that is genuinely indeterminate: the function's
  source file has no matching `SF` record in the LCOV. A zero-branch function
  (no in-range `BRDA`) is *not* N/A; it is trivially 100% covered, even when its
  file is present in the LCOV.

- **LCOV / `BRDA`** — the coverage input format (produced by `coverage.py
  --cov-branch`). A `BRDA:<line>,<block>,<branch>,<taken>` record is one branch
  edge. crap4py reads only `BRDA` (and `SF` to locate the file); coverage.py
  quirks are tolerated: the `branch` id is opaque *text* (not an integer),
  `block` is always `0`, `taken` is `-`/`0`/count, and `line=0` records (a
  coverage.py bug) are ignored. There is **no** `DA` line-coverage fallback.
