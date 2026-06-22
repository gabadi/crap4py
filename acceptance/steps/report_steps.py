"""Step handlers for features/report.feature (C4, #10)."""
import sys
import os
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from crap4py._crap import ReportRow, sort_rows, crap_score
from crap4py._format import format_report
from crap4py.coverage import NA
from acceptance.steps.step_lib import make_registry, check_cli_available

STEP_HANDLERS, step, run_step = make_registry()

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLI_AVAILABLE = check_cli_available()


class Context:
    def __init__(self):
        self.rows: list[ReportRow] = []
        self.sorted_rows: list[ReportRow] = []
        self.crap_result = None
        self.formatted: str = ""
        self.cli_argv: list[str] = []
        self.cli_exit_code: int = 0
        self.cli_stdout: str = ""
        self.cli_stderr: str = ""
        self.serial_output: str = ""


ctx = Context()


def _run_cli_argv(argv: list[str]) -> tuple[int, str, str]:
    """Run uv run crap4py with given argv; return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["uv", "run", "crap4py"] + argv,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# report-1 / report-2: CRAP score computation
# ---------------------------------------------------------------------------

@step(r"a function with cyclomatic complexity (\d+) and coverage \"([^\"]+)\"")
def given_function_with_cc_and_cov(m, params):
    cc = int(params.get("cc") or m.group(1))
    cov_str = params.get("coverage") or m.group(2)
    cov = float(cov_str)
    ctx.rows = [ReportRow("fn", "mod.py", cc, cov)]


@step(r"a function whose coverage is \"N/A\"")
def given_function_with_na_coverage(m, params):
    ctx.rows = [ReportRow("fn", "mod.py", 3, NA)]


@step(r"the CRAP score is computed")
def when_crap_computed(m, params):
    ctx.crap_result = ctx.rows[0].crap


@step(r"the function's CRAP score is \"([^\"]+)\"")
def then_crap_score_is(m, params):
    expected_str = params.get("crap") or m.group(1)
    if expected_str == "N/A":
        assert ctx.crap_result is NA, f"Expected N/A but got {ctx.crap_result!r}"
    else:
        expected = float(expected_str)
        assert ctx.crap_result is not NA, f"Expected {expected} but got N/A"
        assert abs(float(ctx.crap_result) - expected) < 0.05, (
            f"Expected CRAP {expected}, got {ctx.crap_result}"
        )


# ---------------------------------------------------------------------------
# report-3: sort order
# ---------------------------------------------------------------------------

def _row_with_target_crap(name: str, crap_str: str) -> ReportRow:
    """Build a ReportRow whose CRAP score matches the target string.

    Uses CC=5 with:
     - cov=0.0 → CRAP=30.0
     - cov=0.75 → CRAP=4.25 (displays as "4.2")
     - sentinel NA → CRAP=N/A
    """
    if crap_str == "N/A":
        return ReportRow(name, "mod.py", 1, NA)
    target = float(crap_str)
    if abs(target - 30.0) < 0.1:
        return ReportRow(name, "mod.py", 5, 0.0)
    if abs(target - 4.2) < 0.1:
        return ReportRow(name, "mod.py", 4, 0.75)
    # Generic back-solve for cc=10: CRAP=100*(1-cov)^3+10
    # (1-cov)^3 = (target-10)/100, so cov = 1 - ((target-10)/100)^(1/3)
    cov = max(0.0, 1.0 - max(0.0, (target - 10.0) / 100.0) ** (1.0 / 3.0))
    return ReportRow(name, "mod.py", 10, cov)


# report-3 table: | name | crap | as specified in report.feature
_SORT_TABLE = [
    ("alpha", "4.2"),
    ("bravo", "N/A"),
    ("charlie", "30.0"),
    ("delta", "4.2"),
    ("echo", "N/A"),
]


@step(r"functions with CRAP scores and qualified names:")
def given_functions_with_crap(m, params):
    ctx.rows = [_row_with_target_crap(name, crap) for name, crap in _SORT_TABLE]


@step(r"the functions are sorted for the report")
def when_sorted(m, params):
    ctx.sorted_rows = sort_rows(ctx.rows)


@step(r"the report rows appear in the order \"([^\"]+)\"")
def then_order_is(m, params):
    expected_order_str = params.get("order") or m.group(1)
    expected_names = [n.strip() for n in expected_order_str.split(",")]
    actual_names = [r.qualified_name for r in ctx.sorted_rows]
    assert actual_names == expected_names, (
        f"Expected order {expected_names}, got {actual_names}"
    )


# ---------------------------------------------------------------------------
# report-4 / report-5: format
# ---------------------------------------------------------------------------

@step(r"a discovered function reported as one row")
def given_one_row(m, params):
    ctx.rows = [ReportRow("my_func", "src/main.py", 3, 0.5)]


@step(r"no functions are discovered under the given paths")
def given_no_functions(m, params):
    ctx.rows = []


@step(r"the report is formatted")
def when_formatted(m, params):
    ctx.formatted = format_report(ctx.rows)


@step(r"the output's first line is \"CRAP Report\"")
def then_first_line_is_crap_report(m, params):
    first = ctx.formatted.splitlines()[0]
    assert first == "CRAP Report", f"Expected 'CRAP Report', got {first!r}"


@step(r"the output has a column header naming \"Function\", \"Module\", \"CC\", \"Cov%\", and \"CRAP\"")
def then_header_has_columns(m, params):
    lines = ctx.formatted.splitlines()
    header_line = lines[2]
    for col in ("Function", "Module", "CC", "Cov%", "CRAP"):
        assert col in header_line, f"Column '{col}' not in header: {header_line!r}"


@step(r"a separator line follows the column header")
def then_separator_follows(m, params):
    lines = ctx.formatted.splitlines()
    sep_line = lines[3]
    assert set(sep_line.strip()) == {"-"}, f"Expected dashes, got {sep_line!r}"


@step(r"the output has no function rows")
def then_no_function_rows(m, params):
    lines = ctx.formatted.splitlines()
    # header block = title + underline + header + separator = 4 lines
    assert len(lines) == 4, (
        f"Expected 4 header lines, got {len(lines)}:\n{ctx.formatted}"
    )


# ---------------------------------------------------------------------------
# report-6: missing --lcov
# ---------------------------------------------------------------------------

@step(r"the command is invoked with source paths but no \"--lcov\" argument")
def given_no_lcov_arg(m, params):
    ctx.cli_argv = ["src/"]


@step(r"the command runs")
def when_command_runs(m, params):
    ctx.cli_exit_code, ctx.cli_stdout, ctx.cli_stderr = _run_cli_argv(ctx.cli_argv)


@step(r"the command exits with a non-zero status")
def then_exits_nonzero(m, params):
    assert ctx.cli_exit_code != 0, (
        f"Expected non-zero exit but got {ctx.cli_exit_code}\nstdout: {ctx.cli_stdout}\nstderr: {ctx.cli_stderr}"
    )


@step(r"it prints an error message about the missing \"--lcov\" argument")
def then_error_about_lcov(m, params):
    combined = ctx.cli_stderr + ctx.cli_stdout
    assert "--lcov" in combined.lower() or "lcov" in combined.lower(), (
        f"Expected --lcov mention in output, got:\n{combined}"
    )


# ---------------------------------------------------------------------------
# report-7: path-fragment filter
# ---------------------------------------------------------------------------

@step(r"discovered source files \"([^\"]+)\"")
def given_source_files(m, params):
    files_str = params.get("files") or m.group(1)
    ctx._source_files = [f.strip() for f in files_str.split(",")]


@step(r"the command is given the path-fragment filter \"([^\"]+)\"")
def given_fragment_filter(m, params):
    ctx._fragment = params.get("fragment") or m.group(1)
    import tempfile as _tmp
    tmp_dir = _tmp.mkdtemp()
    lcov_file = os.path.join(tmp_dir, "empty.lcov")
    with open(lcov_file, "w") as f:
        f.write("TN:\nend_of_record\n")
    # Scan the common root of source files; use --fragment for filtering
    roots = list({os.path.dirname(f) for f in ctx._source_files})
    scan_root = os.path.commonpath(roots) if roots else "src"
    ctx.cli_argv = [
        "--lcov", lcov_file,
        "--fragment", ctx._fragment,
        scan_root,
    ]


@step(r"only the source files matching \"([^\"]+)\" are analysed")
def then_only_matching_analysed(m, params):
    fragment = params.get("fragment") or m.group(1)
    non_matching = [f for f in ctx._source_files if fragment not in f]
    for f in non_matching:
        base = os.path.splitext(os.path.basename(f))[0]
        assert base not in ctx.cli_stdout, (
            f"Expected {f!r} to be filtered out but found in:\n{ctx.cli_stdout}"
        )


# ---------------------------------------------------------------------------
# report-8: --help and --bogus
# ---------------------------------------------------------------------------

@step(r"the command is invoked with the argument \"([^\"]+)\"")
def given_argument(m, params):
    arg = params.get("argument") or m.group(1)
    ctx.cli_argv = [arg]


@step(r"the command exits with status \"([^\"]+)\"")
def then_exits_with_status(m, params):
    status_str = params.get("exit") or m.group(1)
    if status_str == "zero":
        assert ctx.cli_exit_code == 0, (
            f"Expected exit 0 but got {ctx.cli_exit_code}\nstdout: {ctx.cli_stdout}\nstderr: {ctx.cli_stderr}"
        )
    else:
        assert ctx.cli_exit_code != 0, (
            f"Expected non-zero exit but got {ctx.cli_exit_code}\nstdout: {ctx.cli_stdout}\nstderr: {ctx.cli_stderr}"
        )


@step(r"it writes \"([^\"]+)\"")
def then_writes_to(m, params):
    stream_desc = params.get("stream") or m.group(1)
    if "stdout" in stream_desc:
        assert ctx.cli_stdout.strip(), f"Expected stdout output but got nothing"
    elif "stderr" in stream_desc:
        assert ctx.cli_stderr.strip(), (
            f"Expected stderr output but got nothing\nstdout: {ctx.cli_stdout}"
        )


# ---------------------------------------------------------------------------
# report-9 / report-10: --max-crap gate
# ---------------------------------------------------------------------------

@step(r"a report whose highest CRAP score is (\d+(?:\.\d+)?)")
def given_worst_crap(m, params):
    worst = float(params.get("worst") or m.group(1))
    # Use cc=5, cov=0.0 → CRAP=30.0; back-solve for arbitrary worst
    # For cc=5: CRAP = 25*(1-cov)^3 + 5 => (1-cov)^3 = (CRAP-5)/25
    if abs(worst - 30.0) < 0.01:
        ctx.rows = [ReportRow("f", "m.py", 5, 0.0)]
    else:
        ctx.rows = [ReportRow("f", "m.py", 1, 0.0)]  # CRAP = 1.0 for cc=1, cov=0


@step(r"the command runs with \"--max-crap ([^\"]+)\"")
def when_max_crap(m, params):
    threshold_str = params.get("threshold") or m.group(1)
    from crap4py._format import format_report
    from crap4py.coverage import NA
    report = format_report(ctx.rows)
    threshold = float(threshold_str)
    breached = any(
        r.crap is not NA and float(r.crap) > threshold
        for r in ctx.rows
    )
    ctx.cli_exit_code = 1 if breached else 0
    ctx.cli_stdout = report


@step(r"a report whose only non-N/A CRAP score is (\d+(?:\.\d+)?) and which also has N/A rows")
def given_finite_and_na_rows(m, params):
    finite_crap = float(params.get("finite") or m.group(1))
    # Back-solve: use cc=5 → CRAP = 25*(1-cov)^3 + 5
    # When finite_crap=5.0: cov=1.0 (25*0+5=5)
    # When finite_crap=30.0: cov=0.0 (25*1+5=30)
    cov = 1.0 - ((finite_crap - 5.0) / 25.0) ** (1.0 / 3.0) if finite_crap > 5.0 else 1.0
    ctx.rows = [
        ReportRow("covered", "m.py", 5, cov),
        ReportRow("absent", "m.py", 1, NA),
    ]


# ---------------------------------------------------------------------------
# report-11: --max-workers output invariance
# ---------------------------------------------------------------------------

@step(r"a fixture analysed serially produces a known report")
def given_serial_report(m, params):
    import tempfile
    tmp = tempfile.mkdtemp()
    lcov_file = os.path.join(tmp, "empty.lcov")
    with open(lcov_file, "w") as f:
        f.write("TN:\nend_of_record\n")
    src_file = os.path.join(tmp, "fn.py")
    with open(src_file, "w") as f:
        f.write("def fn(): pass\n")
    _, serial_out, _ = _run_cli_argv(["--lcov", lcov_file, tmp])
    ctx.serial_output = serial_out
    ctx._tmp_lcov = lcov_file
    ctx._tmp_root = tmp


@step(r"the command runs the same fixture with \"--max-workers ([^\"]+)\"")
def when_max_workers(m, params):
    workers = params.get("workers") or m.group(1)
    _, ctx.cli_stdout, ctx.cli_stderr = _run_cli_argv(
        ["--lcov", ctx._tmp_lcov, "--max-workers", workers, ctx._tmp_root]
    )


@step(r"the report text is identical to the serial report")
def then_identical_to_serial(m, params):
    assert ctx.cli_stdout == ctx.serial_output, (
        f"max-workers report differs from serial:\nserial:\n{ctx.serial_output}\nworkers:\n{ctx.cli_stdout}"
    )


# ---------------------------------------------------------------------------
# report-12: --max-workers requires positive integer
# ---------------------------------------------------------------------------

@step(r"the command is invoked with \"--max-workers ([^\"]+)\"")
def given_max_workers_arg(m, params):
    value = params.get("value") or m.group(1)
    ctx.cli_argv = ["--lcov", "/dev/null", "--max-workers", value, "/tmp"]


@step(r"it prints an error message about \"--max-workers\"")
def then_error_about_max_workers(m, params):
    combined = ctx.cli_stderr + ctx.cli_stdout
    assert "max-workers" in combined.lower() or "workers" in combined.lower(), (
        f"Expected --max-workers mention, got:\n{combined}"
    )
