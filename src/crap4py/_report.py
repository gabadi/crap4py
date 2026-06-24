"""Report-building logic: discover functions → score → CRAP rows.

This module owns the data pipeline. It is fully testable without filesystem
side-effects beyond what the injected IO callables do.
"""

from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
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


def _group_by_module(entries: list[FunctionEntry]) -> dict[str, list[FunctionEntry]]:
    groups: dict[str, list[FunctionEntry]] = defaultdict(list)
    for entry in entries:
        groups[entry.module_label].append(entry)
    return dict(groups)


def _score_file(
    module_label: str,
    entries: list[FunctionEntry],
    lcov_data: LcovData,
    open_fn: Callable[[str], str],
) -> list[ReportRow]:
    """Score all functions in one file, reading and parsing the source exactly once."""
    try:
        source_text = open_fn(module_label)
    except OSError:
        return []
    cc_results = {r.name: r.cc for r in cyclomatic_complexity(source_text)}
    rows = []
    for entry in entries:
        bare_name = entry.qualified_name.rsplit(".", 1)[-1]
        cc = cc_results.get(bare_name, 1)
        cov = resolve_coverage(module_label, entry.line_range, lcov_data)
        rows.append(ReportRow(entry.qualified_name, entry.module_label, cc, cov))
    return rows


def _should_parallelize(groups: dict, max_workers: int | None) -> bool:
    return max_workers is not None and max_workers > 1 and len(groups) > 1


def _parallel_rows(
    groups: dict[str, list[FunctionEntry]],
    lcov_data: LcovData,
    open_fn: Callable[[str], str],
    max_workers: int,
) -> list[ReportRow]:
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_score_file, lbl, es, lcov_data, open_fn) for lbl, es in groups.items()]
        return [row for fut in futures for row in fut.result()]


def _serial_rows(
    groups: dict[str, list[FunctionEntry]],
    lcov_data: LcovData,
    open_fn: Callable[[str], str],
) -> list[ReportRow]:
    return [row for lbl, es in groups.items() for row in _score_file(lbl, es, lcov_data, open_fn)]


def build_report(
    lcov_path: str,
    paths: list[str],
    *,
    fragments: list[str] | None = None,
    open_fn: Callable[[str], str] | None = None,
    max_workers: int | None = None,
) -> list[ReportRow]:
    """Return sorted ReportRow list, one per discovered function.

    fragments: optional path-fragment substring filters (crap4go filterSources).
    open_fn: injectable file reader for testing.
    max_workers: number of parallel workers for file analysis; None means serial.
    """
    if open_fn is None:
        open_fn = _default_open
    lcov_data: LcovData = parse_lcov(open_fn(lcov_path))
    entries = discover_functions(paths)
    if fragments:
        entries = _filter_by_fragments(entries, fragments)
    groups = _group_by_module(entries)
    all_rows = _parallel_rows(groups, lcov_data, open_fn, max_workers) if _should_parallelize(groups, max_workers) else _serial_rows(groups, lcov_data, open_fn)
    return sort_rows(all_rows)
