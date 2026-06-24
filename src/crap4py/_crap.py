"""CRAP score computation, sort, and data model (C4, #10).

Pure functions: no IO, no CLI concerns. Consumed by _format.py and __main__.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crap4py.coverage import _NA, NA


def crap_score(cc: int, coverage: float | _NA) -> float | _NA:
    """Return CC² × (1 − coverage)³ + CC, or NA when coverage is NA."""
    if coverage is NA:
        return NA
    cov = float(coverage)
    return cc * cc * (1.0 - cov) ** 3 + cc


def _cov_percent(coverage: float | _NA) -> str:
    if coverage is NA:
        return "N/A"
    pct = float(coverage) * 100.0
    return f"{pct:.1f}%"


def _crap_str(crap: float | _NA) -> str:
    if crap is NA:
        return "N/A"
    return f"{float(crap):.1f}"


@dataclass
class ReportRow:
    qualified_name: str
    module_label: str
    cc: int
    coverage: float | _NA
    crap: float | _NA = field(init=False)
    cov_percent: str = field(init=False)
    crap_str: str = field(init=False)

    def __post_init__(self) -> None:
        self.crap = crap_score(self.cc, self.coverage)
        self.cov_percent = _cov_percent(self.coverage)
        self.crap_str = _crap_str(self.crap)


def _sort_key(row: ReportRow) -> tuple:
    """Sort key: finite CRAP descending (group 0), N/A last (group 1), name ascending."""
    if row.crap is NA:
        return (1, "", row.qualified_name)
    return (0, -float(row.crap), row.qualified_name)


def sort_rows(rows: list[ReportRow]) -> list[ReportRow]:
    """Return rows sorted worst-CRAP-first, N/A last, stable name tiebreak."""
    return sorted(rows, key=_sort_key)
