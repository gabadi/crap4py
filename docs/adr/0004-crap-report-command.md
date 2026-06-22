# ADR 0004 — CRAP report command (the integration surface)

- Status: accepted
- Date: 2026-06-22
- Tracking: #10 (C4)

> The C1–C3 decisions (ADRs 0001–0003) each declared the report itself out of
> scope. This ADR records the integration surface: the one command that combines
> complexity (C1), discovery/naming (C2), and coverage (C3) into a CRAP score,
> sorts the functions, and prints the report. Settled during the C4 grill
> (2026-06-22) against the `crap4go` reference (`cli.go`, `crap.go`, `main.go`).

## Context

`uv run crap4py` is the only user-facing affordance for the whole tool. C1–C3
produce, per function, a cyclomatic complexity, a qualified name + module label,
and a coverage value (a fraction in `[0, 1]` or the `N/A` sentinel). C4 turns
those into the CRAP score and the printed report.

crap4py deliberately diverges from `crap4go` in one structural way: crap4go
*generates* coverage by running `go test` inside `main.go`, so coverage is never
absent. crap4py **consumes a pre-generated LCOV file** (ADR 0002, #6 scope) and
never runs tests. That single difference drives the `--lcov`-required decision
below.

## Decision

**CRAP score.** `CRAP = CC² × (1 − coverage)³ + CC`, where `coverage` is the
fraction in `[0, 1]` from C3. When a function's coverage is `N/A` (indeterminate,
per ADR 0002), its CRAP score is `N/A` — indeterminacy propagates; it is never
coerced to 0 coverage. (crap4go expresses the same formula over a percentage and
`nil`; crap4py uses the `[0, 1]` fraction and the C3 `N/A` sentinel.)

**Sorting.** Rows are ordered **worst CRAP first** (descending). `N/A`-CRAP rows
sort **last**. Ties — equal CRAP scores, or two `N/A` rows — break **stably by
qualified function name, ascending**. The sort is stable so that equal-CRAP rows
retain a deterministic, name-ordered arrangement.

**Report format.** A fixed-width table, mirroring `crap4go`'s `FormatReport`:

```
CRAP Report
===========
Function                       Module                               CC    Cov%     CRAP
------------------------------------------------------------------------------------------
<name>                         <module label>                       <cc>  <cov%>  <crap>
```

- A title line `CRAP Report`, an underline of `=`, the column header row, and a
  `-` separator line, then one row per function.
- Columns are `Function`, `Module`, `CC`, `Cov%`, `CRAP`. (The `Module` column
  is C2's module label — the source path relative to the invocation cwd —
  replacing crap4go's `Package`, since Python has no Go-style package term.)
- `Cov%` is the coverage fraction shown as a percentage; `N/A` when indeterminate.
- `CRAP` is the score to one decimal; `N/A` when coverage is `N/A`.
- Empty input (no functions discovered) still prints the header block.

**CLI.**

- `--lcov PATH` is **required**. Omitting it is a **usage error** (clear stderr
  message + non-zero exit), *not* an all-`N/A` run — because crap4py cannot
  generate coverage the way crap4go does, a CRAP report with no coverage source
  is meaningless. The `[--lcov]` bracket in the issue title was tentative; this
  ADR resolves it to required.
- Positional **path-fragment filters**: zero or more substring fragments. When
  present, only source files whose path contains at least one fragment are
  analyzed (crap4go `filterSources` semantics). With none, all discovered
  source under the given paths is analyzed.
- `-h` / `--help` prints a usage message and exits 0.
- Invalid or missing required arguments print a clear message to stderr and exit
  non-zero.

**`--max-crap N` (opt-in CI gate).** Optional. When supplied, the command exits
**non-zero** if **any** function's CRAP score is **strictly greater than `N`**.
`N/A`-CRAP rows never trigger the gate. The report still prints in full before
the non-zero exit. There is **no default threshold** — absent the flag, success
is always exit 0. The threshold is caller-supplied precisely because the
"crappy = 30" figure is a convention, not a universal project constant, so it is
never hard-coded into the tool.

**`--max-workers N` (parallelism).** Optional. Analyzes source files across `N`
worker processes/threads (crap4go parity). It is a **performance** affordance
only: the printed report — rows, order, every value — is **identical** to a
serial run. Requires a positive integer; a non-positive or non-integer value is
a usage error.

**No risk bands.** The report shows the numeric CRAP score only. No low/moderate/
high band column, label, or color, and no fixed-threshold annotation in normal
output. crap4go's `FormatReport` has none either; the only threshold crap4py
honors is the opt-in `--max-crap` gate, which is caller-supplied. Baking fixed
bands (1–5 / 5–30 / 30+) into output would impose project-specific cutoffs the
tool has no basis to assume.

## Consequences

- C4 is pure integration: it adds the score, the sort, the format, and the CLI;
  it does **not** re-derive CC (C1), discovery/naming/module label (C2), or
  coverage (C3). A contradiction between this report and those upstream values is
  an upstream bug, not a C4 concern.
- `N/A` is a first-class report state end-to-end: indeterminate coverage → `N/A`
  Cov% → `N/A` CRAP → sorts last → never trips `--max-crap`.
- The exit-code contract has three outcomes: `0` on a clean run (or a run with
  no `--max-crap` gate), non-zero on a usage/IO error (bad args, omitted/missing/
  unreadable `--lcov`), and non-zero on a `--max-crap` breach.
- `--max-workers` must be verified to be output-invariant; the QA suite asserts
  identical output between a serial and a parallel run over the same fixture.
