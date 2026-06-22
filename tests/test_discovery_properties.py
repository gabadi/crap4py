"""Property tests for function discovery (architect-owned).

Run separately: uv run pytest tests/test_discovery_properties.py
"""
import ast
import keyword
import textwrap
from hypothesis import given, assume, settings
from hypothesis import strategies as st
from crap4py.discovery import FunctionEntry, _extract_entries


# --- Source generators ---

_VALID_NAME = st.text(
    alphabet=st.characters(whitelist_categories=("Ll",), min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=8,
).filter(lambda s: not keyword.iskeyword(s))


def _function_source(name: str, body: str = "pass") -> str:
    return f"def {name}():\n    {body}\n"


def _class_with_method(class_name: str, method_name: str) -> str:
    return f"class {class_name}:\n    def {method_name}(self):\n        pass\n"


def _parse(source: str) -> ast.AST:
    return ast.parse(textwrap.dedent(source))


# --- Properties ---

@given(st.lists(_VALID_NAME, min_size=1, max_size=10, unique=True))
def test_entry_count_matches_function_count(names):
    """Number of entries equals number of top-level def statements."""
    source = "\n".join(_function_source(n) for n in names)
    entries = _extract_entries(_parse(source), "test.py")
    assert len(entries) == len(names)


@given(st.lists(_VALID_NAME, min_size=1, max_size=8, unique=True))
def test_function_names_preserved_in_order(names):
    """Qualified names in output match the def names in definition order."""
    source = "\n".join(_function_source(n) for n in names)
    entries = _extract_entries(_parse(source), "test.py")
    assert [e.qualified_name for e in entries] == names


@given(_VALID_NAME, _VALID_NAME)
def test_method_qualified_by_class(class_name, method_name):
    """Method entry qualified name is Class.method."""
    capitalized = class_name.capitalize()
    assume(not keyword.iskeyword(capitalized))
    assume(class_name != method_name)
    source = _class_with_method(capitalized, method_name)
    entries = _extract_entries(_parse(source), "mod.py")
    qualified_names = [e.qualified_name for e in entries]
    assert f"{capitalized}.{method_name}" in qualified_names


@given(st.lists(_VALID_NAME, min_size=1, max_size=6, unique=True))
def test_line_range_start_le_end(names):
    """Every entry's line range start is ≤ end."""
    source = "\n".join(_function_source(n) for n in names)
    entries = _extract_entries(_parse(source), "x.py")
    for e in entries:
        assert e.line_range[0] <= e.line_range[1], (
            f"{e.qualified_name}: start {e.line_range[0]} > end {e.line_range[1]}"
        )


@given(st.text(min_size=1, max_size=40).filter(lambda s: "\0" not in s))
def test_module_label_preserved_verbatim(label):
    """module_label is stored exactly as passed, never transformed."""
    source = "def f():\n    pass\n"
    entries = _extract_entries(_parse(source), label)
    assert all(e.module_label == label for e in entries)


@given(st.lists(_VALID_NAME, min_size=1, max_size=5, unique=True))
def test_discovery_is_deterministic(names):
    """Calling _extract_entries twice on the same tree yields identical results."""
    source = "\n".join(_function_source(n) for n in names)
    tree = _parse(source)
    first = _extract_entries(tree, "stable.py")
    second = _extract_entries(tree, "stable.py")
    assert first == second


@given(st.lists(_VALID_NAME, min_size=0, max_size=4, unique=True))
def test_empty_source_or_no_functions(names):
    """A module with no def statements produces zero entries."""
    lines = [f"{n} = 1" for n in names]
    source = "\n".join(lines) if lines else "x = 1"
    entries = _extract_entries(_parse(source), "vars.py")
    assert entries == []


@given(
    outer=_VALID_NAME,
    inner=_VALID_NAME,
)
def test_nested_function_appears_as_separate_entry(outer, inner):
    """A nested def produces its own entry named by its own def name (not qualified by enclosing function)."""
    assume(outer != inner)
    source = (
        f"def {outer}():\n"
        f"    def {inner}():\n"
        f"        pass\n"
    )
    entries = _extract_entries(_parse(source), "nested.py")
    names = [e.qualified_name for e in entries]
    assert outer in names
    assert inner in names
    assert f"{outer}.{inner}" not in names
