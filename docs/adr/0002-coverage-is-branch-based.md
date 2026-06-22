# ADR 0002 — Coverage is branch-based (LCOV)

- Status: accepted
- Date: 2026-06-22
- Tracking: #9 (C3)

> Stub recorded during C1 work so the complexity model (ADR 0001) has its
> companion coverage decision on record. Expanded during the C3 grill
> (2026-06-22) with the LCOV-parsing rules and the DA-fallback decision below.

## Context

The original CRAP metric (Savoia & Evans, crap4j, 2007) defined the coverage
term `cov(m)` as **path coverage** — dimensionally matched to cyclomatic
complexity, which counts the independent paths through a function. Most language
ecosystems lack path-coverage tooling, so ports approximate it.

crap4py consumes Python coverage as **LCOV** (`coverage.py --cov-branch` output),
not by running tests itself (see #6 scope).

## Decision

Coverage for the CRAP formula is **branch coverage**, taken from LCOV `BRDA`
records that fall within a function's line range. Branch coverage is the closest
tractable approximation of crap4j's original path coverage and pairs
dimensionally with cyclomatic complexity (both count control-flow branches).

A function with zero branches (no `BRDA` records in its range) is treated as
trivially 100% covered (0 branches needed, 0 missed), **not** as indeterminate.
A function is reported as `N/A` only when its coverage is genuinely
indeterminate (e.g. its source file is absent from the LCOV data).

## C3 grill outcomes (2026-06-22)

**Branch-coverage formula.** For a function with line range `[start, end]`
(from C2, 1-based inclusive) whose source file matches an `SF` record:
`coverage = (# BRDA records in range with taken ≥ 1) / (# BRDA records in range)`.
A `taken` of `-` (block never reached) and a `taken` of `0` (block reached, this
branch not taken) are *both* uncovered for the numerator but *both* counted in
the denominator. The result is a fraction in `[0, 1]` consumed by the CRAP
formula (ADR 0001 / CONTEXT.md).

**Zero-branch function → 100%, file-absent → N/A.** A function whose range
contains no in-range BRDA records is `100%` (1.0), even when its file is present
in the LCOV. Coverage is `N/A` only when the function's source file has no
matching `SF` record — the single genuinely-indeterminate case.

**File matching.** A discovered source-file path is matched to an `SF` record by
path normalization and suffix matching, because LCOV `SF` paths may be absolute,
relative, or rooted differently from the discovery cwd. The exact matching
algorithm is the coder's choice; the behavior is "the right `SF` is found when one
plausibly corresponds, else N/A."

**No DA line-coverage fallback (decided NO).** A file present in the LCOV but
carrying no BRDA records at all yields correct per-function results under the
zero-branch = 100% rule (every function in it gets 100%), so a DA-based line
fallback is *not* offered. Reasons: (1) it would mix a line-coverage number into
a branch-coverage column, breaking the dimensional consistency this ADR exists to
preserve; (2) the zero-branch rule already covers the motivating case; (3) it
adds an ambiguous third coverage source for no behavioral gain. `DA` records are
tolerated in the input but never drive the coverage number.

## Consequences

- Coverage and complexity are dimensionally consistent (both branch-counted).
- LCOV parsing must handle coverage.py specifics: branch-id field is opaque
  *text* (e.g. `"jump to line 8"`), not an integer; `block` is always `0`;
  `taken` is `-`/`0`/count; `BRDA` records with `line=0` (a coverage.py bug) are
  ignored. Non-`BRDA` records (`DA`/`FN`/`FNDA`/`LF`/`LH`/`BRF`/`BRH`) are
  tolerated whether present or absent and never drive the number.
- Function line ranges come from C2 (`ast`), never from `FN`/`FNDA` (historically
  sometimes omitted by coverage.py).
