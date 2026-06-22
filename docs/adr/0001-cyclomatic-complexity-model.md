# ADR 0001 — Cyclomatic complexity model

- Status: accepted
- Date: 2026-06-22
- Tracking: #7 (C1)

## Context

crap4py ports the CRAP tooling from `unclebob/crap4go` and `unclebob/crap4clj`
to Python. CRAP multiplies cyclomatic complexity (CC) by an uncovered-code
factor, so CC is the load-bearing input to every score. We must define exactly
which Python constructs increase CC.

The Go and Clojure originals count decision points specific to their own
languages; those rules do not map 1:1 onto Python. We surveyed the source code
(not the docs) of the four established Python CC tools — radon, mccabe, lizard,
and Ruff's C901 — and found two coherent philosophies:

- **Statement-only model** (mccabe, Ruff C901): count only statement-level
  control-flow branches.
- **Expression-aware model** (radon): additionally count expression-level
  branching — boolean operators, ternaries, comprehension clauses, `assert`.

CRAP's purpose is to flag functions whose *branches* are under-tested, and
cyclomatic complexity is defined over branches in the control-flow graph. The
expression-aware model captures more of the real branching a reader must reason
about, and radon is the most widely used Python CC tool. crap4py adopts the
expression-aware (radon) model.

## Decision

CC of a function = (number of decision points) + 1, computed from the Python
`ast`. The minimum CC is 1.

Decision points that add +1:

| Construct | Contribution |
| --- | --- |
| `if` | +1 |
| `elif` | +1 (each) |
| `for`, `while` | +1 (each) |
| loop `else` clause (`for…else` / `while…else`) | +1 |
| `except` handler | +1 (each) |
| boolean `and` / `or` | +1 per *extra* operand: `len(values) − 1` per `BoolOp` |
| ternary `a if c else b` (`IfExp`) | +1 |
| comprehension `for` clause | +1 (each) |
| comprehension `if` clause | +1 (each) |
| `match` `case` (non-wildcard) | +1 (each) |
| `assert` | +1 |

Constructs that add **0**: `else` (of an `if`), `try`, `finally`, `with`,
the wildcard `case _:` (without a guard), and the function header itself.

Boolean operand counting: `a and b` = +1; `a and b and c` = +2 (one `BoolOp`
node with three values → +2). Mixed `a and b or c` = two `BoolOp` nodes → +2.

Nested scope: every `def` and `async def` — including methods and inner
functions — is a separate scored unit. A nested function's decision points
count toward the nested function, **not** its enclosing function. This matches
radon and mccabe (and diverges from Ruff C901, which folds nested defs into the
parent).

## Consequences

- crap4py's CC numbers align with **radon**, and diverge from mccabe / Ruff
  C901, which omit booleans, ternaries, comprehensions, and `assert`.
- The loop `else` clause adds +1 (radon behaviour); mccabe and Ruff do not count
  it. This is a deliberate, documented divergence.
- `with` is deliberately uncounted, consistent with *all four* surveyed tools
  (radon's documentation claims it counts `with`, but its source has no
  `visit_With` handler). Revisiting this is tracked separately in #11.
- Each rule is independently observable and therefore independently
  mutation-testable in the acceptance suite.

## Alternatives considered

- **Statement-only (mccabe/Ruff) model** — rejected: it discards
  expression-level branching that CRAP exists to surface, understating risk for
  condition-heavy code.
- **Counting `with`** — rejected: no established Python CC tool counts it;
  doing so would make every crap4py score disagree with radon/Ruff on common
  resource-management code. Tracked for future reconsideration in #11.
- **Folding nested defs into the parent (Ruff)** — rejected: per-function
  scoring is the whole point of a CRAP report; folding hides nested complexity
  and complicates coverage line-range matching.
