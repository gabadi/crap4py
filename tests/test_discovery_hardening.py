"""Mutation-hardening tests for discovery and _discovery_io (C2, #8).

These tests kill surviving mutants from the hardender's mutation run.
They are kept separate from unit tests per swarmforge engineering rules.
"""
import ast
import os
import textwrap

import pytest

from crap4py._discovery_io import (
    _fnmatch_path,
    _is_gitignored,
    _load_gitignore_patterns,
    _match_name_pattern,
    _match_path_pattern,
    _walk_dir,
    collect_source_files,
    read_source,
    relative_label,
)
from crap4py.discovery import FunctionEntry, _extract_entries, discover_functions


def parse_entries(source: str, label: str = "test.py") -> list[FunctionEntry]:
    tree = ast.parse(textwrap.dedent(source))
    return _extract_entries(tree, label)


def names(entries: list[FunctionEntry]) -> list[str]:
    return [e.qualified_name for e in entries]


# --- discover_functions guard: each adapter arm is individually optional ---

def test_discover_functions_only_collect_files_missing(tmp_path):
    """Guard condition: pass read_source and file_label, omit collect_files."""
    (tmp_path / "mod.py").write_text("def fn(): pass\n")

    def my_read(fp):
        with open(fp) as f:
            return f.read()

    def my_label(fp):
        return "custom"

    entries = discover_functions(
        [str(tmp_path / "mod.py")],
        collect_files=None,
        read_source=my_read,
        file_label=my_label,
    )
    assert names(entries) == ["fn"]
    assert entries[0].module_label == "custom"


def test_discover_functions_only_read_source_missing(tmp_path):
    """Guard condition: pass collect_files and file_label, omit read_source."""
    fp = str(tmp_path / "mod.py")
    (tmp_path / "mod.py").write_text("def fn(): pass\n")

    def my_collect(paths):
        return [fp]

    def my_label(f):
        return "lbl"

    entries = discover_functions(
        [str(tmp_path)],
        collect_files=my_collect,
        read_source=None,
        file_label=my_label,
    )
    assert names(entries) == ["fn"]


def test_discover_functions_only_file_label_missing(tmp_path):
    """Guard condition: pass collect_files and read_source, omit file_label."""
    fp = str(tmp_path / "mod.py")
    (tmp_path / "mod.py").write_text("def fn(): pass\n")

    def my_collect(paths):
        return [fp]

    def my_read(f):
        with open(f) as fh:
            return fh.read()

    entries = discover_functions(
        [str(tmp_path)],
        collect_files=my_collect,
        read_source=my_read,
        file_label=None,
        root=str(tmp_path),
    )
    assert names(entries) == ["fn"]
    assert entries[0].module_label == "mod.py"


# --- file_label captures root, not None ---

def test_file_label_uses_root_not_cwd(tmp_path):
    """root must be passed into _label_fn, not None/dropped."""
    sub = tmp_path / "project" / "src"
    sub.mkdir(parents=True)
    fp = str(sub / "mod.py")
    (sub / "mod.py").write_text("def fn(): pass\n")

    root = str(tmp_path / "project")
    entries = discover_functions([fp], root=root)
    assert entries[0].module_label == os.path.join("src", "mod.py")


def test_file_label_root_differs_from_cwd(tmp_path):
    """label_fn(fp, root) must differ from label_fn(fp, None) when root != cwd."""
    sub = tmp_path / "deep" / "nested"
    sub.mkdir(parents=True)
    fp = str(sub / "mod.py")
    (sub / "mod.py").write_text("def fn(): pass\n")

    entries_with_root = discover_functions([fp], root=str(tmp_path))
    label_with_root = entries_with_root[0].module_label

    cwd = os.getcwd()
    if str(tmp_path) != cwd:
        entries_cwd = discover_functions([fp])
        label_with_cwd = entries_cwd[0].module_label
        assert label_with_root != label_with_cwd


# --- label is propagated, not replaced with None ---

def test_file_label_appears_in_entry(tmp_path):
    """label=file_label(filepath), not None, must reach FunctionEntry.module_label."""
    fp = str(tmp_path / "mod.py")
    (tmp_path / "mod.py").write_text("def fn(): pass\n")

    sentinel = "SENTINEL_LABEL"
    entries = discover_functions(
        [fp],
        collect_files=lambda ps: [fp],
        read_source=lambda f: open(f).read(),
        file_label=lambda f: sentinel,
    )
    assert len(entries) == 1
    assert entries[0].module_label == sentinel


