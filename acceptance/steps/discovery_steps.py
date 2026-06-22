"""Step handlers for features/discovery.feature (C2, #8)."""
import ast
import os
import sys
import textwrap
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from crap4py.discovery import FunctionEntry, _extract_entries, discover_functions
from acceptance.steps.step_lib import make_registry

STEP_HANDLERS, step, run_step = make_registry()


class Context:
    def __init__(self):
        self.entries: list[FunctionEntry] = []
        self.tmpdir: str | None = None
        self.source: str = ""


ctx = Context()


def _parse_source(source: str, label: str = "test.py") -> list[FunctionEntry]:
    tree = ast.parse(textwrap.dedent(source))
    return _extract_entries(tree, label)


# --- Background ---

@step(r"a Python project whose source is discovered from its root")
def given_python_project(m, params):
    ctx.entries = []
    ctx.source = ""


# --- discovery-1: module-level function ---

@step(r'a source file defining a top-level function "(.+)"')
def given_top_level_function(m, params):
    name = params.get("def_name") or m.group(1)
    ctx.source = f"def {name}(): pass\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-2: method inside class ---

@step(r'a source file defining method "([^"]+)" inside class "([^"]+)"')
def given_method_in_class(m, params):
    method = params.get("method") or m.group(1)
    cls = params.get("cls") or m.group(2)
    ctx.source = f"class {cls}:\n    def {method}(self): pass\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-3: nested class ---

@step(r'a source file defining method "([^"]+)" inside class "([^"]+)" nested in class "([^"]+)"')
def given_nested_class_method(m, params):
    method = params.get("method") or m.group(1)
    inner = params.get("inner") or m.group(2)
    outer = params.get("outer") or m.group(3)
    ctx.source = f"class {outer}:\n    class {inner}:\n        def {method}(self): pass\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-4: nested functions ---

@step(r'a source file where function "(.+)" contains a nested function "(.+)"')
def given_nested_function(m, params):
    outer = params.get("outer") or m.group(1)
    inner = params.get("inner") or m.group(2)
    ctx.source = f"def {outer}():\n    def {inner}():\n        pass\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-5: async def ---

@step(r'a source file defining an async function "(.+)"')
def given_async_function(m, params):
    name = params.get("def_name") or m.group(1)
    ctx.source = f"async def {name}(): pass\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-6: decorated method ---

@step(r'a source file defining method "(.+)" in class "(.+)" decorated with "(.+)"')
def given_decorated_method(m, params):
    method = params.get("method") or m.group(1)
    cls = params.get("cls") or m.group(2)
    decorator = params.get("decorator") or m.group(3)
    ctx.source = f"class {cls}:\n    {decorator}\n    def {method}(self): pass\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-7: @overload stubs ---

@step(r'a source file with (\d+) `@overload` stubs named "(.+)" and one implementation named "(.+)"')
def given_overload_stubs(m, params):
    stub_count = int(params.get("stub_count") or m.group(1))
    name = params.get("def_name") or m.group(2)
    lines = ["from typing import overload"]
    for _ in range(stub_count):
        lines.append("@overload")
        lines.append(f"def {name}(x): ...")
    lines.append(f"def {name}(x): return x")
    ctx.source = "\n".join(lines) + "\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-8: module label ---

@step(r'a source file at relative path "(.+)" defining a function "(.+)"')
def given_source_at_path(m, params):
    rel_path = params.get("rel_path") or m.group(1)
    name = params.get("def_name") or m.group(2)
    ctx.source = f"def {name}(): pass\n"
    ctx.entries = _parse_source(ctx.source, label=rel_path)


# --- discovery-9: line range ---

@step(r'a source file where function "(.+)" spans lines (\d+) to (\d+)')
def given_function_spans(m, params):
    name = params.get("def_name") or m.group(1)
    start = int(params.get("start") or m.group(2))
    end = int(params.get("end") or m.group(3))
    prefix_lines = start - 1
    body_lines = end - start
    prefix = "\n".join(["x = 1"] * prefix_lines) + "\n" if prefix_lines else ""
    stmts = "\n    ".join(["pass"] * max(1, body_lines))
    ctx.source = f"{prefix}def {name}():\n    {stmts}\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-10: decorated function range starts at def ---

@step(r'a source file where function "(.+)" has a decorator on line (\d+) and `def` on line (\d+) ending on line (\d+)')
def given_decorated_function_lines(m, params):
    name = params.get("def_name") or m.group(1)
    decorator_line = int(params.get("decorator_line") or m.group(2))
    def_line = int(params.get("def_line") or m.group(3))
    end = int(params.get("end") or m.group(4))
    prefix_lines = decorator_line - 1
    body_lines = end - def_line
    prefix = "\n".join(["x = 1"] * prefix_lines) + "\n" if prefix_lines else ""
    stmts = "\n    ".join(["pass"] * max(1, body_lines))
    ctx.source = f"{prefix}@decorator\ndef {name}():\n    {stmts}\n"
    ctx.entries = _parse_source(ctx.source)


# --- discovery-11: test files skipped ---

