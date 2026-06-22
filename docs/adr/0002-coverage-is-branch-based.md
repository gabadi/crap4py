# ADR 0002 — Coverage is branch-based (LCOV)

- Status: accepted
- Date: 2026-06-22
- Tracking: #9 (C3)

> Stub recorded during C1 work so the complexity model (ADR 0001) has its
> companion coverage decision on record. Full LCOV-parsing detail is owned by
> C3 and will be expanded during the C3 grill.

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

## Consequences

- Coverage and complexity are dimensionally consistent.
- Whether a DA line-coverage fallback is also offered is left open for the C3
  grill; the zero-branch = 100% rule already removes the original motivation for
  it.
- LCOV parsing must handle coverage.py specifics (textual branch ids, `block`
  always 0, `taken` of `-`/`0`/count, possible `line=0` records). Detailed in
  C3.
