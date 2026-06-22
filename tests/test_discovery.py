"""Unit tests for function discovery and qualified naming (C2, #8).

Per ADR 0003: qualified name uses enclosing classes only; module label is
cwd-relative file path; line range is the def node's own span.
"""
import ast
import os
import textwrap
import pytest
from crap4py.discovery import FunctionEntry, _extract_entries, discover_functions
from crap4py._discovery_io import collect_source_files as _collect_source_files, relative_label


def parse_entries(source: str, label: str = "test.py") -> list[FunctionEntry]:
    tree = ast.parse(textwrap.dedent(source))
    return _extract_entries(tree, label)


def names(entries: list[FunctionEntry]) -> list[str]:
    return [e.qualified_name for e in entries]


# --- discovery-1: module-level function is its own name ---

def test_module_level_function_name():
    entries = parse_entries("def extract_functions(): pass\n")
    assert names(entries) == ["extract_functions"]


def test_module_level_private_function():
    entries = parse_entries("def _private(): pass\n")
    assert names(entries) == ["_private"]


# --- discovery-2: method qualified by enclosing class ---

def test_method_qualified_by_class():
    src = """
class Function:
    def score(self): pass
"""
    entries = parse_entries(src)
    assert "Function.score" in names(entries)


def test_method_qualified_report():
    src = """
class Report:
    def render(self): pass
"""
    entries = parse_entries(src)
    assert "Report.render" in names(entries)


# --- discovery-3: nested classes ---

def test_nested_class_method():
    src = """
class Outer:
    class Inner:
        def run(self): pass
"""
    entries = parse_entries(src)
    assert "Outer.Inner.run" in names(entries)


# --- discovery-4: nested functions keep their own name ---

def test_nested_function_separate_entries():
    src = """
def compute():
    def helper():
        pass
"""
    ns = names(parse_entries(src))
    assert "compute" in ns
    assert "helper" in ns


def test_nested_function_not_qualified_by_outer():
    src = """
def compute():
    def helper():
        pass
"""
    ns = names(parse_entries(src))
    assert "compute.helper" not in ns


# --- discovery-5: async def ---

def test_async_def_discovered():
    entries = parse_entries("async def fetch(): pass\n")
    assert "fetch" in names(entries)


# --- discovery-6: decorators don't change name ---

def test_property_keeps_def_name():
    src = """
class User:
    @property
    def name(self): return self._name
"""
    assert "User.name" in names(parse_entries(src))


def test_staticmethod_keeps_def_name():
    src = """
class Math:
    @staticmethod
    def of(x): return x
"""
    assert "Math.of" in names(parse_entries(src))


# --- discovery-7: @overload stubs each become their own entry ---

def test_overload_stubs_all_appear():
    src = """
from typing import overload

@overload
def parse(x: int) -> int: ...

@overload
def parse(x: str) -> str: ...

def parse(x):
    return x
"""
    ns = names(parse_entries(src))
    assert ns.count("parse") == 3


# --- discovery-8: module label is cwd-relative path ---

def test_module_label_is_rel_path():
    src = "def parse(): pass\n"
    entries = parse_entries(src, label="src/crap4py/complexity.py")
    assert entries[0].module_label == "src/crap4py/complexity.py"


def test_module_label_scripts():
    src = "def main(): pass\n"
    entries = parse_entries(src, label="scripts/tool.py")
    assert entries[0].module_label == "scripts/tool.py"


# --- discovery-9: line range spans the def node ---

def test_line_range_plain():
    src = "def plain():\n    pass\n"
    entries = parse_entries(src)
    assert entries[0].line_range == (1, 2)


def test_line_range_wide():
    src = textwrap.dedent("""\
        x = 1
        y = 2
        z = 3
        w = 4
        def wide():
            a = 1
            b = 2
            c = 3
            d = 4
            e = 5
            f = 6
            return a
    """)
    entries = parse_entries(src)
    assert entries[0].qualified_name == "wide"
    assert entries[0].line_range == (5, 12)


# --- discovery-10: decorated function range starts at def line ---

def test_decorated_range_starts_at_def():
    src = textwrap.dedent("""\
        x = 1
        y = 2
        @decorator
        def routed():
            a = 1
            return a
    """)
    entries = parse_entries(src)
    assert entries[0].qualified_name == "routed"
    start, end = entries[0].line_range
    assert start == 4
    assert end == 6


# --- discovery-11: test files are skipped ---

