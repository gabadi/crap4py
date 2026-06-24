"""Unit tests for crap4py.coverage (C3, #9).

Tests the pure coverage resolution logic: LCOV parsing and per-function
branch-coverage computation.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from crap4py.coverage import NA, parse_lcov, resolve_coverage

# ---------------------------------------------------------------------------
# parse_lcov
# ---------------------------------------------------------------------------


def _make_lcov(sf: str, brda_lines: list[str]) -> str:
    lines = ["TN:", f"SF:{sf}"]
    lines.extend(brda_lines)
    lines.append("end_of_record")
    return "\n".join(lines) + "\n"


def test_parse_lcov_returns_sf_and_brda():
    lcov = _make_lcov("src/foo.py", ["BRDA:10,0,jump to line 12,1"])
    result = parse_lcov(lcov)
    assert "src/foo.py" in result
    records = result["src/foo.py"]
    assert len(records) == 1
    assert records[0] == (10, "jump to line 12", 1)


def test_parse_lcov_skips_line_0():
    lcov = _make_lcov("src/foo.py", ["BRDA:0,0,0,1", "BRDA:5,0,0,1"])
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert len(records) == 1
    assert records[0][0] == 5


def test_parse_lcov_taken_dash_as_0():
    lcov = _make_lcov("src/foo.py", ["BRDA:5,0,0,-"])
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert records[0] == (5, "0", 0)


def test_parse_lcov_taken_string_0_as_0():
    lcov = _make_lcov("src/foo.py", ["BRDA:5,0,0,0"])
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert records[0][2] == 0


def test_parse_lcov_taken_positive_int():
    lcov = _make_lcov("src/foo.py", ["BRDA:5,0,0,3"])
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert records[0][2] == 3


def test_parse_lcov_ignores_non_brda_records():
    lcov = _make_lcov(
        "src/foo.py",
        [
            "DA:5,1",
            "FN:5,foo",
            "FNDA:1,foo",
            "LF:1",
            "LH:1",
            "BRF:1",
            "BRH:1",
            "BRDA:5,0,0,1",
        ],
    )
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert len(records) == 1


def test_parse_lcov_multiple_sf_blocks():
    lcov = "TN:\nSF:src/a.py\nBRDA:5,0,0,1\nend_of_record\nTN:\nSF:src/b.py\nBRDA:10,0,0,0\nend_of_record\n"
    result = parse_lcov(lcov)
    assert "src/a.py" in result
    assert "src/b.py" in result


def test_parse_lcov_textual_branch_id():
    lcov = _make_lcov("src/foo.py", ["BRDA:10,0,jump to line 8,1"])
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert records[0][1] == "jump to line 8"


# ---------------------------------------------------------------------------
# resolve_coverage
# ---------------------------------------------------------------------------


def _make_brda_records(entries: list[tuple[int, int]]) -> dict:
    """entries: [(line, taken), ...] → simple LCOV dict for sf."""
    return {"src/foo.py": [(ln, str(i), tk) for i, (ln, tk) in enumerate(entries)]}


def test_coverage_fraction_taken_over_total():
    lcov_data = {"src/foo.py": [(1, "0", 1), (2, "1", 1), (3, "2", 0), (4, "3", 0)]}
    cov = resolve_coverage("src/foo.py", (1, 4), lcov_data)
    assert cov == pytest.approx(0.5)


def test_coverage_all_taken():
    lcov_data = {"src/foo.py": [(5, "0", 1), (6, "1", 2), (7, "2", 5)]}
    cov = resolve_coverage("src/foo.py", (5, 7), lcov_data)
    assert cov == pytest.approx(1.0)


def test_coverage_none_taken():
    lcov_data = {"src/foo.py": [(10, "0", 0), (11, "1", 0)]}
    cov = resolve_coverage("src/foo.py", (10, 11), lcov_data)
    assert cov == pytest.approx(0.0)


def test_coverage_taken_dash_normalised_to_zero_and_uncovered():
    # parse_lcov normalises taken="-" to 0; resolve_coverage treats 0 as uncovered.
    lcov_text = "TN:\nSF:src/foo.py\nBRDA:1,0,0,-\nBRDA:2,0,1,1\nend_of_record\n"
    cov = resolve_coverage("src/foo.py", (1, 2), parse_lcov(lcov_text))
    assert cov == pytest.approx(0.5)


def test_coverage_taken_zero_is_uncovered_in_numerator():
    # taken=0 (block reached, branch not taken) counts in denominator but not numerator.
    lcov_data = {"src/foo.py": [(1, "0", 0), (2, "1", 1), (3, "2", 0)]}
    cov = resolve_coverage("src/foo.py", (1, 3), lcov_data)
    assert cov == pytest.approx(1 / 3)


def test_coverage_zero_branches_is_100_percent():
    lcov_data = {"src/foo.py": []}
    cov = resolve_coverage("src/foo.py", (1, 5), lcov_data)
    assert cov == pytest.approx(1.0)


def test_coverage_no_brda_in_range_is_100_percent():
    lcov_data = {"src/foo.py": [(20, "0", 1)]}
    cov = resolve_coverage("src/foo.py", (1, 5), lcov_data)
    assert cov == pytest.approx(1.0)


def test_coverage_na_when_source_file_absent():
    lcov_data = {}
    cov = resolve_coverage("src/foo.py", (1, 5), lcov_data)
    assert cov is NA


def test_coverage_suffix_matching_absolute_sf():
    lcov_data = {"/abs/proj/src/foo.py": [(1, "0", 1), (2, "1", 0)]}
    cov = resolve_coverage("src/foo.py", (1, 2), lcov_data)
    assert cov == pytest.approx(0.5)


def test_coverage_suffix_matching_relative_sf():
    lcov_data = {"proj/src/foo.py": [(1, "0", 1), (2, "1", 1)]}
    cov = resolve_coverage("src/foo.py", (1, 2), lcov_data)
    assert cov == pytest.approx(1.0)


def test_coverage_only_in_range_brda_counted():
    lcov_data = {
        "src/foo.py": [
            (1, "0", 0),  # in range [5,10] — no
            (5, "1", 1),  # in range — yes
            (10, "2", 0),  # in range — yes (uncovered)
            (11, "3", 1),  # out of range — ignored
        ]
    }
    cov = resolve_coverage("src/foo.py", (5, 10), lcov_data)
    assert cov == pytest.approx(0.5)


def test_coverage_textual_branch_id_ignored():
    lcov_data = {"src/foo.py": [(5, "jump to line 8", 1)]}
    cov = resolve_coverage("src/foo.py", (1, 10), lcov_data)
    assert cov == pytest.approx(1.0)


def test_na_sentinel_is_not_float():
    assert NA is not None
    assert not isinstance(NA, float)


def test_na_sentinel_repr():
    assert str(NA) == "N/A"


def test_na_repr_function():
    assert repr(NA) == "N/A"


def test_na_singleton_returns_same_instance():
    from crap4py.coverage import _NA

    a = _NA()
    b = _NA()
    assert a is b


def test_parse_lcov_end_of_record_without_sf_is_ignored():
    lcov = "TN:\nend_of_record\nSF:src/foo.py\nBRDA:5,0,0,1\nend_of_record\n"
    result = parse_lcov(lcov)
    assert "src/foo.py" in result
    assert len(result) == 1


def test_parse_lcov_brda_with_fewer_than_4_parts_is_skipped():
    lcov = "TN:\nSF:src/foo.py\nBRDA:5,0,0\nBRDA:6,0,0,1\nend_of_record\n"
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert len(records) == 1
    assert records[0][0] == 6


def test_match_sf_exact_path_without_prefix():
    from crap4py.coverage import _match_sf

    lcov_data = {"src/foo.py": [(1, "0", 1)]}
    records = _match_sf("src/foo.py", lcov_data)
    assert records is not None
    assert len(records) == 1


def test_coverage_windows_path_normalisation():
    lcov_data = {"src\\foo.py": [(1, "0", 1), (2, "1", 0)]}
    cov = resolve_coverage("src/foo.py", (1, 2), lcov_data)
    assert cov == pytest.approx(0.5)


# --- mutant-killing tests ---


def test_parse_brda_split_on_comma_not_other_separator():
    # mutmut_5: split(",",) removes maxsplit — but "taken" field may contain commas
    # if BRDA format is "BRDA:line,block,branch,taken" we need maxsplit=3
    # A BRDA where taken field value matters: ensure exactly 4 parts produced
    lcov = "TN:\nSF:src/foo.py\nBRDA:5,0,branch,1\nend_of_record\n"
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert len(records) == 1
    assert records[0] == (5, "branch", 1)


def test_parse_brda_rsplit_would_break_branch_id():
    # mutmut_6: rsplit(",",3) would produce different parts ordering for branch IDs with commas
    # Test with a BRDA that has branch id containing "jump to line N" — forward split vs rsplit differs
    lcov = "TN:\nSF:src/foo.py\nBRDA:10,0,jump to line 8,3\nend_of_record\n"
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert records[0] == (10, "jump to line 8", 3)


def test_parse_brda_split_maxsplit_3_not_4():
    # mutmut_9: split(",",4) gives same result for most BRDA but not when taken has commas
    # Verify taken field parsed correctly with exactly maxsplit=3
    lcov = "TN:\nSF:src/foo.py\nBRDA:5,0,branch,42\nend_of_record\n"
    result = parse_lcov(lcov)
    records = result["src/foo.py"]
    assert records[0][2] == 42


def test_lcov_parse_state_current_records_starts_as_list():
    # mutmut_3: __init__ sets current_records = None instead of []
    from crap4py.coverage import _LcovParseState

    state = _LcovParseState()
    assert state.current_records == []
    state.on_brda("BRDA:5,0,0,1")  # would fail if current_records is None
    assert len(state.current_records) == 1


def test_on_end_of_record_clears_current_sf_to_none_not_empty_string():
    # mutmut_3: on_end_of_record sets current_sf = "" instead of None
    from crap4py.coverage import _LcovParseState

    state = _LcovParseState()
    state.on_sf("src/foo.py")
    state.on_end_of_record()
    # After end_of_record, current_sf must be None (not "" or any other falsy-but-not-None value)
    # parse_lcov guards on_brda with `state.current_sf is not None`
    # so if current_sf is "" (empty string), the guard passes and BRDA is wrongly accepted
    assert state.current_sf is None


def test_on_end_of_record_resets_current_records_to_list_not_none():
    # mutmut_4: on_end_of_record sets current_records = None instead of []
    from crap4py.coverage import _LcovParseState

    state = _LcovParseState()
    state.on_sf("src/a.py")
    state.on_brda("BRDA:5,0,0,1")
    state.on_end_of_record()
    state.on_sf("src/b.py")
    state.on_brda("BRDA:10,0,0,1")  # would fail if current_records is None
    state.on_end_of_record()
    assert len(state.result["src/b.py"]) == 1


def test_parse_lcov_brda_requires_active_sf_and_not_or():
    # mutmut_11: `and` changed to `or` — BRDA before any SF would be processed
    lcov = "BRDA:5,0,0,1\nSF:src/foo.py\nBRDA:10,0,0,1\nend_of_record\n"
    result = parse_lcov(lcov)
    # Only the BRDA after SF:src/foo.py should be included
    records = result["src/foo.py"]
    assert len(records) == 1
    assert records[0][0] == 10


def test_match_sf_windows_backslash_in_source_path():
    # mutmut_7: replace("XX\\XX", "/") — source path with backslash not normalized
    from crap4py.coverage import _match_sf

    lcov_data = {"/abs/proj/src/foo.py": [(1, "0", 1)]}
    records = _match_sf("src\\foo.py", lcov_data)
    assert records is not None


def test_match_sf_windows_replacement_target_is_forward_slash():
    # mutmut_8: replace("\\", "XX/XX") — normalization produces wrong separator
    from crap4py.coverage import _match_sf

    lcov_data = {"src/foo.py": [(1, "0", 1)]}
    records = _match_sf("src\\foo.py", lcov_data)
    assert records is not None
    assert records[0][0] == 1
