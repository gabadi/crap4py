"""Step handlers for features/complexity_qa.feature.

End-to-end QA for C1: verifies CC values through the crap4py CLI.

NOT AUTOMATED status:
  All scenarios in complexity_qa.feature require 'uv run crap4py --lcov <lcov> <src>'
  to produce a report. The CLI entrypoint (__main__.py), LCOV reader (C3), and
  report formatter (C4) are not yet implemented.
  Each step is implemented but guarded — the harness skips gracefully when the
  CLI is absent. Re-enable by removing the CLI_AVAILABLE guard once C4 lands.
"""
import re
import subprocess
import sys
import os

from acceptance.steps.step_lib import make_registry

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_FIXTURE_PY = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c1_fixture.py")
_FIXTURE_LCOV = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c1_fixture.lcov")

# Guard: CLI is available when crap4py exposes a __main__ entrypoint.
def _cli_available() -> bool:
    result = subprocess.run(
        ["uv", "run", "python", "-c", "import crap4py.__main__"],
        cwd=_REPO_ROOT,
        capture_output=True,
    )
    return result.returncode == 0


CLI_AVAILABLE = _cli_available()


class QAContext:
    def __init__(self):
        self.report_output: str = ""
        self.fixture_py: str = _FIXTURE_PY
        self.fixture_lcov: str = _FIXTURE_LCOV


ctx = QAContext()

STEP_HANDLERS, step, run_step = make_registry()


