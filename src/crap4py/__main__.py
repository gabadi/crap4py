"""CLI entrypoint for crap4py — thin adapter shell.

Usage: uv run crap4py --lcov <lcov_file> [--max-crap N] [--max-workers N]
                      <source_path> [<source_path> ...] [-- <fragment> ...]

All report logic lives in crap4py._report; this module handles argument
parsing, filesystem error checking, and printing only.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="crap4py",
        description="Compute CRAP scores per function for Python source files.",
    )
    parser.add_argument("--lcov", required=True, help="Path to LCOV coverage file")
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
        help="Number of parallel workers (positive integer; performance only)",
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


def _validate_max_workers(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        n = int(raw)
    except ValueError:
        return None  # signal error
    if n <= 0:
        return None
    return n


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)

    if args.max_workers is not None:
        workers = _validate_max_workers(args.max_workers)
        if workers is None:
            print(
                f"error: --max-workers requires a positive integer, got {args.max_workers!r}",
                file=sys.stderr,
            )
            sys.exit(1)

    from crap4py._report import build_report
    from crap4py._format import format_report
    from crap4py.coverage import NA

    if not os.path.isfile(args.lcov):
        print(f"error: LCOV file not found: {args.lcov}", file=sys.stderr)
        sys.exit(1)

    try:
        rows = build_report(args.lcov, args.paths, fragments=args.fragments or None)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    print(format_report(rows))

    if args.max_crap is not None:
        for row in rows:
            if row.crap is not NA and float(row.crap) > args.max_crap:
                sys.exit(1)


if __name__ == "__main__":
    main()
