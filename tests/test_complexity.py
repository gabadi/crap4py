"""Unit tests for cyclomatic complexity calculation (C1, #7).

Decision point rules per ADR 0001 (radon expression-aware model):
  +1: if, elif, for, while, loop else, each except, each extra bool operand,
      ternary (IfExp), each comprehension for/if clause, non-wildcard match case, assert
  +0: else (of if), try, finally, with, wildcard case _:
"""
import textwrap
import pytest
from crap4py.complexity import cyclomatic_complexity


def cc(source: str) -> int:
    """Return CC for the first function defined in source."""
    results = cyclomatic_complexity(source)
    assert results, "No functions found in source"
    return results[0].cc


def cc_named(source: str) -> dict:
    """Return {name: cc} for all functions in source."""
    return {r.name: r.cc for r in cyclomatic_complexity(source)}


def func(body: str) -> str:
    """Wrap a body string (semicolons → newlines) into a def."""
    lines = body.replace("; ", "\n    ").replace(";", "\n    ")
    return f"def f():\n    {lines}\n"


# complexity-1: no decision points → CC 1
@pytest.mark.parametrize("body,expected", [
    ("pass", 1),
    ("x = 1; y = 2; return x + y", 1),
    ("return f(g(h(1)))", 1),
])
def test_no_decision_points(body, expected):
    assert cc(func(body)) == expected


# complexity-2: if/elif add 1 each; else adds 0
@pytest.mark.parametrize("if_count,elif_count,else_count,expected", [
    (1, 0, 0, 2),
    (1, 0, 1, 2),
    (1, 1, 0, 3),
    (1, 2, 1, 4),
])
def test_if_elif_else(if_count, elif_count, else_count, expected):
    lines = ["if x:"]
    lines.append("    pass")
    for _ in range(elif_count):
        lines.append("elif x:")
        lines.append("    pass")
    if else_count:
        lines.append("else:")
        lines.append("    pass")
    body = "\n    ".join(lines)
    source = f"def f():\n    {body}\n"
    assert cc(source) == expected


# complexity-3: loops +1; loop else +1
@pytest.mark.parametrize("loop,has_else,expected", [
    ("for", False, 2),
    ("for", True, 3),
    ("while", False, 2),
    ("while", True, 3),
])
def test_loops(loop, has_else, expected):
    if loop == "for":
        lines = ["for i in x:", "    pass"]
    else:
        lines = ["while x:", "    pass"]
    if has_else:
        lines += ["else:", "    pass"]
    body = "\n    ".join(lines)
    source = f"def f():\n    {body}\n"
    assert cc(source) == expected


# complexity-4: each except +1; try/finally +0
@pytest.mark.parametrize("except_count,has_finally,expected", [
    (1, False, 2),
    (2, False, 3),
    (1, True, 2),
    (0, True, 1),
])
def test_try_except_finally(except_count, has_finally, expected):
    lines = ["try:", "    pass"]
    for _ in range(except_count):
        lines += ["except Exception:", "    pass"]
    if has_finally:
        lines += ["finally:", "    pass"]
    body = "\n    ".join(lines)
    source = f"def f():\n    {body}\n"
    assert cc(source) == expected


# complexity-5: boolean operators +1 per extra operand
@pytest.mark.parametrize("expr,expected", [
    ("a and b", 2),
    ("a or b", 2),
    ("a and b and c", 3),
    ("a and b or c", 3),
])
def test_boolean_operators(expr, expected):
    source = f"def f():\n    return {expr}\n"
    assert cc(source) == expected


# complexity-6: ternary +1
def test_ternary():
    source = "def f():\n    return a if cond else b\n"
    assert cc(source) == 2


# complexity-7: comprehension for/if clauses +1 each
@pytest.mark.parametrize("body,expected", [
    ("return [x for x in xs]", 2),
    ("return [x for x in xs if x > 0]", 3),
    ("return [x for xs in g for x in xs]", 3),
])
def test_comprehension_clauses(body, expected):
    assert cc(func(body)) == expected


# complexity-8: non-wildcard match case +1; wildcard case _ +0
@pytest.mark.parametrize("case_count,has_wildcard,expected", [
    (1, False, 2),
    (2, False, 3),
    (2, True, 3),
])
def test_match_case(case_count, has_wildcard, expected):
    lines = ["match x:"]
    for i in range(case_count):
        lines += [f"    case {i}:", "        pass"]
    if has_wildcard:
        lines += ["    case _:", "        pass"]
    body = "\n    ".join(lines)
    source = f"def f():\n    {body}\n"
    assert cc(source) == expected


# complexity-9: assert +1
@pytest.mark.parametrize("assert_count,expected", [
    (1, 2),
    (2, 3),
])
def test_assert(assert_count, expected):
    stmts = "\n    ".join(["assert x"] * assert_count)
    source = f"def f():\n    {stmts}\n"
    assert cc(source) == expected


# complexity-10: with adds 0
@pytest.mark.parametrize("with_count,expected", [
    (1, 1),
    (2, 1),
])
def test_with_adds_zero(with_count, expected):
    stmts = "\n    ".join([f"with ctx{i} as v{i}: pass" for i in range(with_count)])
    source = f"def f():\n    {stmts}\n"
    assert cc(source) == expected


# complexity-11: nested functions scored separately
@pytest.mark.parametrize("outer_dp,inner_dp,outer_cc,inner_cc", [
    (0, 2, 1, 3),
    (1, 1, 2, 2),
])
def test_nested_functions(outer_dp, inner_dp, outer_cc, inner_cc):
    outer_stmts = "\n    ".join(["if x: pass"] * outer_dp)
    inner_stmts = "\n        ".join(["if x: pass"] * inner_dp)
    if outer_stmts:
        source = (
            f"def outer():\n"
            f"    {outer_stmts}\n"
            f"    def inner():\n"
            f"        {inner_stmts if inner_stmts else 'pass'}\n"
        )
    else:
        source = (
            f"def outer():\n"
            f"    def inner():\n"
            f"        {inner_stmts if inner_stmts else 'pass'}\n"
        )
    result = cc_named(source)
    assert result["outer"] == outer_cc
    assert result["inner"] == inner_cc


# complexity-12: mixed constructs
@pytest.mark.parametrize("ifs,loops,booleans,asserts,expected", [
    (1, 1, 1, 1, 5),
    (2, 0, 2, 0, 5),
])
def test_mixed_constructs(ifs, loops, booleans, asserts, expected):
    lines = []
    for _ in range(ifs):
        lines.append("if x: pass")
    for _ in range(loops):
        lines.append("for i in x: pass")
    if booleans:
        # booleans extra operands: "a and b" = 1 extra, "a and b and c" = 2 extra
        ops = " and ".join(["x"] * (booleans + 1))
        lines.append(f"y = {ops}")
    for _ in range(asserts):
        lines.append("assert x")
    body = "\n    ".join(lines) if lines else "pass"
    source = f"def f():\n    {body}\n"
    assert cc(source) == expected
