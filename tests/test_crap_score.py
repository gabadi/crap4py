"""Unit tests for C4 CRAP score, sort, and report format logic."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from crap4py._crap import ReportRow, crap_score, sort_rows
from crap4py._format import format_report
from crap4py.coverage import NA

# ---------------------------------------------------------------------------
# crap_score
# ---------------------------------------------------------------------------


def test_crap_score_cc4_cov075():
    # CC=4, coverage=0.75 → 4²*(1-0.75)³ + 4 = 16*0.015625 + 4 = 0.25+4 = 4.25 → 4.2 rounded
    assert crap_score(4, 0.75) == pytest.approx(4.25)


def test_crap_score_cc5_cov00():
    # CC=5, coverage=0.0 → 5²*(1-0)³ + 5 = 25+5 = 30.0
    assert crap_score(5, 0.0) == pytest.approx(30.0)


def test_crap_score_cc1_cov10():
    # CC=1, coverage=1.0 → 1²*(1-1)³ + 1 = 0+1 = 1.0
    assert crap_score(1, 1.0) == pytest.approx(1.0)


def test_crap_score_na_coverage_returns_na():
    assert crap_score(4, NA) is NA


def test_crap_score_cc2_cov05():
    # CC=2, coverage=0.5 → 4*(0.5)³ + 2 = 4*0.125 + 2 = 0.5+2 = 2.5
    assert crap_score(2, 0.5) == pytest.approx(2.5)


# ---------------------------------------------------------------------------
# ReportRow
# ---------------------------------------------------------------------------


def test_report_row_fields():
    row = ReportRow("foo", "src/foo.py", 2, 0.5)
    assert row.qualified_name == "foo"
    assert row.module_label == "src/foo.py"
    assert row.cc == 2
    assert row.coverage == 0.5
    assert row.crap == pytest.approx(2.5)


def test_report_row_na_coverage():
    row = ReportRow("foo", "src/foo.py", 2, NA)
    assert row.crap is NA


def test_report_row_cov_percent_finite():
    row = ReportRow("foo", "src/foo.py", 1, 0.75)
    assert row.cov_percent == "75.0%"


def test_report_row_cov_percent_zero():
    row = ReportRow("foo", "src/foo.py", 1, 0.0)
    assert row.cov_percent == "0.0%"


def test_report_row_cov_percent_full():
    row = ReportRow("foo", "src/foo.py", 1, 1.0)
    assert row.cov_percent == "100.0%"


def test_report_row_cov_percent_na():
    row = ReportRow("foo", "src/foo.py", 1, NA)
    assert row.cov_percent == "N/A"


def test_report_row_crap_str_finite():
    row = ReportRow("foo", "src/foo.py", 5, 0.0)
    assert row.crap_str == "30.0"


def test_report_row_crap_str_na():
    row = ReportRow("foo", "src/foo.py", 1, NA)
    assert row.crap_str == "N/A"


def test_report_row_crap_str_one_decimal():
    row = ReportRow("foo", "src/foo.py", 4, 0.75)
    assert row.crap_str == "4.2"


# ---------------------------------------------------------------------------
# sort_rows
# ---------------------------------------------------------------------------


def _make_rows(specs: list[tuple[str, float | object]]) -> list[ReportRow]:
    return [ReportRow(name, "m.py", 1, cov) for name, cov in specs]


def test_sort_rows_worst_crap_first():
    rows = _make_rows([("low", 1.0), ("high", 0.0)])
    sorted_rows = sort_rows(rows)
    assert sorted_rows[0].qualified_name == "high"
    assert sorted_rows[1].qualified_name == "low"


def test_sort_rows_na_last():
    rows = _make_rows([("finite", 0.0), ("absent", NA)])
    sorted_rows = sort_rows(rows)
    assert sorted_rows[0].qualified_name == "finite"
    assert sorted_rows[1].qualified_name == "absent"


def test_sort_rows_equal_crap_stable_by_name():
    # CC=1, cov=1.0 → CRAP=1.0 for both; should sort by name ascending
    rows = [ReportRow("beta", "m.py", 1, 1.0), ReportRow("alpha", "m.py", 1, 1.0)]
    sorted_rows = sort_rows(rows)
    assert sorted_rows[0].qualified_name == "alpha"
    assert sorted_rows[1].qualified_name == "beta"


def test_sort_rows_two_na_stable_by_name():
    rows = [ReportRow("zed", "m.py", 1, NA), ReportRow("aaa", "m.py", 1, NA)]
    sorted_rows = sort_rows(rows)
    assert sorted_rows[0].qualified_name == "aaa"
    assert sorted_rows[1].qualified_name == "zed"


def test_sort_rows_full_ordering():
    # charlie(crap=30.0), alpha(4.2), delta(4.2), bravo(N/A), echo(N/A)
    rows = [
        ReportRow("alpha", "m.py", 4, 0.75),  # crap=4.25
        ReportRow("bravo", "m.py", 1, NA),
        ReportRow("charlie", "m.py", 5, 0.0),  # crap=30.0
        ReportRow("delta", "m.py", 4, 0.75),  # crap=4.25
        ReportRow("echo", "m.py", 1, NA),
    ]
    sorted_rows = sort_rows(rows)
    names = [r.qualified_name for r in sorted_rows]
    assert names == ["charlie", "alpha", "delta", "bravo", "echo"]


# ---------------------------------------------------------------------------
# format_report
# ---------------------------------------------------------------------------


def test_format_report_first_line_is_crap_report():
    rows = [ReportRow("foo", "src/foo.py", 1, 1.0)]
    output = format_report(rows)
    assert output.splitlines()[0] == "CRAP Report"


def test_format_report_underline_of_equals():
    rows = [ReportRow("foo", "src/foo.py", 1, 1.0)]
    output = format_report(rows)
    lines = output.splitlines()
    assert set(lines[1]) == {"="}


def test_format_report_header_has_five_columns():
    rows = [ReportRow("foo", "src/foo.py", 1, 1.0)]
    output = format_report(rows)
    header = output.splitlines()[2]
    assert "Function" in header
    assert "Module" in header
    assert "CC" in header
    assert "Cov%" in header
    assert "CRAP" in header


def test_format_report_separator_after_header():
    rows = [ReportRow("foo", "src/foo.py", 1, 1.0)]
    output = format_report(rows)
    lines = output.splitlines()
    sep = lines[3]
    assert set(sep.strip()) == {"-"}


def test_format_report_row_data_present():
    rows = [ReportRow("my_func", "src/bar.py", 3, 0.5)]
    output = format_report(rows)
    assert "my_func" in output
    assert "src/bar.py" in output
    assert "3" in output


def test_format_report_empty_rows_has_header_block():
    output = format_report([])
    lines = output.splitlines()
    assert lines[0] == "CRAP Report"
    assert "Function" in output
    assert "CRAP" in output


def test_format_report_empty_has_no_data_rows():
    output = format_report([])
    lines = output.splitlines()
    # Only title, underline, header, separator — 4 lines
    assert len(lines) == 4


def test_format_report_cov_percent_shown():
    rows = [ReportRow("foo", "src/foo.py", 4, 0.75)]
    output = format_report(rows)
    assert "75.0%" in output


def test_format_report_crap_score_shown():
    rows = [ReportRow("foo", "src/foo.py", 5, 0.0)]
    output = format_report(rows)
    assert "30.0" in output


def test_format_report_na_rows():
    rows = [ReportRow("foo", "src/foo.py", 1, NA)]
    output = format_report(rows)
    assert "N/A" in output
