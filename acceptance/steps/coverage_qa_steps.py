"""Step handlers for features/coverage_qa.feature (C3, #9).

End-to-end QA for C3: verifies coverage column through the crap4py CLI.
"""
import os
import sys
import re

from acceptance.steps.step_lib import make_registry, check_cli_available, run_cli, QAState

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_C3_FIXTURE_ROOT = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c3_fixture")
_C3_FIXTURE_LCOV = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c3_fixture.lcov")

STEP_HANDLERS, step, run_step = make_registry()

CLI_AVAILABLE = check_cli_available()
ctx = QAState(_C3_FIXTURE_ROOT, _C3_FIXTURE_LCOV)


def _run_cli() -> str:
    return run_cli(ctx.lcov_path, ctx.source_path, CLI_AVAILABLE)


def _extract_coverage(report: str, func_name: str) -> str | None:
    """Find the row for func_name and return its coverage as a fraction string.

    The Cov% column shows values like '75.0%' or 'N/A'. This helper converts
    percentage values back to fractions ('75.0%' → '0.75') so that C3 QA
    assertions comparing against raw fractions ('0.75', '1.0') still hold.
    """
    lines = report.splitlines()
    header_line = next((l for l in lines if "Cov%" in l), None)
    if header_line is None:
        # Old 4-column format: last token is the raw fraction
        for line in lines:
            if func_name in line:
                parts = line.split()
                return parts[-1] if parts else None
        return None
    cov_col = header_line.index("Cov%")
    for line in lines:
        if func_name in line:
            segment = line[cov_col:]
            tokens = segment.split()
            if not tokens:
                return None
            raw = tokens[0]
            if raw == "N/A":
                return "N/A"
            if raw.endswith("%"):
                try:
                    return str(float(raw[:-1]) / 100.0)
                except ValueError:
                    return raw
            return raw
    return None


def _fixture_coverage(func_name: str):
    """Return the resolved coverage for func_name from the c3 fixture LCOV."""
    sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.coverage import parse_lcov, resolve_coverage, NA as _NA
    from crap4py.discovery import discover_functions
    with open(_C3_FIXTURE_LCOV) as f:
        lcov_text = f.read()
    lcov_data = parse_lcov(lcov_text)
    entries = discover_functions([_C3_FIXTURE_ROOT], root=_REPO_ROOT)
    matching = [e for e in entries if e.qualified_name == func_name]
    assert matching, f"Function '{func_name}' not in fixture; got {[e.qualified_name for e in entries]}"
    entry = matching[0]
    return resolve_coverage(entry.module_label, entry.line_range, lcov_data), _NA


# --- Background ---

@step(r"a committed Python fixture tree and a matching LCOV file")
def given_fixture_tree(m, params):
    assert os.path.isdir(ctx.source_path), f"Fixture dir missing: {ctx.source_path}"
    assert os.path.isfile(ctx.lcov_path), f"Fixture LCOV missing: {ctx.lcov_path}"
    ctx.report_output = _run_cli()


@step(r'the command "uv run crap4py --lcov <lcov> <root>" has been run')
def given_command_run(m, params):
    ctx.report_output = _run_cli()


# --- qa-coverage-1 ---

@step(r'the fixture\'s function "([^"]+)" has (\d+) of (\d+) branches taken in the LCOV')
def given_fixture_function_coverage(m, params):
    func_name = params.get("function") or m.group(1)
    taken = int(params.get("taken_count") or m.group(2))
    total = int(params.get("total_count") or m.group(3))
    cov, NA = _fixture_coverage(func_name)
    assert cov is not NA, f"Unexpected N/A for '{func_name}'"
    expected = taken / total
    assert abs(float(cov) - expected) < 1e-9, (
        f"Fixture coverage for '{func_name}': expected {expected}, got {cov}"
    )


# --- qa-coverage-2 ---

@step(r'the fixture\'s function "([^"]+)" has no branches and its file is in the LCOV')
def given_zero_branch_function(m, params):
    func_name = params.get("function") or m.group(1)
    cov, NA = _fixture_coverage(func_name)
    assert cov is not NA, f"Unexpected N/A for '{func_name}'"
    assert float(cov) == 1.0, f"Expected 1.0 for zero-branch '{func_name}', got {cov}"


# --- qa-coverage-3 ---

@step(r'the fixture\'s function "([^"]+)" is in a file with no SF record in the LCOV')
def given_absent_file_function(m, params):
    func_name = params.get("function") or m.group(1)
    cov, NA = _fixture_coverage(func_name)
    assert cov is NA, f"Expected N/A for '{func_name}', got {cov}"


# --- When ---

@step(r"the report is produced")
def when_report_produced(m, params):
    if not ctx.report_output:
        ctx.report_output = _run_cli()


# --- Then ---

@step(r'the report row for "([^"]+)" shows coverage "([^"]+)"')
def then_report_row_shows_coverage(m, params):
    func_name = params.get("function") or m.group(1)
    expected_cov = params.get("coverage") or m.group(2)
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify '{func_name}' coverage={expected_cov}")
        return
    actual = _extract_coverage(ctx.report_output, func_name)
    assert actual is not None, (
        f"Function '{func_name}' not found in report:\n{ctx.report_output}"
    )
    assert actual == expected_cov, (
        f"Coverage for '{func_name}': expected '{expected_cov}', got '{actual}'"
    )
