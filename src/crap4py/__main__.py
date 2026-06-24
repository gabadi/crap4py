"""CLI entrypoint for crap4py — thin adapter shell.

Usage: uv run crap4py --lcov <lcov_file> [--max-crap N] [--max-workers N]
                      [--format table|json] [--version]
                      <source_path> [<source_path> ...] [-- <fragment> ...]

All report logic lives in crap4py._report; this module handles argument
parsing, filesystem error checking, and printing only.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def _get_version() -> str:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("crap4py")
    except PackageNotFoundError:
        return "0.0.0"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="crap4py",
        description="Compute CRAP scores per function for Python source files.",
    )
    parser.add_argument("--version", action="version", version=f"crap4py {_get_version()}")
    parser.add_argument("--lcov", required=True, help="Path to LCOV coverage file")
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        dest="format",
        help="Output format: table (default) or json",
    )
    parser.add_argument(
        "--max-crap",
        type=float,
        default=None,
        metavar="N",
        help="Exit non-zero if any function's CRAP score exceeds N",
    )
    parser.add_argument(
        "--max-workers",
        type=str,
        default=None,
        metavar="N",
        help="Number of parallel workers for file analysis (positive integer)",
    )
    parser.add_argument(
        "--fragment",
        action="append",
        dest="fragments",
        default=None,
        metavar="FRAGMENT",
        help="Path-fragment filter: only analyse source files whose path contains FRAGMENT",
    )
    parser.add_argument("paths", nargs="+", help="Source paths to analyse")
    return parser.parse_args(argv)


def _validate_max_workers(raw: str) -> int | None:
    try:
        n = int(raw)
    except ValueError:
        return None
    if n <= 0:
        return None
    return n


def _resolve_workers(raw: str | None) -> int | None:
    if raw is None:
        return None
    n = _validate_max_workers(raw)
    if n is None:
        print(
            f"error: --max-workers requires a positive integer, got {raw!r}",
            file=sys.stderr,
        )
        sys.exit(1)
    return n


def _check_crap_gate(rows: list, max_crap: float) -> None:
    from crap4py.coverage import NA

    for row in rows:
        if row.crap is not NA and float(row.crap) > max_crap:
            sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    from crap4py._format import format_json, format_report
    from crap4py._report import build_report

    args = _parse_args(argv)
    max_workers = _resolve_workers(args.max_workers)

    if not os.path.isfile(args.lcov):
        print(f"error: LCOV file not found: {args.lcov}", file=sys.stderr)
        sys.exit(1)

    try:
        rows = build_report(args.lcov, args.paths, fragments=args.fragments or None, max_workers=max_workers)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(format_json(rows))
    else:
        print(format_report(rows))

    if args.max_crap is not None:
        _check_crap_gate(rows, args.max_crap)


if __name__ == "__main__":
    main()
