"""Architecture boundary check.

Core modules (src/crap4py) must not import IO-level or framework concerns.
Forbidden imports in the core: os, sys, pathlib, subprocess, socket, urllib,
http, requests, click, typer, argparse.

IO adapter modules (named *_io.py) and entrypoints (__main__.py) are excluded
from this check — they are the intentional IO boundary.
"""
import ast
import pathlib

_CORE_DIR = pathlib.Path(__file__).parent.parent / "src" / "crap4py"
_FORBIDDEN = {
    "os", "sys", "pathlib", "subprocess", "socket",
    "urllib", "http", "requests", "click", "typer", "argparse",
}
_IO_BOUNDARY_SUFFIXES = ("_io.py", "__main__.py")


def _top_level_imports(path: pathlib.Path) -> set[str]:
    tree = ast.parse(path.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_core_has_no_forbidden_imports():
    violations: list[str] = []
    for py_file in _CORE_DIR.rglob("*.py"):
        if any(py_file.name.endswith(s) for s in _IO_BOUNDARY_SUFFIXES):
            continue
        bad = _top_level_imports(py_file) & _FORBIDDEN
        if bad:
            violations.append(f"{py_file.relative_to(_CORE_DIR)}: {sorted(bad)}")
    assert not violations, "Core modules must not import IO/framework:\n" + "\n".join(violations)
