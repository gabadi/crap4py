"""CLI entrypoint for crap4py — thin adapter shell.

Usage: uv run crap4py --lcov <lcov_file> <source_path> [<source_path> ...]

All report logic lives in crap4py._report; this module handles argument
parsing, filesystem error checking, and printing only.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="crap4py",
        description="Compute CRAP scores per function for Python source files.",
    )
    parser.add_argument("--lcov", required=True, help="Path to LCOV coverage file")
    parser.add_argument("paths", nargs="+", help="Source paths to analyse")
    args = parser.parse_args()

    from crap4py._report import build_rows, format_table

    if not os.path.isfile(args.lcov):
        print(f"error: LCOV file not found: {args.lcov}", file=sys.stderr)
        sys.exit(1)

    try:
        rows = build_rows(args.lcov, args.paths)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    print(format_table(rows))


if __name__ == "__main__":
    main()
