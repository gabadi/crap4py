# ADR 0003 — Function discovery & qualified naming

- Status: accepted
- Date: 2026-06-22
- Tracking: #8 (C2)

## Context

C1 (ADR 0001) defined how to compute cyclomatic complexity for *a function*,
operating on a single parsed source string. It deliberately did not say which
functions exist, what they are called in the report, where they live, or which
files are even in scope. C2 owns that discovery layer — the port of crap4go's
`findSourceFiles` + `ExtractFunctions`.

The Go original (`unclebob/crap4go`) establishes the shape we port:

- `findSourceFiles(".")` walks the tree, skips the dirs `.git`, `target`,
  `vendor`, includes `*.go`, and excludes `*_test.go`.
- `ExtractFunctions` records, per top-level `FuncDecl`, a `Name`, a `Package`
  (the Go `package` declaration), and a `StartLine`/`EndLine` span.
- `functionName` qualifies a method as `Receiver.method` and leaves a bare
  function as its own name.

Three things do not map 1:1 onto Python and were settled with the user during
the C2 grill:

1. **The module/package label.** Go has one `package` name per file; Python has
   no per-file package declaration, and inferring a dotted import path
   (`crap4py.complexity`) requires package-root inference that is ambiguous for
   namespace packages and scripts with no `__init__.py`.
2. **The skip rules.** crap4go hardcodes `.git`/`target`/`vendor`. Python's
   non-source trees vary per project (`.venv`, `build/`, `dist/`,
   `__pycache__`, …) and are already enumerated in each project's `.gitignore`.
3. **Decorated functions, properties, and `@overload` stubs.** Go has no direct
   analog; Python decorators must not silently change which entries appear or
   what they are named.

## Decision

**Discovery.** Walk each given source path. Parse every non-excluded `*.py`
file with `ast` and emit one entry per `def`/`async def` — including methods and
nested/inner functions — consistent with C1's per-`def` CC scoping. Each `def`
is its own entry even when it shares a name with a sibling (e.g. successive
`@overload` stubs each appear).

**Skip rules** (the drywall strategy):

- Respect the project's `.gitignore`. A path ignored by Git is not scored. This
  is how `drywall` (the project's DRY tool) discovers files — it passes
  `--gitignore` to jscpd — and it auto-excludes `.venv`, `build/`, `dist/`,
  `__pycache__`, and anything else the project already ignores, tracking each
  project's own conventions instead of a hardcoded list.
- On top of `.gitignore`, **always** skip test files matching `test_*.py` or
  `*_test.py`, even when they are not gitignored. Tests are not shippable
  production code; CRAP-scoring them is noise (crap4go excluded `*_test.go` for
  the same reason).

**Module label.** The report's module column is the **source file path,
relative to the invocation working directory** (e.g. `src/crap4py/complexity.py`).
No package-root inference; never ambiguous; click-to-open in editors; mirrors
crap4go's intent of locating the function's file. The cost — the label shifts
if the tool is run from a different cwd — is accepted as the price of
determinism over import-path inference.

**Qualified name.** A function entry's display name is its `def` name, qualified
by every enclosing *class*:

- A module-level function → its own name (`extract_functions`).
- A method → `Class.method` (`Function.score`).
- A method on a nested class → `Outer.Inner.method`.
- A nested/inner `def` → its own entry named by its `def` name (enclosing
  *functions* do not contribute to the qualifier; only enclosing classes do).

**Decorators.** Decorators do not change an entry's name or whether it appears.
`@property`, `@staticmethod`, `@classmethod`, `@app.route(...)`, and any other
decorator leave the name as the `def` name qualified by enclosing classes. Each
`@overload`-decorated stub is its own entry (it is a `def`).

**Line range.** Each entry records the `def`'s own `ast` span: `node.lineno`
through `node.end_lineno`. For a decorated function this starts at the `def`
keyword line, **not** the decorator line (Python's `ast` reports `lineno` at the
`def`). This range is what C3 intersects with LCOV `BRDA` records.

## Consequences

- The module column is a path, so the report is greppable and editor-clickable
  but is relative to cwd; downstream formatting (C4) treats it as an opaque
  string.
- `.gitignore`-driven skipping means discovery output depends on the project's
  ignore file. A project with no `.gitignore` skips only test files and the
  always-excluded VCS internals. (The exact reader — whether crap4py shells to
  `git`, reads `.gitignore` directly, or reuses a library — is an
  implementation choice owned by the coder; the *behavior* is "gitignored paths
  are not scored.")
- Each `@overload` stub appearing as its own zero-or-low-CC entry is intended,
  not a bug; it keeps discovery a pure structural walk with no decorator
  semantics to special-case.
- The line range deliberately excludes decorator lines. If a future coverage
  question needs decorator execution counted, it is a C3 concern and revisits
  this range, not C2's naming.
