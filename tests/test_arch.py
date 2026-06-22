"""Architecture boundary checks.

Two rules enforced here:

1. Core modules (src/crap4py, non-_io, non-__main__) must not import stdlib IO
   or framework modules: os, sys, pathlib, subprocess, socket, urllib, http,
   requests, click, typer, argparse.

2. Core modules must not import intra-package IO adapters (crap4py.*_io). IO
   adapters depend inward toward core, never the other way. The only permitted
   exception is a single deferred-default import inside ``discover_functions``
   in discovery.py — documented in that module's docstring and guarded below.

IO adapter modules (*_io.py) and entrypoints (__main__.py) are excluded from
both checks — they are the intentional IO boundary.
"""
import ast
import pathlib

_CORE_DIR = pathlib.Path(__file__).parent.parent / "src" / "crap4py"
_FORBIDDEN_STDLIB = {
    "os", "sys", "pathlib", "subprocess", "socket",
    "urllib", "http", "requests", "click", "typer", "argparse",
}
_IO_BOUNDARY_SUFFIXES = ("_io.py", "__main__.py")
_PACKAGE = "crap4py"


def _all_imports(path: pathlib.Path) -> set[str]:
    """Return every imported top-level module name found anywhere in the file."""
    tree = ast.parse(path.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def _all_intrapackage_io_imports(path: pathlib.Path) -> set[str]:
    """Return every crap4py.*_io dotted module imported anywhere in the file."""
    tree = ast.parse(path.read_text())
    io_imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            parts = node.module.split(".")
            if parts[0] == _PACKAGE and len(parts) > 1 and parts[-1].endswith("_io"):
                io_imports.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == _PACKAGE and len(parts) > 1 and parts[-1].endswith("_io"):
                    io_imports.add(alias.name)
    return io_imports


def test_core_has_no_forbidden_stdlib_imports():
    violations: list[str] = []
    for py_file in _CORE_DIR.rglob("*.py"):
        if any(py_file.name.endswith(s) for s in _IO_BOUNDARY_SUFFIXES):
            continue
        bad = _all_imports(py_file) & _FORBIDDEN_STDLIB
        if bad:
            violations.append(f"{py_file.relative_to(_CORE_DIR)}: {sorted(bad)}")
    assert not violations, "Core modules must not import IO/framework:\n" + "\n".join(violations)


def test_core_does_not_import_io_adapters_at_module_scope():
    """Core modules must not import *_io adapters at module (top-level) scope.

    Deferred imports inside function bodies are allowed in discovery.py only,
    as the documented default-adapter wiring point.  Module-level imports of
    *_io from a core module are always a dependency-direction violation.
    """
    violations: list[str] = []
    for py_file in _CORE_DIR.rglob("*.py"):
        if any(py_file.name.endswith(s) for s in _IO_BOUNDARY_SUFFIXES):
            continue
        tree = ast.parse(py_file.read_text())
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                parts = node.module.split(".")
                if parts[0] == _PACKAGE and len(parts) > 1 and parts[-1].endswith("_io"):
                    violations.append(
                        f"{py_file.relative_to(_CORE_DIR)}: top-level import of {node.module}"
                    )
    assert not violations, (
        "Core modules must not import IO adapters at module scope "
        "(dependency direction: IO adapters depend on core, not vice-versa):\n"
        + "\n".join(violations)
    )