def _run_cli() -> str:
    """Run 'uv run crap4py --lcov <lcov> <src>' and return stdout."""
    if not CLI_AVAILABLE:
        return ""
    result = subprocess.run(
        ["uv", "run", "crap4py", "--lcov", ctx.fixture_lcov, ctx.fixture_py],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _extract_cc(report: str, func_name: str) -> int | None:
    """Parse a report line for func_name and return its CC integer, or None."""
    for line in report.splitlines():
        if func_name in line:
            m = re.search(r"\b(\d+)\b", line)
            if m:
                return int(m.group(1))
    return None


# --- Background steps ---

@step(r"a committed Python fixture file and a matching LCOV file")
def given_fixture_files(m, params):
    assert os.path.isfile(ctx.fixture_py), f"Fixture missing: {ctx.fixture_py}"
    assert os.path.isfile(ctx.fixture_lcov), f"Fixture missing: {ctx.fixture_lcov}"


@step(r'the command "uv run crap4py --lcov <lcov> <source>" has been run')
def given_command_run(m, params):
    # NOT AUTOMATED — CLI not yet implemented (C4 scope).
    # Will run automatically once CLI_AVAILABLE is True.
    ctx.report_output = _run_cli()


# --- qa-complexity-1 steps ---

@step(r'the fixture defines a function "(.+)" with expected complexity (\d+)')
def given_fixture_function(m, params):
    func_name = params.get("function") or m.group(1)
    expected_cc = int(params.get("cc") or m.group(2))
    # Verify the fixture source actually has this function with the expected CC.
    import ast as ast_mod
    import sys as sys_mod
    sys_mod.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.complexity import cyclomatic_complexity
    with open(ctx.fixture_py) as f:
        source = f.read()
    results = {r.name: r.cc for r in cyclomatic_complexity(source)}
    assert func_name in results, f"Function '{func_name}' not in fixture; got {list(results)}"
    assert results[func_name] == expected_cc, (
        f"Fixture CC mismatch for '{func_name}': expected {expected_cc}, got {results[func_name]}"
    )


@step(r"the report is produced")
def when_report_produced(m, params):
    ctx.report_output = _run_cli()


@step(r'the report row for "(.+)" shows CC (\d+)')
def then_report_row_shows_cc(m, params):
    func_name = params.get("function") or m.group(1)
    expected_cc = int(params.get("cc") or m.group(2))
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify '{func_name}' CC={expected_cc} in report")
        return
    actual_cc = _extract_cc(ctx.report_output, func_name)
    assert actual_cc is not None, (
        f"Function '{func_name}' not found in report output:\n{ctx.report_output}"
    )
    assert actual_cc == expected_cc, (
        f"Report CC mismatch for '{func_name}': expected {expected_cc}, got {actual_cc}"
    )


# --- qa-complexity-2 steps ---

@step(r'the fixture defines a function "(.+)" using chained `and`/`or`')
def given_fixture_boolean_heavy(m, params):
    import sys as sys_mod
    sys_mod.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.complexity import cyclomatic_complexity
    with open(ctx.fixture_py) as f:
        source = f.read()
    results = {r.name: r.cc for r in cyclomatic_complexity(source)}
    assert "boolean_heavy" in results, f"'boolean_heavy' not in fixture; got {list(results)}"


@step(r"its expected complexity under the radon model is (\d+)")
def given_expected_cc_radon(m, params):
    expected = int(params.get("cc") or m.group(1))
    import sys as sys_mod
    sys_mod.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.complexity import cyclomatic_complexity
    with open(ctx.fixture_py) as f:
        source = f.read()
    results = {r.name: r.cc for r in cyclomatic_complexity(source)}
    actual = results.get("boolean_heavy")
    assert actual == expected, f"'boolean_heavy' CC={actual}, expected {expected}"


# --- qa-complexity-3 steps ---

@step(r'the fixture defines a function "(.+)" whose only compound statement is a `with`')
def given_fixture_uses_with(m, params):
    import sys as sys_mod
    sys_mod.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.complexity import cyclomatic_complexity
    with open(ctx.fixture_py) as f:
        source = f.read()
    results = {r.name: r.cc for r in cyclomatic_complexity(source)}
    assert "uses_with" in results, f"'uses_with' not in fixture; got {list(results)}"
    assert results["uses_with"] == 1, f"'uses_with' CC={results['uses_with']}, expected 1"


# --- qa-complexity-4 steps ---

@step(r'the fixture defines an outer function "(.+)" containing a nested function "(.+)"')
def given_fixture_nested(m, params):
    outer = m.group(1)
    inner = m.group(2)
    import sys as sys_mod
    sys_mod.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.complexity import cyclomatic_complexity
    with open(ctx.fixture_py) as f:
        source = f.read()
    results = {r.name: r.cc for r in cyclomatic_complexity(source)}
    assert outer in results, f"'{outer}' not in fixture; got {list(results)}"
    assert inner in results, f"'{inner}' not in fixture; got {list(results)}"


@step(r'"(.+)" has expected complexity (\d+) and "(.+)" has expected complexity (\d+)')
def given_outer_inner_expected(m, params):
    outer = m.group(1)
    outer_cc = int(m.group(2))
    inner = m.group(3)
    inner_cc = int(m.group(4))
    import sys as sys_mod
    sys_mod.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.complexity import cyclomatic_complexity
    with open(ctx.fixture_py) as f:
        source = f.read()
    results = {r.name: r.cc for r in cyclomatic_complexity(source)}
    assert results.get(outer) == outer_cc, (
        f"'{outer}' CC={results.get(outer)}, expected {outer_cc}"
    )
    assert results.get(inner) == inner_cc, (
        f"'{inner}' CC={results.get(inner)}, expected {inner_cc}"
    )


@step(r'the report has a row for "(.+)" showing CC (\d+)')
def then_report_has_row(m, params):
    func_name = m.group(1)
    expected_cc = int(m.group(2))
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify '{func_name}' CC={expected_cc} in report")
        return
    actual_cc = _extract_cc(ctx.report_output, func_name)
    assert actual_cc is not None, (
        f"Function '{func_name}' not found in report output:\n{ctx.report_output}"
    )
    assert actual_cc == expected_cc, (
        f"Report CC mismatch for '{func_name}': expected {expected_cc}, got {actual_cc}"
    )


