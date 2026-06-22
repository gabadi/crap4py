"""Step handlers for features/coverage.feature (C3, #9)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from crap4py.coverage import resolve_coverage, parse_lcov, NA, LcovData
from acceptance.steps.step_lib import make_registry

STEP_HANDLERS, step, run_step = make_registry()

_PRESENT_SF = "src/crap4py/module_under_test.py"
_FUNCTION_LINE_RANGE = (1, 100)  # wide default range; tests narrow it if needed


class Context:
    def __init__(self):
        self.sf: str = _PRESENT_SF
        self.line_range: tuple[int, int] = _FUNCTION_LINE_RANGE
        self.lcov_data: LcovData = {}
        self.result = None
        self._brda_counter: int = 0
        self._matched_sf: str | None = None

    def _next_branch_id(self) -> str:
        self._brda_counter += 1
        return str(self._brda_counter)

    def _add_brda(self, line: int, taken_raw: str):
        bid = self._next_branch_id()
        taken = 0 if taken_raw == "-" else int(taken_raw)
        records = self.lcov_data.setdefault(self.sf, [])
        records.append((line, bid, taken))


ctx = Context()


# --- Background ---

@step(r"an LCOV file produced by coverage\.py and a function with a known line range")
def given_background(m, params):
    ctx.__init__()


# --- Given: file present in LCOV ---

@step(r"a function in a file present in the LCOV")
def given_file_present(m, params):
    ctx.lcov_data.setdefault(ctx.sf, [])


# --- Given: taken counts ---

@step(r"(\d+) of its (\d+) in-range BRDA branches have a taken count of at least 1")
def given_taken_of_total(m, params):
    taken_count = int(params.get("taken_count") or m.group(1))
    total_count = int(params.get("total_count") or m.group(2))
    not_taken = total_count - taken_count
    base_line = 5
    for i in range(taken_count):
        ctx._add_brda(base_line + i, "1")
    for i in range(not_taken):
        ctx._add_brda(base_line + taken_count + i, "0")
    ctx.line_range = (1, base_line + total_count)


@step(r'it has one in-range BRDA branch with taken "([^"]+)"')
def given_one_branch_with_taken(m, params):
    # Always use regex capture: the literal in the step text may differ from params.
    taken_raw = m.group(1)
    ctx._add_brda(5 + ctx._brda_counter, taken_raw)
    ctx.line_range = (1, 20)


@step(r'it has one in-range BRDA branch with branch id "([^"]+)" and taken "([^"]+)"')
def given_branch_with_id_and_taken(m, params):
    branch_id = params.get("branch_id") or m.group(1)
    taken_raw = params.get("taken") or m.group(2)
    taken = 0 if taken_raw == "-" else int(taken_raw)
    records = ctx.lcov_data.setdefault(ctx.sf, [])
    records.append((5, branch_id, taken))
    ctx.line_range = (1, 20)


@step(r"the LCOV has no BRDA records within the function's line range")
def given_no_brda_in_range(m, params):
    ctx.lcov_data.setdefault(ctx.sf, [])
    ctx.line_range = (50, 100)


# --- Given: file absent from LCOV ---

@step(r'the function\'s source file "([^"]+)" has no matching SF record in the LCOV')
def given_file_absent(m, params):
    source = params.get("source") or m.group(1)
    ctx.sf = source
    ctx.lcov_data = {}


# --- Given: suffix matching ---

@step(r'the LCOV has an SF record for "([^"]+)"')
def given_sf_record(m, params):
    sf_path = params.get("sf_path") or m.group(1)
    ctx.lcov_data = {sf_path: [(5, "0", 1)]}
    ctx.line_range = (1, 10)


@step(r'the function\'s discovered source path is "([^"]+)"')
def given_source_path(m, params):
    source = params.get("source") or m.group(1)
    ctx.sf = source
    ctx._matched_sf = None


# --- Given: line 0 BRDA ignored ---

@step(r'the LCOV has a BRDA record on line 0 with taken "([^"]+)"')
def given_brda_line_0(m, params):
    taken_raw = params.get("taken") or m.group(1)
    taken = 0 if taken_raw == "-" else int(taken_raw)
    records = ctx.lcov_data.setdefault(ctx.sf, [])
    records.append((0, "line0-branch", taken))
    ctx.line_range = (1, 20)


# --- When ---

@step(r"coverage is resolved for the function")
def when_coverage_resolved(m, params):
    ctx.result = resolve_coverage(ctx.sf, ctx.line_range, ctx.lcov_data)


# --- Then ---

@step(r'the function\'s coverage is "([^"]+)"')
def then_coverage_is(m, params):
    expected_str = params.get("coverage") or m.group(1)
    if expected_str == "N/A":
        assert ctx.result is NA, f"Expected N/A but got {ctx.result!r}"
    else:
        expected = float(expected_str)
        assert isinstance(ctx.result, float), f"Expected float but got {ctx.result!r}"
        assert abs(ctx.result - expected) < 1e-9, (
            f"Expected coverage {expected}, got {ctx.result}"
        )


@step(r'the function\'s source file is matched to the SF record for "([^"]+)"')
def then_file_matched_to_sf(m, params):
    expected_sf = params.get("sf_path") or m.group(1)
    assert ctx.result is not NA, (
        f"Expected match to SF '{expected_sf}' but got N/A"
    )
