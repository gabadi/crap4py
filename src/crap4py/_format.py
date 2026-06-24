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


def _entry_dict(row: ReportRow) -> dict:
    return {
        "name": row.qualified_name,
        "module": row.module_label,
        "cc": row.cc,
        "coverage": None if row.coverage is NA else float(row.coverage),
        "crap": None if row.crap is NA else float(row.crap),
    }


def _finite_crap(rows: list[ReportRow]) -> list[float]:
    return [float(r.crap) for r in rows if r.crap is not NA]


def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 1) if values else None


def _json_summary(rows: list[ReportRow]) -> dict:
    fc = _finite_crap(rows)
    return {
        "totalFunctions": len(rows),
        "indeterminateFunctions": sum(1 for r in rows if r.crap is NA),
        "averageCc": round(sum(r.cc for r in rows) / len(rows), 1) if rows else None,
        "averageCrap": _avg(fc),
        "worstCrap": round(max(fc), 1) if fc else None,
    }


def format_json(rows: list[ReportRow]) -> str:
    """Return the CRAP report serialised as a JSON string."""
    return json.dumps({"functions": [_entry_dict(r) for r in rows], "summary": _json_summary(rows)}, indent=2)
