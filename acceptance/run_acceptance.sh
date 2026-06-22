#!/usr/bin/env bash
# Run acceptance tests for all feature files, then Gherkin soft mutation.
# Usage: ./acceptance/run_acceptance.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARSED_DIR="$REPO_ROOT/acceptance/parsed"
GENERATED_DIR="$REPO_ROOT/acceptance/generated"

mkdir -p "$PARSED_DIR" "$GENERATED_DIR"

# Feature → steps module mapping
declare -A STEPS_MAP
STEPS_MAP[complexity]="complexity_steps"
STEPS_MAP[discovery]="discovery_steps"

# QA feature → steps module mapping (run separately; no Gherkin mutation)
declare -A QA_STEPS_MAP
QA_STEPS_MAP[complexity_qa]="complexity_qa_steps"
QA_STEPS_MAP[discovery_qa]="discovery_qa_steps"

FAILED=0
PASSED=0

for feature_file in "$REPO_ROOT"/features/*.feature; do
    stem="$(basename "$feature_file" .feature)"

    # QA feature files are run in the QA section below
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

    # 2. Generate (pass relative feature path for stable metadata naming)
    rel_feature="features/${stem}.feature"
    uv run python "$REPO_ROOT/acceptance/generate_acceptance.py" \
        "$parsed" "$steps_mod" "$GENERATED_DIR" "$rel_feature"

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

if [[ $FAILED -gt 0 ]]; then
    echo "Skipping Gherkin mutation — acceptance tests failed"
    exit 1
fi

# --- Gherkin soft mutation ---
echo ""
echo "=== Gherkin soft mutation ==="

MUTATION_FAILED=0
RUNNER="uv run python $REPO_ROOT/acceptance/runner_adapter.py"

for feature_file in "$REPO_ROOT"/features/*.feature; do
    stem="$(basename "$feature_file" .feature)"

    if [[ "$stem" == *_qa ]]; then
        continue
    fi

    steps_mod="${STEPS_MAP[$stem]:-}"
    if [[ -z "$steps_mod" ]]; then
        continue
    fi

    echo "--- mutation: $stem ---"
    if gherkin-mutator \
        --feature "$feature_file" \
        --generated-dir "$GENERATED_DIR" \
        --work-dir "$REPO_ROOT/tmp/acceptance-mutation/$stem" \
        --level soft \
        --workers 4 \
        --runner-worker "$RUNNER"; then
        echo "PASS mutation: $stem"
    else
        echo "FAIL mutation: $stem"
        MUTATION_FAILED=$((MUTATION_FAILED + 1))
    fi
done

if [[ $MUTATION_FAILED -gt 0 ]]; then
    echo "=== Gherkin mutation: $MUTATION_FAILED feature(s) have surviving mutants (spec gaps — route to specifier) ==="
fi

echo "=== Gherkin mutation done ==="

# --- QA end-to-end suite ---
echo ""
echo "=== QA end-to-end suite ==="

QA_FAILED=0
QA_PASSED=0

for feature_file in "$REPO_ROOT"/features/*_qa.feature; do
    [[ -f "$feature_file" ]] || continue
    stem="$(basename "$feature_file" .feature)"
    steps_mod="${QA_STEPS_MAP[$stem]:-}"
    if [[ -z "$steps_mod" ]]; then
        echo "SKIP QA: no steps module for $stem"
        continue
    fi

    echo "=== QA: $stem ==="

    parsed="$PARSED_DIR/${stem}_parsed.json"
    gherkin-parser "$feature_file" "$parsed"

    rel_feature="features/${stem}.feature"
    uv run python "$REPO_ROOT/acceptance/generate_acceptance.py" \
        "$parsed" "$steps_mod" "$GENERATED_DIR" "$rel_feature"

    generated="$GENERATED_DIR/${stem}_acceptance.py"
    if uv run python "$generated"; then
        QA_PASSED=$((QA_PASSED + 1))
    else
        QA_FAILED=$((QA_FAILED + 1))
    fi
done

echo ""
echo "=== QA suite: $QA_PASSED feature(s) passed, $QA_FAILED failed ==="

if [[ $QA_FAILED -gt 0 ]]; then
    exit 1
fi

exit 0