# --- ast.parse filename= matters: captured in SyntaxError, not tested here ---
# ast.parse with filename= doesn't affect result for valid source;
# the meaningful check is that entries come back correctly:

def test_ast_parse_returns_entries_for_valid_source(tmp_path):
    """Sanity: entries are produced (killing mutmut_34 indirectly via label check)."""
    fp = str(tmp_path / "mod.py")
    (tmp_path / "mod.py").write_text("def fn(): pass\n")
    entries = discover_functions([fp], root=str(tmp_path))
    assert names(entries) == ["fn"]


# --- _extract_entries passes module_label through, not None ---

def test_extract_entries_module_label_propagated_to_nested():
    """module_label must reach nested function entries, not become None."""
    src = textwrap.dedent("""\
        class A:
            def method(self):
                pass
            class B:
                def inner(self): pass
    """)
    entries = parse_entries(src, label="my_label")
    for e in entries:
        assert e.module_label == "my_label"


def test_collect_function_propagates_module_label_to_nested_fn():
    """Nested function inside function must keep module_label."""
    src = textwrap.dedent("""\
        def outer():
            def inner(): pass
    """)
    entries = parse_entries(src, label="file.py")
    labels = [e.module_label for e in entries]
    assert all(lb == "file.py" for lb in labels)


def test_collect_scope_propagates_module_label_through_class():
    """Class inside function must keep module_label in its collected entries."""
    src = textwrap.dedent("""\
        def outer():
            class Inner:
                def method(self): pass
    """)
    entries = parse_entries(src, label="module.py")
    method_entries = [e for e in entries if "method" in e.qualified_name]
    assert method_entries
    for e in method_entries:
        assert e.module_label == "module.py"


# --- read_source encoding: "utf-8" must be preserved ---

def test_read_source_reads_utf8_content(tmp_path):
    """read_source must decode utf-8 correctly (kills encoding=None/empty mutants)."""
    fp = str(tmp_path / "mod.py")
    content = "# café\ndef fn(): pass\n"
    (tmp_path / "mod.py").write_bytes(content.encode("utf-8"))
    result = read_source(fp)
    assert result == content


def test_read_source_returns_none_on_missing_file(tmp_path):
    assert read_source(str(tmp_path / "missing.py")) is None


# --- collect_source_files passes cwd through to gitignore check ---

def test_collect_source_files_cwd_matters_for_gitignore(tmp_path):
    """When root= is explicit, gitignore is loaded relative to root, not os.getcwd()."""
    (tmp_path / "lib.py").write_text("def fn(): pass\n")
    (tmp_path / ".gitignore").write_text("lib.py\n")
    result = collect_source_files([str(tmp_path)], root=str(tmp_path))
    assert result == []


def test_collect_source_files_no_gitignore_includes_file(tmp_path):
    """Without gitignore, file must be collected."""
    (tmp_path / "lib.py").write_text("def fn(): pass\n")
    result = collect_source_files([str(tmp_path)], root=str(tmp_path))
    assert any("lib.py" in r for r in result)


# --- _walk_dir must use os.path.join(dirpath, d), not just d ---

def test_walk_dir_uses_full_dir_path_for_gitignore(tmp_path):
    """_walk_dir must pass os.path.join(dirpath, d) to gitignore, not just d."""
    sub = tmp_path / "deep" / "ignored_dir"
    sub.mkdir(parents=True)
    (sub / "hidden.py").write_text("def secret(): pass\n")
    keep = tmp_path / "deep" / "kept"
    keep.mkdir()
    (keep / "visible.py").write_text("def visible(): pass\n")
    (tmp_path / ".gitignore").write_text("ignored_dir\n")
    files = _walk_dir(str(tmp_path), ["ignored_dir"], str(tmp_path))
    filenames = [os.path.basename(f) for f in files]
    assert "visible.py" in filenames
    assert "hidden.py" not in filenames


def test_walk_dir_empty_dir_returns_empty(tmp_path):
    sub = tmp_path / "empty"
    sub.mkdir()
    files = _walk_dir(str(sub), [], str(tmp_path))
    assert files == []


# --- _load_gitignore_patterns filtering ---

