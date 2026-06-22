"""Pure report-building logic extracted from the CLI entrypoint.

This module owns the data pipeline: discover functions → score complexity →
resolve coverage → format rows. It is fully testable without filesystem
side-effects beyond what the injected IO callables do.
"""
from __future__ import annotations

from typing import Callable

from crap4py.discovery import discover_functions
from crap4py.complexity import cyclomatic_complexity
from crap4py.coverage import parse_lcov, resolve_coverage, NA, LcovData


def build_rows(
    lcov_path: str,
    paths: list[str],
    *,
    open_fn: Callable[[str], str] | None = None,
) -> list[tuple[str, str, int, str]]:
    """Return one row per function: (qualified_name, module_label, cc, cov_str).

    open_fn reads a file path and returns its text. Defaults to the real open().
    Returns an empty list when no functions are found.
    """
    if open_fn is None:
        def open_fn(p: str) -> str:
            with open(p) as f:
                return f.read()

    lcov_text = open_fn(lcov_path)
    lcov_data: LcovData = parse_lcov(lcov_text)
    entries = discover_functions(paths)

    rows: list[tuple[str, str, int, str]] = []
    for entry in entries:
        try:
            source_text = open_fn(entry.module_label)
        except OSError:
            continue
        cc_results = {r.name: r.cc for r in cyclomatic_complexity(source_text)}
        bare_name = entry.qualified_name.rsplit(".", 1)[-1]
        cc = cc_results.get(bare_name, 1)
        cov = resolve_coverage(entry.module_label, entry.line_range, lcov_data)
        cov_str = _format_coverage(cov)
        rows.append((entry.qualified_name, entry.module_label, cc, cov_str))

    return rows


def _format_coverage(cov: float | object) -> str:
    if cov is NA:
        return "N/A"
    f = float(cov)  # type: ignore[arg-type]
    if f == 0.0:
        return "0.0"
    if f == 1.0:
        return "1.0"
    return f"{f:.4g}"


_HEADERS = ("function", "module", "cc", "coverage")


def _col_widths(rows: list[tuple[str, str, int, str]]) -> list[int]:
    return [
        max(len(h), max(len(str(r[i])) for r in rows))
        for i, h in enumerate(_HEADERS)
    ]


def format_table(rows: list[tuple[str, str, int, str]]) -> str:
    """Return a formatted fixed-width table string (no trailing newline on last line)."""
    if not rows:
        return "no functions found"
    col_w = _col_widths(rows)
    fmt = "  ".join(f"{{:<{w}}}" for w in col_w)
    lines = [
        fmt.format(*_HEADERS),
        "  ".join("-" * w for w in col_w),
    ]
    for row in rows:
        lines.append(fmt.format(*row))
    return "\n".join(lines)
