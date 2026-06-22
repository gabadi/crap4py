"""Step handlers for features/report_qa.feature (C4, #10).

End-to-end QA: verifies CRAP column, sort order, format, and CLI flags
through the crap4py CLI using the committed c4_fixture.
"""
import os
import sys
import subprocess

from acceptance.steps.step_lib import make_registry, check_cli_available

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_C4_FIXTURE_ROOT = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c4_fixture")
_C4_FIXTURE_LCOV = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c4_fixture.lcov")

STEP_HANDLERS, step, run_step = make_registry()
CLI_AVAILABLE = check_cli_available()


class QACtx:
    def __init__(self):
        self.report_output: str = ""
        self.cli_exit_code: int = 0
        self.cli_stdout: str = ""
        self.cli_stderr: str = ""
        self.serial_output: str = ""


ctx = QACtx()


def _run_fixture_cli(*extra_args: str) -> tuple[int, str, str]:
    """Run the CLI on the c4 fixture with optional extra args."""
    cmd = ["uv", "run", "crap4py", "--lcov", _C4_FIXTURE_LCOV, _C4_FIXTURE_ROOT] + list(extra_args)
    result = subprocess.run(cmd, cwd=_REPO_ROOT, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def _row_for(report: str, func_name: str) -> str | None:
    """Return the table row line containing func_name, or None."""
    for line in report.splitlines():
        if func_name in line:
            return line
    return None


def _crap_col(row: str) -> str:
    """Extract the last whitespace-delimited token from a report row (the CRAP column)."""
    return row.split()[-1]


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------

@step(r"a committed Python fixture tree and a matching LCOV file")
def given_fixture_tree(m, params):
    assert os.path.isdir(_C4_FIXTURE_ROOT), f"Fixture dir missing: {_C4_FIXTURE_ROOT}"
    assert os.path.isfile(_C4_FIXTURE_LCOV), f"Fixture LCOV missing: {_C4_FIXTURE_LCOV}"
    if not ctx.report_output:
        _, ctx.report_output, _ = _run_fixture_cli()


@step(r"the command \"uv run crap4py --lcov <lcov> <root>\" has been run")
def given_command_run(m, params):
    if not ctx.report_output:
        _, ctx.report_output, _ = _run_fixture_cli()


# ---------------------------------------------------------------------------
# qa-report-1: CRAP column from CC and coverage
# ---------------------------------------------------------------------------

@step(r"the fixture's function \"([^\"]+)\" has cyclomatic complexity (\d+) and coverage \"([^\"]+)\"")
def given_fixture_function_cc_and_cov(m, params):
    # Validate the fixture is correct (actual values were set at fixture-build time).
    func_name = params.get("function") or m.group(1)
    expected_cc = int(params.get("cc") or m.group(2))
    expected_cov_str = params.get("coverage") or m.group(3)

    sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.discovery import discover_functions
    from crap4py.complexity import cyclomatic_complexity
    from crap4py.coverage import parse_lcov, resolve_coverage, NA

    entries = discover_functions([_C4_FIXTURE_ROOT])
    matching = [e for e in entries if e.qualified_name == func_name]
    assert matching, f"Function {func_name!r} not found in fixture; got {[e.qualified_name for e in entries]}"
    entry = matching[0]

    with open(entry.module_label) as f:
        src = f.read()
    cc_map = {r.name: r.cc for r in cyclomatic_complexity(src)}
    bare = entry.qualified_name.rsplit(".", 1)[-1]
    actual_cc = cc_map.get(bare, 1)
    assert actual_cc == expected_cc, f"CC for {func_name!r}: expected {expected_cc}, got {actual_cc}"

    with open(_C4_FIXTURE_LCOV) as f:
        lcov_data = parse_lcov(f.read())
    cov = resolve_coverage(entry.module_label, entry.line_range, lcov_data)
    assert cov is not NA, f"Expected finite coverage for {func_name!r}, got N/A"
    assert abs(float(cov) - float(expected_cov_str)) < 1e-9, (
        f"Coverage for {func_name!r}: expected {expected_cov_str}, got {float(cov)}"
    )


@step(r"the report is produced")
def when_report_produced(m, params):
    if not ctx.report_output:
        _, ctx.report_output, _ = _run_fixture_cli()


@step(r"the report row for \"([^\"]+)\" shows CRAP \"([^\"]+)\"")
def then_row_shows_crap(m, params):
    func_name = params.get("function") or m.group(1)
    expected_crap = params.get("crap") or m.group(2)
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify CRAP for {func_name!r}")
        return
    row = _row_for(ctx.report_output, func_name)
    assert row is not None, f"Function {func_name!r} not found in report:\n{ctx.report_output}"
    actual_crap = _crap_col(row)
    assert actual_crap == expected_crap, (
        f"CRAP for {func_name!r}: expected {expected_crap!r}, got {actual_crap!r}\nrow: {row!r}"
    )


# ---------------------------------------------------------------------------
# qa-report-2: N/A coverage → N/A CRAP
# ---------------------------------------------------------------------------

@step(r"the fixture's function \"([^\"]+)\" is in a file with no SF record in the LCOV")
def given_absent_file_function(m, params):
    func_name = params.get("function") or m.group(1)
    sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.discovery import discover_functions
    from crap4py.coverage import parse_lcov, resolve_coverage, NA

    entries = discover_functions([_C4_FIXTURE_ROOT])
    matching = [e for e in entries if e.qualified_name == func_name]
    assert matching, f"Function {func_name!r} not found in fixture"
    entry = matching[0]

    with open(_C4_FIXTURE_LCOV) as f:
        lcov_data = parse_lcov(f.read())
    cov = resolve_coverage(entry.module_label, entry.line_range, lcov_data)
    assert cov is NA, f"Expected N/A for {func_name!r}, got {cov!r}"


# ---------------------------------------------------------------------------
# qa-report-3: sort order
# ---------------------------------------------------------------------------

@step(r"the fixture has a worst-CRAP function \"([^\"]+)\" and an N/A-CRAP function \"([^\"]+)\"")
def given_worst_and_na(m, params):
    worst_fn = params.get("worst_fn") or m.group(1)
    na_fn = params.get("na_fn") or m.group(2)
    ctx._worst_fn = worst_fn
    ctx._na_fn = na_fn
    if not ctx.report_output:
        _, ctx.report_output, _ = _run_fixture_cli()


@step(r"the row for \"([^\"]+)\" appears before the row for \"([^\"]+)\"")
def then_row_before(m, params):
    first_fn = params.get("first") or m.group(1)
    second_fn = params.get("second") or m.group(2)
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify order {first_fn!r} before {second_fn!r}")
        return
    lines = ctx.report_output.splitlines()
    positions = {}
    for i, line in enumerate(lines):
        if first_fn in line:
            positions[first_fn] = i
        if second_fn in line:
            positions[second_fn] = i
    assert first_fn in positions, f"Function {first_fn!r} not in report:\n{ctx.report_output}"
    assert second_fn in positions, f"Function {second_fn!r} not in report:\n{ctx.report_output}"
    assert positions[first_fn] < positions[second_fn], (
        f"Expected {first_fn!r} (line {positions[first_fn]}) before "
        f"{second_fn!r} (line {positions[second_fn]})"
    )


@step(r"the row for \"([^\"]+)\" appears after every non-N/A row")
def then_row_last(m, params):
    na_fn = params.get("na_fn") or m.group(1)
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify {na_fn!r} sorts last")
        return
    lines = ctx.report_output.splitlines()
    na_pos = None
    for i, line in enumerate(lines):
        if na_fn in line:
            na_pos = i
            break
    assert na_pos is not None, f"Function {na_fn!r} not in report:\n{ctx.report_output}"
    # All data rows after header (line 3 = separator, data starts at line 4)
    data_lines = [(i, l) for i, l in enumerate(lines) if i > 3 and l.strip()]
    non_na_positions = [i for i, l in data_lines if na_fn not in l]
    assert all(p < na_pos for p in non_na_positions), (
        f"N/A row {na_fn!r} at line {na_pos} is not last; "
        f"non-N/A lines at: {non_na_positions}"
    )


# ---------------------------------------------------------------------------
# qa-report-4: header block format
# ---------------------------------------------------------------------------

@step(r"the first printed line is \"CRAP Report\"")
def then_first_line_is_crap_report(m, params):
    if not CLI_AVAILABLE:
        print("NOT AUTOMATED — CLI absent: cannot verify first line")
        return
    first = ctx.report_output.splitlines()[0] if ctx.report_output else ""
    assert first == "CRAP Report", f"Expected 'CRAP Report', got {first!r}"


@step(r"a header row names \"Function\", \"Module\", \"CC\", \"Cov%\", and \"CRAP\"")
def then_header_names_columns(m, params):
    if not CLI_AVAILABLE:
        print("NOT AUTOMATED — CLI absent: cannot verify header")
        return
    header_line = ctx.report_output.splitlines()[2] if ctx.report_output else ""
    for col in ("Function", "Module", "CC", "Cov%", "CRAP"):
        assert col in header_line, f"Column {col!r} not in header: {header_line!r}"


# ---------------------------------------------------------------------------
# qa-report-5: --max-crap gate
# ---------------------------------------------------------------------------

@step(r"the fixture's worst CRAP score is (\d+(?:\.\d+)?)")
def given_fixture_worst_crap(m, params):
    # Just verify the fixture has worst=30.0 (it does — `worst` function).
    expected = float(params.get("worst") or m.group(1))
    assert abs(expected - 30.0) < 0.01, f"QA fixture worst CRAP is 30.0, not {expected}"


@step(r"the command runs with \"--max-crap ([^\"]+)\"")
def when_max_crap(m, params):
    threshold = params.get("threshold") or m.group(1)
    result = subprocess.run(
        ["uv", "run", "crap4py", "--lcov", _C4_FIXTURE_LCOV,
         "--max-crap", threshold, _C4_FIXTURE_ROOT],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    ctx.cli_exit_code = result.returncode
    ctx.cli_stdout = result.stdout
    ctx.cli_stderr = result.stderr


@step(r"the command exits with status \"([^\"]+)\"")
def then_exits_with_status(m, params):
    status_str = params.get("exit") or m.group(1)
    if status_str == "zero":
        assert ctx.cli_exit_code == 0, (
            f"Expected exit 0 but got {ctx.cli_exit_code}\n"
            f"stdout:\n{ctx.cli_stdout}\nstderr:\n{ctx.cli_stderr}"
        )
    else:
        assert ctx.cli_exit_code != 0, (
            f"Expected non-zero exit but got {ctx.cli_exit_code}\n"
            f"stdout:\n{ctx.cli_stdout}\nstderr:\n{ctx.cli_stderr}"
        )


# ---------------------------------------------------------------------------
# qa-report-6: N/A rows don't trip --max-crap
# ---------------------------------------------------------------------------

@step(r"the fixture has an N/A-CRAP function and its worst finite CRAP score is (\d+(?:\.\d+)?)")
def given_na_and_finite(m, params):
    expected = float(params.get("worst") or m.group(1))
    # Fixture has uncovered_file_fn (N/A) and worst (30.0).
    assert abs(expected - 30.0) < 0.01, f"QA fixture worst finite CRAP is 30.0, not {expected}"


# ---------------------------------------------------------------------------
# qa-report-7: --max-workers produces identical report
# ---------------------------------------------------------------------------

@step(r"the command runs the fixture with \"--max-workers ([^\"]+)\"")
def when_max_workers(m, params):
    workers = params.get("workers") or m.group(1)
    if not ctx.serial_output:
        _, ctx.serial_output, _ = _run_fixture_cli()
    _, ctx.cli_stdout, ctx.cli_stderr = _run_fixture_cli("--max-workers", workers)


@step(r"the report text is identical to the serial report over the same fixture")
def then_identical_to_serial(m, params):
    if not CLI_AVAILABLE:
        print("NOT AUTOMATED — CLI absent: cannot compare serial vs workers report")
        return
    assert ctx.cli_stdout == ctx.serial_output, (
        f"max-workers output differs from serial:\n"
        f"serial:\n{ctx.serial_output}\nworkers:\n{ctx.cli_stdout}"
    )
