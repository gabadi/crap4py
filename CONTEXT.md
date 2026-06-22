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

- **Qualified name** — a function entry's display name. A bare function is its
  own name; a method is `Class.method`; nesting is reflected per ADR 0001 (each
  nested def is its own entry). (Detailed in C2.)

- **Coverage** — the fraction of a function's branches exercised by tests, read
  from LCOV `BRDA` records within the function's line range. See
  [ADR 0002](docs/adr/0002-coverage-is-branch-based.md). (Detailed in C3.)

- **N/A coverage** — coverage that is genuinely indeterminate (e.g. the source
  file is absent from the LCOV). A zero-branch function is *not* N/A; it is
  trivially 100% covered.
