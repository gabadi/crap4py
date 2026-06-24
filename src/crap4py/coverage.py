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


def _parse_brda(line: str) -> "_BrdaRecord | None":
    """Parse a BRDA line body (after 'BRDA:') and return a record or None to skip."""
    parts = line[5:].split(",", 3)
    if len(parts) < 4:
        return None
    lineno = int(parts[0])
    if lineno == 0:
        return None
    taken_raw = parts[3]
    return (lineno, parts[2], 0 if taken_raw == "-" else int(taken_raw))


class _LcovParseState:
    """Mutable state carrier for the LCOV line-by-line parser."""

    def __init__(self) -> None:
        self.result: LcovData = {}
        self.current_sf: str | None = None
        self.current_records: list[_BrdaRecord] = []

    def on_sf(self, path: str) -> None:
        self.current_sf = path
        self.current_records = []

    def on_end_of_record(self) -> None:
        if self.current_sf is not None:
            self.result[self.current_sf] = self.current_records
        self.current_sf = None
        self.current_records = []

    def on_brda(self, line: str) -> None:
        record = _parse_brda(line)
        if record is not None:
            self.current_records.append(record)


def parse_lcov(lcov_text: str) -> LcovData:
    """Parse LCOV text and return a dict mapping SF path → BRDA records.

    Only SF and BRDA records are consumed; all other record types are ignored.
    BRDA records with line=0 are skipped (coverage.py bug).
    taken="-" is normalised to 0.
    """
    state = _LcovParseState()
    for raw_line in lcov_text.splitlines():
        line = raw_line.strip()
        if line.startswith("SF:"):
            state.on_sf(line[3:])
        elif line == "end_of_record":
            state.on_end_of_record()
        elif line.startswith("BRDA:") and state.current_sf is not None:
            state.on_brda(line)
    return state.result


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


def _branch_coverage_ratio(in_range: list[_BrdaRecord]) -> float:
    """Compute taken/total ratio for a non-empty list of in-range BRDA records."""
    taken_count = sum(1 for _, _, taken in in_range if taken >= 1)
    return taken_count / len(in_range)


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
    return 1.0 if not in_range else _branch_coverage_ratio(in_range)