@step(r'a source tree containing a non-test file "(.+)" and a test file "(.+)"')
def given_tree_with_test_file(m, params):
    source_file = params.get("source") or m.group(1)
    test_file = params.get("test_file") or m.group(2)
    import tempfile, shutil
    d = tempfile.mkdtemp()
    ctx.tmpdir = d
    # Create source file with a unique sentinel function
    src_parts = source_file.split("/")
    src_dir = os.path.join(d, *src_parts[:-1])
    os.makedirs(src_dir, exist_ok=True)
    with open(os.path.join(d, *src_parts), "w") as f:
        f.write("def src_sentinel(): pass\n")
    # Create test file with a unique function
    tst_parts = test_file.split("/")
    tst_dir = os.path.join(d, *tst_parts[:-1])
    os.makedirs(tst_dir, exist_ok=True)
    with open(os.path.join(d, *tst_parts), "w") as f:
        f.write("def test_sentinel(): pass\n")
    old_cwd = os.getcwd()
    os.chdir(d)
    ctx.entries = discover_functions([d])
    os.chdir(old_cwd)
    if ctx.tmpdir:
        import shutil
        shutil.rmtree(ctx.tmpdir, ignore_errors=True)
        ctx.tmpdir = None
    # Store expected labels for assertions
    ctx._source_label = source_file
    ctx._test_label = test_file


# --- discovery-12: .gitignore paths skipped ---

@step(r'a project whose `\.gitignore` ignores "(.+)"')
def given_gitignore_ignores(m, params):
    ignored_path = params.get("ignored_path") or m.group(1)
    import tempfile
    d = tempfile.mkdtemp()
    ctx.tmpdir = d
    ctx._ignored_path = ignored_path
    ctx._ignored_label = ignored_path


@step(r'a non-ignored source file "(.+)"')
def given_non_ignored_source(m, params):
    kept_path = params.get("kept_path") or m.group(1)
    d = ctx.tmpdir
    # Write gitignore
    ignored = ctx._ignored_path
    ignored_parts = ignored.split("/")
    ignored_dir = os.path.join(d, *ignored_parts[:-1])
    os.makedirs(ignored_dir, exist_ok=True)
    with open(os.path.join(d, *ignored_parts), "w") as f:
        f.write("def ignored_fn(): pass\n")
    # Write .gitignore
    gitignore_pattern = ignored_parts[0] + "/" if len(ignored_parts) > 1 else ignored
    with open(os.path.join(d, ".gitignore"), "w") as f:
        f.write(gitignore_pattern + "\n")
    # Write kept file
    kept_parts = kept_path.split("/")
    kept_dir = os.path.join(d, *kept_parts[:-1])
    os.makedirs(kept_dir, exist_ok=True)
    with open(os.path.join(d, *kept_parts), "w") as f:
        f.write("def kept_fn(): pass\n")
    old_cwd = os.getcwd()
    os.chdir(d)
    ctx.entries = discover_functions([d])
    os.chdir(old_cwd)
    import shutil
    shutil.rmtree(d, ignore_errors=True)
    ctx.tmpdir = None
    ctx._kept_label = kept_path


# --- "When functions are discovered" (no-op: discovery already done in Given) ---

@step(r"functions are discovered")
def when_functions_discovered(m, params):
    pass


# --- Then steps ---

@step(r'an entry exists with qualified name "(.+)"')
def then_entry_exists(m, params):
    expected = params.get("qualified") or m.group(1)
    ns = [e.qualified_name for e in ctx.entries]
    assert expected in ns, f"Expected entry '{expected}' but got: {ns}"


@step(r'(\d+) entries exist with qualified name "(.+)"')
def then_n_entries_with_name(m, params):
    count = int(params.get("entry_count") or m.group(1))
    name = params.get("def_name") or m.group(2)
    ns = [e.qualified_name for e in ctx.entries]
    actual = ns.count(name)
    assert actual == count, f"Expected {count} entries named '{name}', got {actual}: {ns}"


@step(r'the entry for "(.+)" has module label "(.+)"')
def then_entry_has_module_label(m, params):
    name = params.get("def_name") or m.group(1)
    expected_label = params.get("rel_path") or m.group(2)
    matching = [e for e in ctx.entries if e.qualified_name == name]
    assert matching, f"No entry with name '{name}'; got {[e.qualified_name for e in ctx.entries]}"
    actual = matching[0].module_label
    assert actual == expected_label, f"Module label for '{name}': expected '{expected_label}', got '{actual}'"


@step(r'the entry for "(.+)" has line range (\d+) to (\d+)')
def then_entry_has_line_range(m, params):
    name = params.get("def_name") or m.group(1)
    start = int(params.get("start") or m.group(2))
    end = int(params.get("end") or m.group(3))
    matching = [e for e in ctx.entries if e.qualified_name == name]
    assert matching, f"No entry named '{name}'; got {[e.qualified_name for e in ctx.entries]}"
    actual = matching[0].line_range
    assert actual == (start, end), f"Line range for '{name}': expected ({start},{end}), got {actual}"


@step(r'entries come only from "(.+)"')
def then_entries_only_from(m, params):
    source = params.get("source") or params.get("kept_path") or m.group(1)
    labels = [e.module_label for e in ctx.entries]
    for label in labels:
        assert os.path.basename(label) == os.path.basename(source) or label == source, (
            f"Unexpected entry from '{label}'; expected only '{source}'"
        )


@step(r'no entry has module label "(.+)"')
def then_no_entry_with_label(m, params):
    label = params.get("test_file") or params.get("ignored_path") or m.group(1)
    labels = [e.module_label for e in ctx.entries]
    matches = [l for l in labels if os.path.basename(l) == os.path.basename(label) or l == label]
    assert not matches, f"Entries from '{label}' should not appear but got: {matches}"
