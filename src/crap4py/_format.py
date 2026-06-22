"""Fixed-width report formatter for crap4py (C4, #10).

Formats a list of ReportRow objects into the CRAP Report table.
"""
from __future__ import annotations

from crap4py._crap import ReportRow

_COL_HEADERS = ("Function", "Module", "CC", "Cov%", "CRAP")


def _col_widths(rows: list[ReportRow]) -> list[int]:
    widths = [len(h) for h in _COL_HEADERS]
    for row in rows:
        cols = (row.qualified_name, row.module_label, str(row.cc),
                row.cov_percent, row.crap_str)
        for i, val in enumerate(cols):
            widths[i] = max(widths[i], len(val))
    return widths


def format_report(rows: list[ReportRow]) -> str:
    """Return the full CRAP Report as a string (no trailing newline)."""
    widths = _col_widths(rows)
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    header = fmt.format(*_COL_HEADERS)
    separator = "-" * len(header)
    underline = "=" * len("CRAP Report")
    lines = ["CRAP Report", underline, header, separator]
    for row in rows:
        lines.append(fmt.format(
            row.qualified_name, row.module_label,
            str(row.cc), row.cov_percent, row.crap_str
        ))
    return "\n".join(lines)