def test_test_prefix_file_skipped(tmp_path):
    (tmp_path / "test_cli.py").write_text("def test_runs(): pass\n")
    (tmp_path / "cli.py").write_text("def main(): pass\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "test_runs" not in ns


def test_test_suffix_file_skipped(tmp_path):
    (tmp_path / "cli_test.py").write_text("def test_it(): pass\n")
    (tmp_path / "cli.py").write_text("def run(): pass\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "run" in ns
    assert "test_it" not in ns


# --- discovery-12: .gitignore paths not scored ---

def test_gitignored_path_skipped(tmp_path):
    ignored_dir = tmp_path / ".venv" / "lib"
    ignored_dir.mkdir(parents=True)
    (ignored_dir / "site.py").write_text("def ignored_fn(): pass\n")
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "cli.py").write_text("def kept(): pass\n")
    (tmp_path / ".gitignore").write_text(".venv/\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "kept" in ns
    assert "ignored_fn" not in ns


def test_build_dir_gitignored(tmp_path):
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "generated.py").write_text("def gen(): pass\n")
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "cli.py").write_text("def kept(): pass\n")
    (tmp_path / ".gitignore").write_text("build/\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "kept" in ns
    assert "gen" not in ns


# --- discovery-13: error resilience ---

def test_unreadable_file_skipped(tmp_path):
    src_file = tmp_path / "good.py"
    src_file.write_text("def good(): pass\n")
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def bad(): pass\n")
    bad_file.chmod(0o000)
    try:
        entries = discover_functions([str(tmp_path)], root=str(tmp_path))
        ns = names(entries)
        assert "good" in ns
        assert "bad" not in ns
    finally:
        bad_file.chmod(0o644)


def test_syntax_error_file_skipped(tmp_path):
    (tmp_path / "broken.py").write_text("def broken(\n")
    (tmp_path / "fine.py").write_text("def fine(): pass\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "fine" in ns
    assert "broken" not in ns


# --- discovery-14: non-py file passed directly is ignored ---

def test_non_py_file_path_ignored(tmp_path):
    (tmp_path / "notes.txt").write_text("def foo(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    entries = discover_functions(
        [str(tmp_path / "notes.txt"), str(tmp_path / "main.py")],
        root=str(tmp_path),
    )
    ns = names(entries)
    assert "main" in ns
    assert "foo" not in ns


# --- discovery-15: gitignore with comments and blank lines ---

def test_gitignore_comments_and_blanks_ignored(tmp_path):
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("# comment\n\n*.pyc\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns


# --- discovery-16: gitignore path-pattern (contains slash) ---

def test_gitignore_slash_pattern_matches_path(tmp_path):
    nested = tmp_path / "dist" / "pkg"
    nested.mkdir(parents=True)
    (nested / "bundle.py").write_text("def bundled(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("dist/\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "bundled" not in ns


def test_gitignore_exact_path_pattern(tmp_path):
    special = tmp_path / "vendor" / "lib.py"
    special.parent.mkdir()
    special.write_text("def vendored(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("vendor/lib.py\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "vendored" not in ns


# --- discovery-17: gitignore glob matching by name component ---

def test_gitignore_glob_name_pattern(tmp_path):
    (tmp_path / "generated_code.py").write_text("def gen(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("generated_*.py\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "gen" not in ns


# --- discovery-18: class inside function body ---

def test_class_inside_function_not_collected(tmp_path):
    src = """
def outer():
    class Local:
        def method(self): pass
    return Local()
"""
    entries = parse_entries(src)
    ns = names(entries)
    assert "outer" in ns
    assert "Local.method" in ns


# --- discovery-19: non-gitignore file in _walk_dir skipped when gitignored ---

def test_gitignored_file_path_directly_skipped(tmp_path):
    cached = tmp_path / "cached.py"
    cached.write_text("def cached(): pass\n")
    (tmp_path / ".gitignore").write_text("cached.py\n")
    entries = discover_functions([str(cached)], root=str(tmp_path))
    assert names(entries) == []


def test_nonexistent_path_ignored(tmp_path):
    entries = discover_functions([str(tmp_path / "missing.py")], root=str(tmp_path))
    assert entries == []


def test_gitignore_exact_file_match(tmp_path):
    special = tmp_path / "lib.py"
    special.write_text("def lib_fn(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("lib.py\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "lib_fn" not in ns


def test_gitignore_dir_slash_exact_rel_match(tmp_path):
    # covers _fnmatch_path line 86: rel == p (dir without trailing slash in pattern)
    # Pattern "out" matches a directory named "out" that is the exact relative path
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "result.py").write_text("def result(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("out/\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "result" not in ns


def test_gitignore_glob_path_component(tmp_path):
    # covers _fnmatch_path line 92: matching a path component inside a subdir
    # when the file name itself doesn't match the pattern
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "helpers.py").write_text("def help_fn(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("sub\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "help_fn" not in ns


def test_walk_dir_gitignored_file_skipped(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "cached.py").write_text("def cached(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("sub/cached.py\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "cached" not in ns


# --- mutant killers ---

def test_relative_label_no_root_uses_cwd(tmp_path):
    filepath = str(tmp_path / "mod.py")
    cwd = os.getcwd()
    expected = os.path.relpath(filepath, cwd)
    assert relative_label(filepath) == expected
    assert relative_label(filepath, None) == expected


def test_relative_label_explicit_root_differs_from_cwd(tmp_path):
    parent = tmp_path / "project"
    parent.mkdir()
    filepath = str(parent / "src" / "mod.py")
    label_with_root = relative_label(filepath, str(parent))
    label_with_cwd = relative_label(filepath, os.getcwd())
    assert label_with_root != label_with_cwd or str(parent) == os.getcwd()
    assert label_with_root == os.path.relpath(filepath, str(parent))


def test_gitignore_trailing_slash_in_pattern_stripped(tmp_path):
    ignored = tmp_path / "build"
    ignored.mkdir()
    (ignored / "out.py").write_text("def gen(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("build/\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "gen" not in ns


def test_gitignore_pattern_ending_with_x_still_matches(tmp_path):
    ignored = tmp_path / "fooX"
    ignored.mkdir()
    (ignored / "mod.py").write_text("def hidden(): pass\n")
    (tmp_path / "main.py").write_text("def main(): pass\n")
    (tmp_path / ".gitignore").write_text("fooX/\n")
    entries = discover_functions([str(tmp_path)], root=str(tmp_path))
    ns = names(entries)
    assert "main" in ns
    assert "hidden" not in ns
