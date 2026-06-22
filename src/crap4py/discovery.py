"""Function discovery and qualified naming (C2, #8) — pure AST layer.

Implements ADR 0003: qualified name uses enclosing classes only; module label
is caller-supplied; line range is the def node's own span.

IO (file walking, gitignore) lives in _discovery_io.py.
"""
import ast
from dataclasses import dataclass


@dataclass
class FunctionEntry:
    qualified_name: str
    module_label: str
    line_range: tuple[int, int]


def discover_functions(paths: list[str]) -> list[FunctionEntry]:
    """Discover all def/async def under the given source paths.

    Delegates file collection to the IO adapter so this module stays IO-free.
    """
    from crap4py._discovery_io import collect_source_files, read_source, relative_label
    entries: list[FunctionEntry] = []
    for filepath in collect_source_files(paths):
        label = relative_label(filepath)
        source = read_source(filepath)
        if source is None:
            continue
        try:
            tree = ast.parse(source, filename=filepath)
        except SyntaxError:
            continue
        entries.extend(_extract_entries(tree, label))
    return entries


def _extract_entries(tree: ast.AST, module_label: str) -> list[FunctionEntry]:
    return _collect_scope(tree, [], module_label)


def _collect_scope(scope: ast.AST, class_stack: list[str], module_label: str) -> list[FunctionEntry]:
    entries: list[FunctionEntry] = []
    for child in ast.iter_child_nodes(scope):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            entries.extend(_collect_function(child, class_stack, module_label))
        elif isinstance(child, ast.ClassDef):
            entries.extend(_collect_scope(child, class_stack + [child.name], module_label))
    return entries


def _collect_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    class_stack: list[str],
    module_label: str,
) -> list[FunctionEntry]:
    qualified_name = ".".join(class_stack + [node.name])
    entry = FunctionEntry(
        qualified_name=qualified_name,
        module_label=module_label,
        line_range=(node.lineno, node.end_lineno),
    )
    nested: list[FunctionEntry] = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nested.extend(_collect_function(child, class_stack, module_label))
        elif isinstance(child, ast.ClassDef):
            nested.extend(_collect_scope(child, class_stack + [child.name], module_label))
    return [entry] + nested
