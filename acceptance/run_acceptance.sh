#!/usr/bin/env bash
# Run acceptance tests for all feature files.
# Usage: ./acceptance/run_acceptance.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARSED_DIR="$REPO_ROOT/acceptance/parsed"
GENERATED_DIR="$REPO_ROOT/acceptance/generated"

mkdir -p "$PARSED_DIR" "$GENERATED_DIR"

# Feature → steps module mapping
declare -A STEPS_MAP
STEPS_MAP[complexity]="complexity_steps"

FAILED=0
PASSED=0

for feature_file in "$REPO_ROOT"/features/*.feature; do
    stem="$(basename "$feature_file" .feature)"

    # Skip QA feature files (owned by QA role)
    if [[ "$stem" == *_qa ]]; then
        continue
    fi

    steps_mod="${STEPS_MAP[$stem]:-}"
    if [[ -z "$steps_mod" ]]; then
        echo "SKIP: no steps module for $stem"
        continue
    fi

    echo "=== $stem ==="

    # 1. Parse
    parsed="$PARSED_DIR/${stem}_parsed.json"
    gherkin-parser "$feature_file" "$parsed"

    # 2. Generate
    uv run python "$REPO_ROOT/acceptance/generate_acceptance.py" "$parsed" "$steps_mod" "$GENERATED_DIR"

    # 3. Run
    generated="$GENERATED_DIR/${stem}_acceptance.py"
    if uv run python "$generated"; then
        PASSED=$((PASSED + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "=== Acceptance summary: $PASSED feature(s) passed, $FAILED failed ==="
exit $((FAILED > 0 ? 1 : 0))
