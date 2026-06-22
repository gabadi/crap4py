"""Cyclomatic complexity calculator for Python source (C1, #7).

Implements the radon expression-aware model per ADR 0001.
"""
import ast
from dataclasses import dataclass


@dataclass
class FunctionCC:
    name: str
    cc: int


def cyclomatic_complexity(source: str) -> list[FunctionCC]:
    """Return one FunctionCC per def/async def in source, in definition order."""
    tree = ast.parse(source)
    results: list[FunctionCC] = []
    _visit_scope(tree, results)
    return results


def _visit_scope(scope: ast.AST, results: list[FunctionCC]) -> None:
    """Visit direct children looking for function defs and class bodies."""
    for child in ast.iter_child_nodes(scope):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = 1 + _count_function_body(child, results)
            results.append(FunctionCC(name=child.name, cc=cc))
        elif isinstance(child, ast.ClassDef):
            _visit_scope(child, results)


def _count_function_body(func_node: ast.AST, results: list[FunctionCC]) -> int:
    """Count decision points in func_node's body, stopping at nested def boundaries.

    Nested defs are recursively processed and appended to results.
    """
    total = 0
    stack: list[ast.AST] = list(ast.iter_child_nodes(func_node))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = 1 + _count_function_body(node, results)
            results.append(FunctionCC(name=node.name, cc=cc))
            continue
        total += _decision_points(node)
        stack.extend(ast.iter_child_nodes(node))
    return total


def _decision_points(node: ast.AST) -> int:
    """Return decision points contributed by a single AST node."""
    if isinstance(node, ast.If):
        return 1
    if isinstance(node, (ast.For, ast.While)):
        return 1 + (1 if node.orelse else 0)
    if isinstance(node, ast.ExceptHandler):
        return 1
    if isinstance(node, ast.BoolOp):
        return len(node.values) - 1
    if isinstance(node, ast.IfExp):
        return 1
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
        return _comprehension_points(node.generators)
    if isinstance(node, ast.Assert):
        return 1
    if isinstance(node, ast.match_case):
        if _is_wildcard(node.pattern) and node.guard is None:
            return 0
        return 1
    return 0


def _comprehension_points(generators: list) -> int:
    total = 0
    for gen in generators:
        total += 1
        total += len(gen.ifs)
    return total


def _is_wildcard(pattern: ast.AST) -> bool:
    return isinstance(pattern, ast.MatchAs) and pattern.name is None and pattern.pattern is None
