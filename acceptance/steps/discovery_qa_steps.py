"""Step handlers for features/discovery_qa.feature (C2, #8).

End-to-end QA for C2: verifies function discovery through the crap4py CLI.

NOT AUTOMATED: All scenarios require 'uv run crap4py --lcov <lcov> <src>' to
produce a report. The CLI entrypoint (__main__.py) and report formatter (C4)
are not yet implemented. Steps are guarded — the harness skips gracefully when
the CLI is absent. Re-enable by removing the CLI_AVAILABLE guard once C4 lands.
"""
import os
import sys

from acceptance.steps.step_lib import make_registry, check_cli_available, run_cli, QAState

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_C2_FIXTURE_ROOT = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c2_fixture")
_C2_FIXTURE_LCOV = os.path.join(_REPO_ROOT, "acceptance", "fixtures", "c2_fixture.lcov")

STEP_HANDLERS, step, run_step = make_registry()

CLI_AVAILABLE = check_cli_available()
ctx = QAState(_C2_FIXTURE_ROOT, _C2_FIXTURE_LCOV)


def _run_cli() -> str:
    return run_cli(ctx.lcov_path, ctx.source_path, CLI_AVAILABLE)


def _has_row_for(report: str, qualified: str) -> bool:
    for line in report.splitlines():
        if qualified in line:
            return True
    return False


def _module_for(report: str, qualified: str) -> str | None:
    for line in report.splitlines():
        if qualified in line:
            return line
    return None


# --- Background ---

@step(r"a committed Python fixture tree and a matching LCOV file")
def given_fixture_tree(m, params):
    assert os.path.isdir(ctx.source_path), f"Fixture dir missing: {ctx.source_path}"
    assert os.path.isfile(ctx.lcov_path), f"Fixture LCOV missing: {ctx.lcov_path}"


@step(r'the command "uv run crap4py --lcov <lcov> <root>" has been run')
def given_command_run(m, params):
    ctx.report_output = _run_cli()


# --- qa-discovery-1: report has row for each discovered function ---

@step(r'the fixture defines a function whose expected qualified name is "(.+)"')
def given_expected_qualified(m, params):
    qualified = params.get("qualified") or m.group(1)
    # Verify fixture source contains this function
    sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.discovery import discover_functions
    entries = discover_functions([_C2_FIXTURE_ROOT], root=_REPO_ROOT)
    names = [e.qualified_name for e in entries]
    assert qualified in names, f"Fixture missing '{qualified}'; discovered: {names}"


@step(r"the report is produced")
def when_report_produced(m, params):
    ctx.report_output = _run_cli()


@step(r'the report has a row for "(.+)"')
def then_report_has_row(m, params):
    qualified = params.get("qualified") or m.group(1)
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify '{qualified}' in report")
        return
    assert _has_row_for(ctx.report_output, qualified), (
        f"Report has no row for '{qualified}':\n{ctx.report_output}"
    )


# --- qa-discovery-2: nested function appears as its own row ---

@step(r'the fixture defines a function "(.+)" containing a nested function "(.+)"')
def given_fixture_nested(m, params):
    outer = params.get("outer") or m.group(1)
    inner = params.get("inner") or m.group(2)
    sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.discovery import discover_functions
    entries = discover_functions([_C2_FIXTURE_ROOT], root=_REPO_ROOT)
    names = [e.qualified_name for e in entries]
    assert outer in names, f"Fixture missing outer '{outer}'; got {names}"
    assert inner in names, f"Fixture missing inner '{inner}'; got {names}"


# --- qa-discovery-3: decorated method keeps def name ---

@step(r'the fixture defines a "(.+)" method "(.+)" on class "(.+)"')
def given_fixture_decorated_method(m, params):
    decorator = params.get("decorator") or m.group(1)
    method = params.get("method") or m.group(2)
    cls = params.get("cls") or m.group(3)
    expected = f"{cls}.{method}"
    sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.discovery import discover_functions
    entries = discover_functions([_C2_FIXTURE_ROOT], root=_REPO_ROOT)
    names = [e.qualified_name for e in entries]
    assert expected in names, f"Fixture missing '{expected}'; got {names}"


# --- qa-discovery-4: module column shows file path ---

@step(r'the fixture defines function "(.+)" in file "(.+)"')
def given_function_in_file(m, params):
    function = params.get("function") or m.group(1)
    rel_path = params.get("rel_path") or m.group(2)
    sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))
    from crap4py.discovery import discover_functions
    entries = discover_functions([_C2_FIXTURE_ROOT], root=_REPO_ROOT)
    matching = [e for e in entries if e.qualified_name == function]
    assert matching, f"No entry '{function}' in fixture; got {[e.qualified_name for e in entries]}"
    actual_label = matching[0].module_label
    assert rel_path in actual_label, (
        f"Module label for '{function}': expected '{rel_path}' in '{actual_label}'"
    )


@step(r'the report row for "(.+)" shows module "(.+)"')
def then_report_row_shows_module(m, params):
    function = params.get("function") or m.group(1)
    rel_path = params.get("rel_path") or m.group(2)
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify '{function}' module='{rel_path}'")
        return
    line = _module_for(ctx.report_output, function)
    assert line is not None, f"No report row for '{function}':\n{ctx.report_output}"
    assert rel_path in line, f"Module '{rel_path}' not found in row: {line}"


# --- qa-discovery-5: test files absent ---

@step(r'the fixture tree includes a test file "(.+)" defining a function "(.+)"')
def given_fixture_test_file(m, params):
    test_file = params.get("test_file") or m.group(1)
    test_function = params.get("test_function") or m.group(2)
    full_path = os.path.join(_C2_FIXTURE_ROOT, test_file)
    assert os.path.isfile(full_path), f"Test fixture file missing: {full_path}"


@step(r'the report has no row for "(.+)"')
def then_report_no_row_for(m, params):
    name = params.get("test_function") or params.get("ignored_function") or m.group(1)
    if not CLI_AVAILABLE:
        print(f"NOT AUTOMATED — CLI absent: cannot verify absence of '{name}' in report")
        return
    assert not _has_row_for(ctx.report_output, name), (
        f"Report should not have row for '{name}':\n{ctx.report_output}"
    )


# --- qa-discovery-6: gitignored files absent ---

@step(r'the fixture tree\'s `\.gitignore` ignores "(.+)" which defines a function "(.+)"')
def given_fixture_gitignored(m, params):
    ignored_path = params.get("ignored_path") or m.group(1)
    ignored_function = params.get("ignored_function") or m.group(2)
    full_path = os.path.join(_C2_FIXTURE_ROOT, ignored_path)
    assert os.path.isfile(full_path), f"Gitignored fixture file missing: {full_path}"
    gitignore = os.path.join(_C2_FIXTURE_ROOT, ".gitignore")
    assert os.path.isfile(gitignore), f".gitignore missing in fixture: {gitignore}"
