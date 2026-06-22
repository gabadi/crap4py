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
    return _collect_from_scope(tree)


# --- Traversal layer ---

def _collect_from_scope(scope: ast.AST) -> list[FunctionCC]:
    """Walk direct children of a scope, collecting FunctionCC entries."""
    results: list[FunctionCC] = []
    for child in ast.iter_child_nodes(scope):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            results.extend(_score_function(child))
        elif isinstance(child, ast.ClassDef):
            results.extend(_collect_from_scope(child))
    return results


def _score_function(func_node: ast.AST) -> list[FunctionCC]:
    """Score a function node: returns its own FunctionCC followed by nested ones."""
    own_points = 0
    nested: list[FunctionCC] = []
    stack: list[ast.AST] = list(ast.iter_child_nodes(func_node))
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            nested.extend(_score_function(node))
            continue
        own_points += _decision_points(node)
        stack.extend(ast.iter_child_nodes(node))
    return [FunctionCC(name=func_node.name, cc=1 + own_points)] + nested


# --- Decision-point rules (ADR 0001) ---

def _decision_points(node: ast.AST) -> int:
    """Return decision points contributed by a single AST node."""
    if isinstance(node, (ast.If, ast.ExceptHandler, ast.IfExp, ast.Assert)):
        return 1
    if isinstance(node, (ast.For, ast.While)):
        return 1 + (1 if node.orelse else 0)
    if isinstance(node, ast.BoolOp):
        return len(node.values) - 1
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
        return _comprehension_points(node.generators)
    if isinstance(node, ast.match_case):
        return _match_case_points(node)
    return 0


def _match_case_points(node: ast.match_case) -> int:
    if _is_wildcard(node.pattern) and node.guard is None:
        return 0
    return 1


def _comprehension_points(generators: list) -> int:
    total = 0
    for gen in generators:
        total += 1
        total += len(gen.ifs)
    return total


def _is_wildcard(pattern: ast.AST) -> bool:
    return isinstance(pattern, ast.MatchAs) and pattern.name is None and pattern.pattern is None
