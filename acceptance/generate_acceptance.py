"""Acceptance entrypoint generator.

Reads a gherkin-parser JSON output file and emits a Python test module
(acceptance/generated/<feature_stem>_acceptance.py) with one test function
per scenario+example row.

Usage: python acceptance/generate_acceptance.py <parsed.json> <steps_module> <out_dir>
"""
import json
import re
import sys
import os


def sanitize(name: str) -> str:
    return re.sub(r"\W+", "_", name).strip("_").lower()[:60]


def generate(parsed: dict, steps_module: str, feature_stem: str) -> str:
    lines = [
        "import sys, os",
        f"sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))",
        f"sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))",
        f"from acceptance.steps.{steps_module} import run_step",
        "",
    ]

    background = parsed.get("background", [])
    scenarios = parsed.get("scenarios", [])

    test_count = 0
    for scenario in scenarios:
        name = scenario["name"]
        steps = scenario["steps"]
        examples = scenario.get("examples", [{}])

        for i, example in enumerate(examples):
            fn_name = f"test_{sanitize(name)}_{i}"
            lines.append(f"def {fn_name}():")
            lines.append(f'    """Scenario: {name} — example {i}"""')

            # background steps
            for step in background:
                kw = step["keyword"]
                text = step["text"]
                lines.append(f"    run_step({kw!r}, {text!r}, {example!r})")

            # scenario steps
            for step in steps:
                kw = step["keyword"]
                text = _expand(step["text"], example)
                lines.append(f"    run_step({kw!r}, {text!r}, {example!r})")

            lines.append("")
            test_count += 1

    # runner
    lines.append("if __name__ == '__main__':")
    lines.append("    import traceback, sys")
    lines.append("    passed = failed = 0")

    fns = [l.split("def ")[1].split("()")[0] for l in lines if l.startswith("def test_")]
    for fn in fns:
        lines.append(f"    try:")
        lines.append(f"        {fn}()")
        lines.append(f"        print('PASS {fn}')")
        lines.append(f"        passed += 1")
        lines.append(f"    except Exception as e:")
        lines.append(f"        print(f'FAIL {fn}: {{e}}')")
        lines.append(f"        traceback.print_exc()")
        lines.append(f"        failed += 1")
    lines.append("    print(f'\\n{passed} passed, {failed} failed')")
    lines.append("    sys.exit(0 if failed == 0 else 1)")
    lines.append("")

    return "\n".join(lines)


def _expand(text: str, example: dict) -> str:
    """Replace <param> placeholders with example values."""
    for key, val in example.items():
        text = text.replace(f"<{key}>", val)
    return text


def main():
    if len(sys.argv) < 4:
        print(f"usage: {sys.argv[0]} <parsed.json> <steps_module> <out_dir>")
        sys.exit(1)

    parsed_path = sys.argv[1]
    steps_module = sys.argv[2]
    out_dir = sys.argv[3]

    with open(parsed_path) as f:
        parsed = json.load(f)

    feature_stem = os.path.basename(parsed_path).replace("_parsed.json", "").replace(".json", "")
    code = generate(parsed, steps_module, feature_stem)

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{feature_stem}_acceptance.py")
    with open(out_path, "w") as f:
        f.write(code)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    main()
