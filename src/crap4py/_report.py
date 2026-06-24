"""Report-building logic: discover functions → score → CRAP rows.

This module owns the data pipeline. It is fully testable without filesystem
side-effects beyond what the injected IO callables do.
"""

from __future__ import annotations

from typing import Callable

from crap4py._crap import ReportRow, sort_rows
from crap4py.complexity import cyclomatic_complexity
from crap4py.coverage import LcovData, parse_lcov, resolve_coverage
from crap4py.discovery import FunctionEntry, discover_functions


def _default_open(p: str) -> str:
    with open(p) as f:
        return f.read()


def _filter_by_fragments(entries: list[FunctionEntry], fragments: list[str]) -> list[FunctionEntry]:
    return [e for e in entries if any(frag in e.module_label for frag in fragments)]


def _score_entry(
    entry: FunctionEntry,
    lcov_data: LcovData,
    open_fn: Callable[[str], str],
) -> ReportRow | None:
    try:
        source_text = open_fn(entry.module_label)
    except OSError:
        return None
    cc_results = {r.name: r.cc for r in cyclomatic_complexity(source_text)}
    bare_name = entry.qualified_name.rsplit(".", 1)[-1]
    cc = cc_results.get(bare_name, 1)
    cov = resolve_coverage(entry.module_label, entry.line_range, lcov_data)
    return ReportRow(entry.qualified_name, entry.module_label, cc, cov)


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
        open_fn = _default_open

    lcov_data: LcovData = parse_lcov(open_fn(lcov_path))
    entries = discover_functions(paths)

    if fragments:
        entries = _filter_by_fragments(entries, fragments)

    rows = [_score_entry(e, lcov_data, open_fn) for e in entries]
    return sort_rows([r for r in rows if r is not None])
