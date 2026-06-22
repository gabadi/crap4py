"""Step handlers for features/complexity.feature."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from crap4py.complexity import cyclomatic_complexity
from acceptance.steps.step_lib import make_registry


class Context:
    def __init__(self):
        self.results = None
        self.source = None


ctx = Context()

STEP_HANDLERS, step, run_step = make_registry()


def _first_cc() -> int:
    assert ctx.results, "No results computed yet"
    return ctx.results[0].cc


def _cc_by_name(name: str) -> int:
    by_name = {r.name: r.cc for r in ctx.results}
    assert name in by_name, f"Function '{name}' not found; got {list(by_name)}"
    return by_name[name]


def _func_body(body: str) -> str:
    lines = body.replace("; ", "\n    ").replace(";", "\n    ")
    return f"def f():\n    {lines}\n"


@step(r"a syntactically valid Python source")
def given_valid_source(m, params):
    ctx.results = None
    ctx.source = None


@step(r'the function body is "(.+)"')
def when_function_body_is(m, params):
    body = params.get("body") or m.group(1)
    ctx.source = _func_body(body)
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r'the function condition is "(.+)"')
def when_function_condition_is(m, params):
    expr = params.get("expression") or m.group(1)
    ctx.source = f"def f():\n    return {expr}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r"the function contains (\d+) `if`, (\d+) `elif`, and (\d+) `else` clauses")
def when_if_elif_else(m, params):
    if_count = int(params.get("if_count", m.group(1)))
    elif_count = int(params.get("elif_count", m.group(2)))
    else_count = int(params.get("else_count", m.group(3)))
    assert else_count in (0, 1), f"else_count must be 0 or 1, got {else_count}"
    # Build an if/elif/else chain: if_count independent ifs before the main chain
    lines = []
    for _ in range(if_count - 1):
        lines.append("if x:")
        lines.append("    pass")
    lines.append("if x:")
    lines.append("    pass")
    for _ in range(elif_count):
        lines.append("elif x:")
        lines.append("    pass")
    if else_count:
        lines.append("else:")
        lines.append("    pass")
    body = "\n    ".join(lines)
    ctx.source = f"def f():\n    {body}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r'the function contains a "(.+)" loop with else="(.+)"')
def when_loop_with_else(m, params):
    loop = params.get("loop") or m.group(1)
    has_else_raw = params.get("has_else") or m.group(2)
    assert loop in ("for", "while"), f"loop must be 'for' or 'while', got {loop!r}"
    assert has_else_raw in ("yes", "no"), f"has_else must be 'yes' or 'no', got {has_else_raw!r}"
    has_else = has_else_raw == "yes"
    if loop == "for":
        lines = ["for i in x:", "    pass"]
    else:
        lines = ["while x:", "    pass"]
    if has_else:
        lines += ["else:", "    pass"]
    body = "\n    ".join(lines)
    ctx.source = f"def f():\n    {body}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r'the function contains a try with (\d+) except handlers and finally="(.+)"')
def when_try_except_finally(m, params):
    except_count = int(params.get("except_count", m.group(1)))
    has_finally_raw = params.get("has_finally") or m.group(2)
    assert has_finally_raw in ("yes", "no"), f"has_finally must be 'yes' or 'no', got {has_finally_raw!r}"
    has_finally = has_finally_raw == "yes"
    lines = ["try:", "    pass"]
    for _ in range(except_count):
        lines += ["except Exception:", "    pass"]
    if has_finally:
        lines += ["finally:", "    pass"]
    body = "\n    ".join(lines)
    ctx.source = f"def f():\n    {body}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r'the function contains a match with (\d+) cases and wildcard="(.+)"')
def when_match_case(m, params):
    case_count = int(params.get("case_count", m.group(1)))
    has_wildcard_raw = params.get("has_wildcard") or m.group(2)
    assert has_wildcard_raw in ("yes", "no"), f"has_wildcard must be 'yes' or 'no', got {has_wildcard_raw!r}"
    has_wildcard = has_wildcard_raw == "yes"
    lines = ["match x:"]
    for i in range(case_count):
        lines += [f"    case {i}:", "        pass"]
    if has_wildcard:
        lines += ["    case _:", "        pass"]
    body = "\n    ".join(lines)
    ctx.source = f"def f():\n    {body}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r"the function contains (\d+) assert statements")
def when_assert_statements(m, params):
    assert_count = int(params.get("assert_count", m.group(1)))
    stmts = "\n    ".join(["assert x"] * assert_count)
    ctx.source = f"def f():\n    {stmts}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r"the function contains (\d+) with statements")
def when_with_statements(m, params):
    with_count = int(params.get("with_count", m.group(1)))
    stmts = "\n    ".join([f"with ctx{i} as v{i}: pass" for i in range(with_count)])
    ctx.source = f"def f():\n    {stmts}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r"the outer function has (\d+) decision points and a nested function with (\d+) decision points")
def when_nested_functions(m, params):
    outer_dp = int(params.get("outer_dp", m.group(1)))
    inner_dp = int(params.get("inner_dp", m.group(2)))
    outer_stmts = "\n    ".join(["if x: pass"] * outer_dp) if outer_dp else ""
    inner_stmts = "\n        ".join(["if x: pass"] * inner_dp) if inner_dp else "pass"
    if outer_stmts:
        ctx.source = (
            f"def outer():\n"
            f"    {outer_stmts}\n"
            f"    def inner():\n"
            f"        {inner_stmts}\n"
        )
    else:
        ctx.source = (
            f"def outer():\n"
            f"    def inner():\n"
            f"        {inner_stmts}\n"
        )
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r"the function contains (\d+) if, (\d+) for loops, (\d+) extra boolean operands, and (\d+) assert statements")
def when_mixed_constructs(m, params):
    ifs = int(params.get("ifs", m.group(1)))
    loops = int(params.get("loops", m.group(2)))
    booleans = int(params.get("booleans", m.group(3)))
    asserts = int(params.get("asserts", m.group(4)))
    lines = []
    for _ in range(ifs):
        lines.append("if x: pass")
    for _ in range(loops):
        lines.append("for i in x: pass")
    if booleans:
        ops = " and ".join(["x"] * (booleans + 1))
        lines.append(f"y = {ops}")
    for _ in range(asserts):
        lines.append("assert x")
    body = "\n    ".join(lines) if lines else "pass"
    ctx.source = f"def f():\n    {body}\n"
    ctx.results = cyclomatic_complexity(ctx.source)


@step(r"the cyclomatic complexity is (\d+)")
def then_cc_is(m, params):
    expected = int(params.get("cc", m.group(1)))
    actual = _first_cc()
    assert actual == expected, f"Expected CC {expected}, got {actual}\nSource:\n{ctx.source}"


@step(r"the cyclomatic complexity of the outer function is (\d+)")
def then_outer_cc_is(m, params):
    expected = int(params.get("outer_cc", m.group(1)))
    actual = _cc_by_name("outer")
    assert actual == expected, f"Expected outer CC {expected}, got {actual}"


@step(r"the cyclomatic complexity of the nested function is (\d+)")
def then_inner_cc_is(m, params):
    expected = int(params.get("inner_cc", m.group(1)))
    actual = _cc_by_name("inner")
    assert actual == expected, f"Expected inner CC {expected}, got {actual}"


