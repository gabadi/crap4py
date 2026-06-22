"""Unit tests for crap4py._report (report-building logic extracted from CLI)."""
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from crap4py._report import build_rows, format_table, _format_coverage
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
# _format_coverage
# ---------------------------------------------------------------------------

def test_format_coverage_na():
    assert _format_coverage(NA) == "N/A"


def test_format_coverage_zero():
    assert _format_coverage(0.0) == "0.0"


def test_format_coverage_one():
    assert _format_coverage(1.0) == "1.0"


def test_format_coverage_fraction():
    result = _format_coverage(0.5)
    assert result == "0.5"


def test_format_coverage_small_fraction():
    result = _format_coverage(0.3333)
    assert "0.333" in result


# ---------------------------------------------------------------------------
# format_table
# ---------------------------------------------------------------------------

def test_format_table_no_rows():
    assert format_table([]) == "no functions found"


def test_format_table_has_headers():
    rows = [("add", "src/foo.py", 1, "1.0")]
    table = format_table(rows)
    assert "function" in table
    assert "module" in table
    assert "cc" in table
    assert "coverage" in table


def test_format_table_has_separator():
    rows = [("add", "src/foo.py", 1, "1.0")]
    table = format_table(rows)
    lines = table.splitlines()
    assert any(set(l.strip()).issubset({"-", " "}) for l in lines)


def test_format_table_row_data_present():
    rows = [("my_func", "src/bar.py", 3, "0.75")]
    table = format_table(rows)
    assert "my_func" in table
    assert "src/bar.py" in table
    assert "3" in table
    assert "0.75" in table


def test_format_table_multiple_rows():
    rows = [
        ("func_a", "src/a.py", 1, "1.0"),
        ("func_b", "src/b.py", 2, "0.5"),
    ]
    table = format_table(rows)
    assert "func_a" in table
    assert "func_b" in table


# ---------------------------------------------------------------------------
# build_rows — uses real temp files (discover_functions needs real filesystem)
# ---------------------------------------------------------------------------

def test_build_rows_empty_paths(tmp_path):
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nSF:src/foo.py\nend_of_record\n")
    rows = build_rows(str(lcov_file), [])
    assert rows == []


def test_build_rows_single_function_full_coverage(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    # Discover first to get the real module_label used in resolution
    from crap4py.discovery import discover_functions
    entries = discover_functions([str(tmp_path)])
    assert len(entries) == 1
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{label}\nBRDA:1,0,0,1\nend_of_record\n")
    rows = build_rows(str(lcov_file), [str(tmp_path)])
    assert len(rows) == 1
    qname, mod, cc, cov_str = rows[0]
    assert qname == "add"
    assert cc == 1
    assert cov_str == "1.0"


def test_build_rows_coverage_na_when_file_absent_from_lcov(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nSF:/other/path.py\nBRDA:1,0,0,1\nend_of_record\n")
    rows = build_rows(str(lcov_file), [str(tmp_path)])
    assert len(rows) == 1
    _, _, _, cov_str = rows[0]
    assert cov_str == "N/A"


def test_build_rows_fraction_coverage(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_COMPLEX_SOURCE)
    from crap4py.discovery import discover_functions
    entries = discover_functions([str(tmp_path)])
    assert len(entries) == 1
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(
        f"TN:\nSF:{label}\n"
        "BRDA:2,0,0,1\n"
        "BRDA:2,0,1,0\n"
        "BRDA:4,0,0,0\n"
        "BRDA:4,0,1,0\n"
        "end_of_record\n"
    )
    rows = build_rows(str(lcov_file), [str(tmp_path)])
    assert len(rows) == 1
    _, _, cc, cov_str = rows[0]
    assert cc >= 3
    assert cov_str not in ("1.0",)


def test_build_rows_skips_when_open_fn_raises_on_source(tmp_path):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{src_file}\nend_of_record\n")
    lcov_text = lcov_file.read_text()

    call_count = [0]

    def open_fn(path: str) -> str:
        call_count[0] += 1
        if call_count[0] == 1:
            return lcov_text  # first call is for the lcov file
        raise OSError("simulated read failure")

    rows = build_rows(str(lcov_file), [str(tmp_path)], open_fn=open_fn)
    assert rows == []
