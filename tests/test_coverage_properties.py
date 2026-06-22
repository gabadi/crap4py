"""Property tests for LCOV coverage resolution (architect-owned).

Run separately: uv run pytest tests/test_coverage_properties.py
"""
from hypothesis import given, assume
from hypothesis import strategies as st
from crap4py.coverage import resolve_coverage, parse_lcov, NA

_BRDA_RECORD = st.tuples(
    st.integers(min_value=1, max_value=1000),
    st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8),
    st.integers(min_value=0, max_value=5),
)

_RANGE = st.integers(min_value=1, max_value=900).flatmap(
    lambda start: st.tuples(st.just(start), st.integers(min_value=start, max_value=start + 200))
)


@given(
    records=st.lists(_BRDA_RECORD, min_size=0, max_size=20),
    line_range=_RANGE,
)
def test_coverage_is_in_unit_interval_or_na(records, line_range):
    """resolve_coverage always returns a float in [0, 1] or NA."""
    lcov_data = {"src/foo.py": records}
    result = resolve_coverage("src/foo.py", line_range, lcov_data)
    if result is NA:
        # NA only when source file is absent — but we provided the key, so this should not happen
        assert False, "NA returned but source file was present"
    assert isinstance(result, float), f"Expected float, got {type(result)}"
    assert 0.0 <= result <= 1.0, f"Coverage {result} out of [0, 1]"


@given(records=st.lists(_BRDA_RECORD, min_size=0, max_size=20), line_range=_RANGE)
def test_coverage_na_when_file_absent(records, line_range):
    """Coverage is NA when the source file is not in lcov_data."""
    lcov_data = {"other/path.py": records}
    result = resolve_coverage("src/foo.py", line_range, lcov_data)
    assert result is NA


@given(
    count=st.integers(min_value=1, max_value=10),
    start=st.integers(min_value=1, max_value=100),
)
def test_all_taken_gives_full_coverage(count, start):
    """If all BRDA records in range have taken >= 1, coverage is 1.0."""
    records = [(start + i, "b", 1) for i in range(count)]
    lcov_data = {"src/foo.py": records}
    result = resolve_coverage("src/foo.py", (start, start + count - 1), lcov_data)
    assert result == 1.0


@given(
    count=st.integers(min_value=1, max_value=10),
    start=st.integers(min_value=1, max_value=100),
)
def test_none_taken_gives_zero_coverage(count, start):
    """If all BRDA records in range have taken=0, coverage is 0.0."""
    records = [(start + i, "b", 0) for i in range(count)]
    lcov_data = {"src/foo.py": records}
    result = resolve_coverage("src/foo.py", (start, start + count - 1), lcov_data)
    assert result == 0.0


@given(line_range=_RANGE)
def test_empty_records_gives_full_coverage(line_range):
    """A function with no BRDA records in its range is 100% covered."""
    lcov_data = {"src/foo.py": []}
    result = resolve_coverage("src/foo.py", line_range, lcov_data)
    assert result == 1.0


@given(
    records=st.lists(_BRDA_RECORD, min_size=1, max_size=10),
    start=st.integers(min_value=500, max_value=1000),
)
def test_out_of_range_records_give_full_coverage(records, start):
    """BRDA records outside the function line range don't affect coverage."""
    records_low = [(r[0] % 100, r[1], r[2]) for r in records]
    lcov_data = {"src/foo.py": records_low}
    # Query a range that is entirely above all records
    result = resolve_coverage("src/foo.py", (start, start + 100), lcov_data)
    assert result == 1.0


@given(
    taken_counts=st.lists(st.integers(min_value=0, max_value=3), min_size=1, max_size=20),
    start=st.integers(min_value=1, max_value=100),
)
def test_coverage_ratio_is_taken_over_total(taken_counts, start):
    """Coverage = taken / total, where taken counts records with taken >= 1."""
    records = [(start + i, "b", t) for i, t in enumerate(taken_counts)]
    lcov_data = {"src/foo.py": records}
    end = start + len(taken_counts) - 1
    result = resolve_coverage("src/foo.py", (start, end), lcov_data)
    expected_taken = sum(1 for t in taken_counts if t >= 1)
    expected = expected_taken / len(taken_counts)
    assert abs(float(result) - expected) < 1e-10
