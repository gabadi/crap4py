"""Report-building logic: discover functions → score → CRAP rows.

This module owns the data pipeline. It is fully testable without filesystem
side-effects beyond what the injected IO callables do.
"""
from __future__ import annotations

from typing import Callable

from crap4py.discovery import discover_functions
from crap4py.complexity import cyclomatic_complexity
from crap4py.coverage import parse_lcov, resolve_coverage, NA, LcovData
from crap4py._crap import ReportRow, sort_rows


def build_report(
    lcov_path: str,
    paths: list[str],
    *,
    fragments: list[str] | None = None,
    open_fn: Callable[[str], str] | None = None,
) -> list[ReportRow]:
    """Return sorted ReportRow list, one per discovered function.

    fragments: optional path-fragment substring filters (crap4go filterSources).
    open_fn: injectable file reader for testing.
    """
    if open_fn is None:
        def open_fn(p: str) -> str:
            with open(p) as f:
                return f.read()

    lcov_text = open_fn(lcov_path)
    lcov_data: LcovData = parse_lcov(lcov_text)
    entries = discover_functions(paths)

    if fragments:
        entries = [e for e in entries if any(frag in e.module_label for frag in fragments)]

    rows: list[ReportRow] = []
    for entry in entries:
        try:
            source_text = open_fn(entry.module_label)
        except OSError:
            continue
        cc_results = {r.name: r.cc for r in cyclomatic_complexity(source_text)}
        bare_name = entry.qualified_name.rsplit(".", 1)[-1]
        cc = cc_results.get(bare_name, 1)
        cov = resolve_coverage(entry.module_label, entry.line_range, lcov_data)
        rows.append(ReportRow(entry.qualified_name, entry.module_label, cc, cov))

    return sort_rows(rows)
