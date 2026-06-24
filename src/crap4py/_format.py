"""Fixed-width report formatter and JSON serialiser for crap4py (C4, #10).

Formats a list of ReportRow objects into the CRAP Report table or JSON.
"""

from __future__ import annotations

import json

from crap4py._crap import ReportRow
from crap4py.coverage import NA

_COL_HEADERS = ("Function", "Module", "CC", "Cov%", "CRAP")


def _col_widths(rows: list[ReportRow]) -> list[int]:
    widths = [len(h) for h in _COL_HEADERS]
    for row in rows:
        cols = (
            row.qualified_name,
            row.module_label,
            str(row.cc),
            row.cov_percent,
            row.crap_str,
        )
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
        lines.append(
            fmt.format(
                row.qualified_name,
                row.module_label,
                str(row.cc),
                row.cov_percent,
                row.crap_str,
            )
        )
    return "\n".join(lines)


def format_json(rows: list[ReportRow]) -> str:
    """Return the CRAP report serialised as a JSON string."""
    entries = [
        {
            "name": row.qualified_name,
            "module": row.module_label,
            "cc": row.cc,
            "coverage": None if row.coverage is NA else float(row.coverage),
            "crap": None if row.crap is NA else float(row.crap),
        }
        for row in rows
    ]
    finite_crap = [float(r.crap) for r in rows if r.crap is not NA]
    summary = {
        "totalFunctions": len(rows),
        "indeterminateFunctions": sum(1 for r in rows if r.crap is NA),
        "averageCc": round(sum(r.cc for r in rows) / len(rows), 1) if rows else None,
        "averageCrap": round(sum(finite_crap) / len(finite_crap), 1) if finite_crap else None,
        "worstCrap": round(max(finite_crap), 1) if finite_crap else None,
    }
    return json.dumps({"functions": entries, "summary": summary}, indent=2)