def test_load_gitignore_strips_trailing_newline(tmp_path):
    (tmp_path / ".gitignore").write_text("build/\n*.pyc\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "build/" in patterns
    assert "*.pyc" in patterns


def test_load_gitignore_excludes_comment_lines(tmp_path):
    """Lines starting with # must be excluded (kills startswith("XX#XX") mutant)."""
    (tmp_path / ".gitignore").write_text("# this is a comment\nbuild/\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "# this is a comment" not in patterns
    assert "build/" in patterns


def test_load_gitignore_excludes_blank_lines(tmp_path):
    """Empty lines after rstrip must be excluded (kills or→or mutant)."""
    (tmp_path / ".gitignore").write_text("\nbuild/\n\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "" not in patterns
    assert "build/" in patterns


def test_load_gitignore_line_with_only_newline_is_excluded(tmp_path):
    """A line that is only \\n rstrips to '' and must not appear in patterns."""
    (tmp_path / ".gitignore").write_text("\n*.pyc\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "" not in patterns
    assert "*.pyc" in patterns


def test_load_gitignore_comment_line_excluded_even_without_blank(tmp_path):
    """Comment filter must fire on non-blank comment lines."""
    (tmp_path / ".gitignore").write_text("#comment\nsrc/\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "#comment" not in patterns
    assert "src/" in patterns


def test_load_gitignore_no_file_returns_empty(tmp_path):
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert patterns == []


def test_load_gitignore_reads_correct_filename(tmp_path):
    """Must open .gitignore, not .GITIGNORE."""
    (tmp_path / ".gitignore").write_text("dist/\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "dist/" in patterns


# --- _is_gitignored: backslash replacement ---

def test_is_gitignored_basic_match(tmp_path):
    """Baseline: a matching pattern ignores the file."""
    fp = str(tmp_path / "build" / "out.py")
    os.makedirs(str(tmp_path / "build"))
    open(fp, "w").close()
    assert _is_gitignored(fp, ["build"], str(tmp_path))


def test_is_gitignored_non_matching_not_ignored(tmp_path):
    fp = str(tmp_path / "src" / "main.py")
    os.makedirs(str(tmp_path / "src"))
    open(fp, "w").close()
    assert not _is_gitignored(fp, ["build"], str(tmp_path))


# --- _fnmatch_path: lstrip("/") on path patterns with leading slash ---

def test_fnmatch_path_leading_slash_stripped(tmp_path):
    """Pattern /src/lib.py: lstrip('/') must produce src/lib.py."""
    assert _fnmatch_path("src/lib.py", "lib.py", "/src/lib.py")


def test_fnmatch_path_no_leading_slash(tmp_path):
    """Pattern without leading slash still works via _match_path_pattern."""
    assert _fnmatch_path("src/lib.py", "lib.py", "src/lib.py")


def test_fnmatch_path_leading_slash_vs_rstrip(tmp_path):
    """lstrip('/') and rstrip('/') must differ in result for /build/ pattern."""
    # /build/ -> rstrip('/') -> /build -> lstrip('/') -> build
    # rstrip('/') on /build gives build (correct), not /build
    assert _fnmatch_path("build/out.py", "out.py", "/build/")


# --- _match_path_pattern: or logic, not and ---

def test_match_path_pattern_fnmatch_hit(tmp_path):
    """fnmatch.fnmatch wins: src/*.py matches src/mod.py."""
    assert _match_path_pattern("src/mod.py", "src/*.py")


def test_match_path_pattern_startswith_hit(tmp_path):
    """rel.startswith(pat + '/') must trigger independently of fnmatch."""
    # "build/deep/out.py".startswith("build/") is True; fnmatch("build/deep/out.py","build") is False
    assert _match_path_pattern("build/deep/out.py", "build")


def test_match_path_pattern_exact_hit(tmp_path):
    """rel == pat must trigger independently (kills or→and mutants)."""
    # rel == pat but fnmatch("build", "build") is also True (trivial), so use a non-glob pat
    # Use a pattern that fnmatch would match differently with wildcards disabled
    assert _match_path_pattern("vendor/lib.py", "vendor/lib.py")


def test_match_path_pattern_startswith_not_fnmatch(tmp_path):
    """Kills mutmut_2: fnmatch and startswith must be independent (or not and)."""
    # fnmatch("sub/deep/f.py", "sub") = False (no glob expands to path sep)
    # but startswith("sub/") = True
    assert _match_path_pattern("sub/deep/f.py", "sub")


def test_match_path_pattern_slash_suffix(tmp_path):
    """pat + '/' must use '/', not 'XX/XX' (kills mutmut_9)."""
    # "dist/pkg/f.py".startswith("dist/") is True
    assert _match_path_pattern("dist/pkg/f.py", "dist")


# --- _match_name_pattern: or, not and; split on "/" not None ---

def test_match_name_pattern_name_hit(tmp_path):
    """fnmatch(name, pat) alone triggers return True."""
    assert _match_name_pattern("src/mod.py", "mod.py", "mod.py")


def test_match_name_pattern_path_component_hit_not_name(tmp_path):
    """A path component matches but the name itself doesn't (kills or→and mutant)."""
    # name = "app.py", pattern = "src", path component "src" matches
    assert _match_name_pattern("src/app.py", "app.py", "src")


def test_match_name_pattern_split_on_slash(tmp_path):
    """split('/') must split on '/', not None or 'XX/XX'."""
    # rel = "a/b/c.py", split('/') = ['a','b','c.py']
    # pattern "b" matches path component "b"
    assert _match_name_pattern("a/b/c.py", "c.py", "b")


def test_match_name_pattern_no_match(tmp_path):
    assert not _match_name_pattern("src/mod.py", "mod.py", "build")


def test_match_name_pattern_deep_path_component(tmp_path):
    """Deep nested path: split('/') must produce all components."""
    assert _match_name_pattern("a/b/c/d.py", "d.py", "c")


# --- _load_gitignore_patterns: rstrip value vs rstrip(None) ---

def test_load_gitignore_trailing_spaces_preserved_in_pattern(tmp_path):
    """rstrip('\\n') preserves trailing spaces; rstrip(None) strips them.
    A gitignore line 'build  \\n' → rstrip('\\n') → 'build  ' (with spaces).
    rstrip(None) → 'build' (no spaces). They differ in the returned pattern value."""
    (tmp_path / ".gitignore").write_bytes(b"build  \n*.pyc\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "build  " in patterns


def test_load_gitignore_spaces_only_line_is_included(tmp_path):
    """A line of only spaces rstrip('\\n') = '   ' (truthy) → included in patterns.
    rstrip(None) = '' (falsy) → excluded by mutant_15.
    Real code includes the spaces-only pattern; mutant excludes it."""
    (tmp_path / ".gitignore").write_bytes(b"   \n*.pyc\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "   " in patterns
    assert "*.pyc" in patterns


def test_load_gitignore_X_line_in_filter(tmp_path):
    """Line 'X\\n': rstrip('\\n') = 'X' (truthy, included in list).
    rstrip('XX\\nXX') strips X and \\n → '' (falsy, excluded by filter).
    Kills mutmut_17 (rstrip('XX\\nXX') in filter condition)."""
    (tmp_path / ".gitignore").write_bytes(b"X\n*.pyc\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "X" in patterns


def test_load_gitignore_X_suffix_pattern_preserved(tmp_path):
    """Pattern 'buildX\\n': rstrip('\\n') → 'buildX'; rstrip('XX\\nXX') strips X → 'build'.
    Kills mutmut_13 (rstrip('XX\\nXX') in output)."""
    (tmp_path / ".gitignore").write_bytes(b"buildX\n*.pyc\n")
    patterns = _load_gitignore_patterns(str(tmp_path))
    assert "buildX" in patterns


# --- _fnmatch_path: lstrip('/') vs lstrip('XX/XX') ---

def test_fnmatch_path_X_prefix_pattern_not_stripped(tmp_path):
    """Pattern '/Xsrc/lib.py': lstrip('/') → 'Xsrc/lib.py' (correct, path has '/').
    lstrip('XX/XX') would strip the leading 'X' too → 'src/lib.py' (wrong match for 'Xsrc/lib.py').
    Kills mutmut_13 in _fnmatch_path."""
    # _fnmatch_path("Xsrc/lib.py", "lib.py", "/Xsrc/lib.py") must return True
    # because lstrip('/') gives 'Xsrc/lib.py' which matches rel exactly
    assert _fnmatch_path("Xsrc/lib.py", "lib.py", "/Xsrc/lib.py")
    # lstrip('XX/XX') would give 'src/lib.py' → _match_path_pattern('Xsrc/lib.py','src/lib.py') → False
    # We verify the result is True (real) so any mutation that makes it False is caught
    assert not _fnmatch_path("Xsrc/other.py", "other.py", "/Xsrc/lib.py")
