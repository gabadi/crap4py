"""CLI entrypoint for crap4py.

Usage: uv run crap4py --lcov <lcov_file> <source_path> [<source_path> ...]

Prints one row per discovered function with:
  qualified_name  module_label  cc  coverage
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

    from crap4py.discovery import discover_functions
    from crap4py.complexity import cyclomatic_complexity
    from crap4py.coverage import parse_lcov, resolve_coverage, NA

    lcov_path = args.lcov
    if not os.path.isfile(lcov_path):
        print(f"error: LCOV file not found: {lcov_path}", file=sys.stderr)
        sys.exit(1)

    with open(lcov_path) as f:
        lcov_text = f.read()
    lcov_data = parse_lcov(lcov_text)

    entries = discover_functions(args.paths)

    rows = []
    for entry in entries:
        src_path = entry.module_label
        try:
            with open(src_path) as f:
                source = f.read()
        except OSError:
            continue

        cc_results = {r.name: r.cc for r in cyclomatic_complexity(source)}
        qualified = entry.qualified_name
        bare_name = qualified.rsplit(".", 1)[-1]
        cc = cc_results.get(bare_name, 1)

        cov = resolve_coverage(src_path, entry.line_range, lcov_data)
        if cov is NA:
            cov_str = "N/A"
        else:
            cov_str = f"{float(cov):.4g}" if float(cov) not in (0.0, 1.0) else (
                "0.0" if float(cov) == 0.0 else "1.0"
            )

        rows.append((qualified, entry.module_label, cc, cov_str))

    if not rows:
        print("no functions found")
        return

    col_w = [
        max(len("function"), max(len(r[0]) for r in rows)),
        max(len("module"), max(len(r[1]) for r in rows)),
        max(len("cc"), max(len(str(r[2])) for r in rows)),
        max(len("coverage"), max(len(r[3]) for r in rows)),
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_w)
    print(fmt.format("function", "module", "cc", "coverage"))
    print("  ".join("-" * w for w in col_w))
    for qname, mod, cc, cov_str in rows:
        print(fmt.format(qname, mod, cc, cov_str))


if __name__ == "__main__":
    main()
