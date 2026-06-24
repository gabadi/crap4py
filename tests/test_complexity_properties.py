"""Property tests for cyclomatic complexity (architect-owned).

Run separately: uv run pytest tests/test_complexity_properties.py
"""

import keyword

from hypothesis import given
from hypothesis import strategies as st

from crap4py.complexity import cyclomatic_complexity

# --- Source generators ---

_SIMPLE_BODIES = [
    "pass",
    "return 1",
    "x = 1",
    "x = 1\n    return x",
]

_DECISION_STMTS = [
    "if x: pass",
    "for i in range(1): pass",
    "while False: pass",
    "assert True",
]


def _function(name: str, body_lines: list[str]) -> str:
    body = "\n    ".join(body_lines) if body_lines else "pass"
    return f"def {name}():\n    {body}\n"


# --- Properties ---


@given(
    body=st.sampled_from(_SIMPLE_BODIES),
    extra=st.lists(st.sampled_from(_DECISION_STMTS), min_size=0, max_size=5),
)
def test_cc_always_at_least_one(body, extra):
    """CC of any function is always ≥ 1."""
    lines = [body] + extra
    source = _function("f", lines)
    results = cyclomatic_complexity(source)
    assert results, "At least one function must be scored"
    assert all(r.cc >= 1 for r in results), "CC must be >= 1 for every function"


@given(
    base_body=st.sampled_from(_SIMPLE_BODIES),
    added=st.lists(st.sampled_from(_DECISION_STMTS), min_size=1, max_size=5),
)
def test_adding_decision_points_does_not_decrease_cc(base_body, added):
    """Adding decision points to a function never decreases its CC."""
    base_source = _function("f", [base_body])
    augmented_source = _function("f", [base_body] + added)
    base_cc = cyclomatic_complexity(base_source)[0].cc
    augmented_cc = cyclomatic_complexity(augmented_source)[0].cc
    assert augmented_cc >= base_cc


@given(
    outer_body=st.sampled_from(_SIMPLE_BODIES),
    inner_extra=st.lists(st.sampled_from(_DECISION_STMTS), min_size=1, max_size=3),
)
def test_nested_function_decision_points_do_not_affect_outer_cc(outer_body, inner_extra):
    """Nested function's decision points must not increase the outer function's CC."""
    outer_only_source = _function("outer", [outer_body])
    outer_cc_alone = cyclomatic_complexity(outer_only_source)[0].cc

    inner_lines = inner_extra
    inner_body = "\n        ".join(inner_lines) if inner_lines else "pass"
    with_nested = f"def outer():\n    {outer_body}\n    def inner():\n        {inner_body}\n"
    results = {r.name: r.cc for r in cyclomatic_complexity(with_nested)}
    assert "outer" in results
    assert "inner" in results
    assert results["outer"] == outer_cc_alone, (
        f"outer CC changed from {outer_cc_alone} to {results['outer']} when nested function decision points were added"
    )


_VALID_NAME = st.text(
    alphabet=st.characters(whitelist_categories=("Ll",), min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=8,
).filter(lambda s: not keyword.iskeyword(s))


@given(names=st.lists(_VALID_NAME, min_size=2, max_size=5, unique=True))
def test_result_order_matches_definition_order(names):
    """Functions are returned in their definition order."""
    source = "\n".join(_function(name, ["pass"]) for name in names)
    results = cyclomatic_complexity(source)
    result_names = [r.name for r in results]
    assert result_names == names, f"Expected order {names}, got {result_names}"
