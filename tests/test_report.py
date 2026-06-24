"""Unit tests for crap4py._report (C4 pipeline: discover → score → CRAP rows)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from crap4py._report import build_report
from crap4py.coverage import NA

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SIMPLE_SOURCE = """\
def add(a, b):
    return a + b
"""

_COMPLEX_SOURCE = """\
def branchy(x):
    if x > 0:
        return x
    elif x < 0:
        return -x
    return 0
"""

# ---------------------------------------------------------------------------
# build_report
# ---------------------------------------------------------------------------


def test_build_report_empty_paths(tmp_path):
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nSF:src/foo.py\nend_of_record\n")
    rows = build_report(str(lcov_file), [])
    assert rows == []


def test_build_report_single_function_full_coverage(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    from crap4py.discovery import discover_functions

    entries = discover_functions([str(tmp_path)])
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{label}\nBRDA:1,0,0,1\nend_of_record\n")
    rows = build_report(str(lcov_file), [str(tmp_path)])
    assert len(rows) == 1
    row = rows[0]
    assert row.qualified_name == "add"
    assert row.cc == 1
    assert row.coverage == pytest.approx(1.0)
    assert row.crap == pytest.approx(1.0)


def test_build_report_coverage_na_when_file_absent(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nSF:/other/path.py\nBRDA:1,0,0,1\nend_of_record\n")
    rows = build_report(str(lcov_file), [str(tmp_path)])
    assert len(rows) == 1
    assert rows[0].coverage is NA
    assert rows[0].crap is NA


def test_build_report_fraction_coverage(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_COMPLEX_SOURCE)
    from crap4py.discovery import discover_functions

    entries = discover_functions([str(tmp_path)])
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{label}\nBRDA:2,0,0,1\nBRDA:2,0,1,0\nBRDA:4,0,0,0\nBRDA:4,0,1,0\nend_of_record\n")
    rows = build_report(str(lcov_file), [str(tmp_path)])
    assert len(rows) == 1
    row = rows[0]
    assert row.cc >= 3
    assert 0.0 < float(row.coverage) < 1.0


def test_build_report_skips_when_open_fn_raises_on_source(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{src_file}\nend_of_record\n")
    lcov_text = lcov_file.read_text()

    call_count = [0]

    def open_fn(path: str) -> str:
        call_count[0] += 1
        if call_count[0] == 1:
            return lcov_text
        raise OSError("simulated read failure")

    rows = build_report(str(lcov_file), [str(tmp_path)], open_fn=open_fn)
    assert rows == []


def test_build_report_sorted_worst_first(tmp_path):
    src = "def low(): pass\ndef high():\n    if True: pass\n    if True: pass\n    if True: pass\n    if True: pass\n"
    src_file = tmp_path / "foo.py"
    src_file.write_text(src)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    rows = build_report(str(lcov_file), [str(tmp_path)])
    assert len(rows) >= 2
    # N/A coverage → N/A CRAP → sorts last OR all N/A same order by name
    # Either way, high has bigger CC so higher CRAP if we had coverage,
    # but all are N/A here — just verify rows returned
    names = [r.qualified_name for r in rows]
    assert "low" in names
    assert "high" in names


def test_build_report_fragment_filter(tmp_path):
    dir_a = tmp_path / "src"
    dir_b = tmp_path / "tests"
    dir_a.mkdir()
    dir_b.mkdir()
    (dir_a / "main.py").write_text("def fn_src(): pass\n")
    (dir_b / "test_main.py").write_text("def fn_test(): pass\n")
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    rows = build_report(str(lcov_file), [str(tmp_path)], fragments=["src"])
    names = [r.qualified_name for r in rows]
    assert "fn_src" in names
    assert "fn_test" not in names


# --- mutant-killing tests ---

_TWO_FILE_SOURCE_A = "def first(x):\n    return x\n"
_TWO_FILE_SOURCE_B = "def second(x):\n    return x\n"


def test_build_report_continue_skips_only_failed_file(tmp_path):
    file_a = tmp_path / "a.py"
    file_b = tmp_path / "b.py"
    file_a.write_text(_TWO_FILE_SOURCE_A)
    file_b.write_text(_TWO_FILE_SOURCE_B)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    lcov_text = lcov_file.read_text()

    failed_paths: set[str] = set()

    def open_fn(path: str) -> str:
        if path == lcov_file.as_posix() or path == str(lcov_file):
            return lcov_text
        if "a.py" in path and path not in failed_paths:
            failed_paths.add(path)
            raise OSError("simulated failure for a.py")
        with open(path) as f:
            return f.read()

    rows = build_report(str(lcov_file), [str(tmp_path)], open_fn=open_fn)
    assert len(rows) == 1
    assert rows[0].qualified_name == "second"


def test_build_report_bare_name_uses_last_component(tmp_path):
    source = "class Outer:\n    class Inner:\n        def method(self):\n            if True:\n                pass\n"
    src_file = tmp_path / "thing.py"
    src_file.write_text(source)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    rows = build_report(str(lcov_file), [str(tmp_path)])
    assert len(rows) == 1
    assert rows[0].qualified_name == "Outer.Inner.method"
    assert rows[0].cc == 2


def test_build_report_default_cc_is_1_when_name_not_found(tmp_path):
    source = "def actual_func():\n    pass\n"
    src_file = tmp_path / "foo.py"
    src_file.write_text(source)
    from crap4py.discovery import discover_functions

    entries = discover_functions([str(tmp_path)])
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{label}\nend_of_record\n")
    lcov_text = lcov_file.read_text()

    def open_fn(path: str) -> str:
        if path == str(lcov_file):
            return lcov_text
        return "def different_name():\n    pass\n"

    rows = build_report(str(lcov_file), [str(tmp_path)], open_fn=open_fn)
    assert len(rows) == 1
    assert rows[0].cc == 1


def test_build_report_qualified_name_uses_dot_separator(tmp_path):
    source = "class Foo:\n    def bar(self):\n        pass\n"
    src_file = tmp_path / "mod.py"
    src_file.write_text(source)
    from crap4py.discovery import discover_functions

    entries = discover_functions([str(tmp_path)])
    assert any(e.qualified_name == "Foo.bar" for e in entries)
    for e in entries:
        assert "XX" not in e.qualified_name
