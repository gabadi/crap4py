"""Function discovery and qualified naming (C2, #8) — pure AST layer.

Implements ADR 0003: qualified name uses enclosing classes only; module label
is caller-supplied; line range is the def node's own span.

IO (file walking, gitignore) lives in _discovery_io.py. This module owns only
the pure-AST traversal; it does not import os, sys, or pathlib.

``discover_functions`` accepts optional IO adapter callables so the AST logic
can be exercised without touching the filesystem. When called with no adapters
the real filesystem adapters from ``_discovery_io`` are used as defaults —
this single inward call is the only cross-boundary touch in this module, and
it is deferred to call time so tests can inject stubs without importing IO.
"""

import ast
from dataclasses import dataclass
from typing import Callable


@dataclass
class FunctionEntry:
    qualified_name: str
    module_label: str
    line_range: tuple[int, int]


def _io_defaults(
    root: str | None,
) -> tuple[
    Callable[[list[str]], list[str]],
    Callable[[str], str | None],
    Callable[[str], str],
]:
    """Load and return the default filesystem IO adapters from _discovery_io."""
    from crap4py._discovery_io import (
        collect_source_files as _collect_all,
    )
    from crap4py._discovery_io import (
        read_source as _read,
    )
    from crap4py._discovery_io import (
        relative_label as _label_fn,
    )

    return (
        lambda ps: _collect_all(ps, root),
        _read,
        lambda fp: _label_fn(fp, root),
    )


def _resolve_adapters(
    root: str | None,
    collect_files: Callable[[list[str]], list[str]] | None,
    read_source: Callable[[str], str | None] | None,
    file_label: Callable[[str], str] | None,
) -> tuple[
    Callable[[list[str]], list[str]],
    Callable[[str], str | None],
    Callable[[str], str],
]:
    """Return concrete IO adapter callables, filling missing ones from _io_defaults."""
    supplied = (collect_files, read_source, file_label)
    if all(fn is not None for fn in supplied):
        return collect_files, read_source, file_label  # type: ignore[return-value]
    defaults = _io_defaults(root)
    resolved = tuple(fn if fn is not None else dflt for fn, dflt in zip(supplied, defaults))
    return resolved  # type: ignore[return-value]


def _parse_file(
    filepath: str,
    read_source: Callable[[str], str | None],
    file_label: Callable[[str], str],
) -> list[FunctionEntry]:
    """Parse one source file and return its function entries, skipping on read/parse error."""
    source = read_source(filepath)
    if source is None:
        return []
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []
    return _extract_entries(tree, file_label(filepath))


def discover_functions(
    paths: list[str],
    *,
    root: str | None = None,
    collect_files: Callable[[list[str]], list[str]] | None = None,
    read_source: Callable[[str], str | None] | None = None,
    file_label: Callable[[str], str] | None = None,
) -> list[FunctionEntry]:
    """Discover all def/async def under the given source paths.

    ``root`` sets the working-directory anchor for gitignore and relative
    labels. Defaults to ``os.getcwd()`` via the IO adapter.

    When called without adapter arguments, delegates file IO to
    ``crap4py._discovery_io``. Pass explicit callables to test without IO.
    """
    collect_files, read_source, file_label = _resolve_adapters(root, collect_files, read_source, file_label)
    entries: list[FunctionEntry] = []
    for filepath in collect_files(paths):
        entries.extend(_parse_file(filepath, read_source, file_label))
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
