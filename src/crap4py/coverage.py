"""LCOV branch-coverage resolution per function (C3, #9).

Reads BRDA records from a pre-generated LCOV file and computes
branch coverage for a function given its source file path and line range.

Coverage = (# in-range BRDA with taken >= 1) / (# in-range BRDA).
A function with zero in-range BRDA records is 100% covered (1.0).
Coverage is N/A when the function's source file has no matching SF record.
"""
from __future__ import annotations


class _NA:
    """Sentinel for indeterminate (file-absent) coverage."""
    _instance: "_NA | None" = None

    def __new__(cls) -> "_NA":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "N/A"

    def __str__(self) -> str:
        return "N/A"


NA: _NA = _NA()

# Type alias: BRDA record as (line: int, branch_id: str, taken: int)
_BrdaRecord = tuple[int, str, int]

# Parsed LCOV: SF path → list of BRDA records
LcovData = dict[str, list[_BrdaRecord]]


def parse_lcov(lcov_text: str) -> LcovData:
    """Parse LCOV text and return a dict mapping SF path → BRDA records.

    Only SF and BRDA records are consumed; all other record types are ignored.
    BRDA records with line=0 are skipped (coverage.py bug).
    taken="-" is normalised to 0.
    """
    result: LcovData = {}
    current_sf: str | None = None
    current_records: list[_BrdaRecord] = []

    for raw_line in lcov_text.splitlines():
        line = raw_line.strip()
        if line.startswith("SF:"):
            current_sf = line[3:]
            current_records = []
        elif line == "end_of_record":
            if current_sf is not None:
                result[current_sf] = current_records
            current_sf = None
            current_records = []
        elif line.startswith("BRDA:") and current_sf is not None:
            parts = line[5:].split(",", 3)
            if len(parts) < 4:
                continue
            lineno = int(parts[0])
            if lineno == 0:
                continue
            branch_id = parts[2]
            taken_raw = parts[3]
            taken = 0 if taken_raw == "-" else int(taken_raw)
            current_records.append((lineno, branch_id, taken))

    return result


def _match_sf(source_path: str, lcov_data: LcovData) -> list[_BrdaRecord] | None:
    """Find BRDA records for source_path using exact match or suffix matching.

    Returns None if no SF record matches (file absent → N/A).
    """
    if source_path in lcov_data:
        return lcov_data[source_path]

    norm_source = source_path.replace("\\", "/")
    for sf, records in lcov_data.items():
        norm_sf = sf.replace("\\", "/")
        if norm_sf.endswith("/" + norm_source) or norm_sf == norm_source:
            return records

    return None


def resolve_coverage(
    source_path: str,
    line_range: tuple[int, int],
    lcov_data: LcovData,
) -> float | _NA:
    """Return the branch coverage for a function as a float in [0, 1] or NA.

    source_path: the function's source file path (as discovered by C2).
    line_range:  (start, end) 1-based inclusive range from C2.
    lcov_data:   parsed LCOV from parse_lcov().
    """
    records = _match_sf(source_path, lcov_data)
    if records is None:
        return NA

    start, end = line_range
    in_range = [r for r in records if start <= r[0] <= end]

    if not in_range:
        return 1.0

    taken_count = sum(1 for _, _, taken in in_range if taken >= 1)
    return taken_count / len(in_range)
