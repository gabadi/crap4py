# Ledger — Project Knowledge

Permanent, append-only. Contains only `promoted` and `rejected→first-occurrence` items.

Format: `<date> | <session-id> | <role> | <failure-class> | <verdict> | <one-line summary>`

---

## 2026-06-22 — knowledge/c1-complexity-spec run

2026-06-22 | 4b9a255f | curator | tool-error | rejected→first-occurrence | agent-retro: conversation_arc content fields empty in extract.py (skill action #2)
2026-06-22 | 4b9a255f | curator | tool-error | rejected→first-occurrence | agent-retro: session turn_count and estimated_cost_usd null in extract output (skill action #3)
2026-06-22 | a546a4bb | coder | convention-gap | promoted→AGENTS.md | In shell scripts, use `uv run python` not bare `python`; no venv is activated on PATH in this project
2026-06-22 | a546a4bb | coder | convention-gap | rejected→first-occurrence | acceptance generator f-string escaping guidance (skill action #4)
2026-06-22 | a546a4bb | coder | convention-gap | rejected→first-occurrence | coder startup: sketch module boundary before writing first file (skill action #6)
2026-06-22 | 6c891396 | specifier | tool-error | rejected→first-occurrence | agent-retro: entire session current worktree mismatch — verify branch before trusting (skill action #1)
2026-06-22 | 6c891396 | specifier | tool-error | rejected→first-occurrence | agent-retro: Claude Code project-dir path uses double-dash for /. boundary (skill action #2)

## 2026-06-22 — knowledge/c2-discovery run

2026-06-22 | dede7aa0 | cleaner | convention-gap | rejected→first-occurrence | gitignored fixture must exist on disk for qa-discovery-6 (acceptance/fixtures/c2_fixture/build/generated.py)
2026-06-22 | d161025e | coder | convention-gap | rejected→first-occurrence | replace_all unsafe when search string is substring of new name — use targeted Edit (skill action #1)
2026-06-22 | d161025e | coder | convention-gap | rejected→first-occurrence | drywall step duplication: prefer named class in step_lib.py over module-level mutable state (skill action #4)
2026-06-22 | ce7a20cc | ux-engineer | missing-artifact | promoted→AGENTS.md | acceptance/fixtures/c2_fixture/build/generated.py must exist on disk (gitignored); absence fails qa-discovery-6
2026-06-22 | ce7a20cc | ux-engineer | tool-error | promoted→.agents/skills/agent-retro-worktree-fallback | entire session current worktree mismatch (2nd occurrence): skip session info, use JSONL fallback
2026-06-22 | ce7a20cc | ux-engineer | tool-error | promoted→.agents/skills/agent-retro-arc-fallback | conversation arc content null (2nd occurrence): fallback to in-context reconstruction
2026-06-22 | 4ae7dcbc | curator | tool-error | rejected→first-occurrence | entire session info returns Session not found for active sessions — JSONL fallback is primary
2026-06-22 | 4ae7dcbc | curator | tool-error | promoted→.agents/skills/agent-retro-worktree-fallback | agent-retro: after stale entire result, skip session info, go directly to JSONL (curator evidence)

## 2026-06-22 — knowledge/c3-coverage-spec run

2026-06-22 | 3a08e3a5 | specifier | tool-error | rejected→first-occurrence | agent-retro SKILL.md Step 1 fallback: lead with ls ~/.claude/projects/ | grep <last-segment> (update to main skill, not fallback patch)
2026-06-22 | e8692053 | cleaner | convention-gap | promoted→.agents/roles/cleaner.md | BoolOp/IfExp each add branch points in Python CC — verify with crap4py before committing
2026-06-22 | e8692053 | cleaner | tool-error | rejected→first-occurrence | real filesystem (tmp_path) required when testable module wraps a filesystem walker — skill update candidate
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→AGENTS.md | acceptance step handlers must use m.group(N) not params.get(key) or m.group(N) — params dict silently overrides step-text literals
2026-06-22 | 45b70da6 | curator | tool-error | promoted→.agents/roles/curator.md | session-to-skill is interactive; write SKILL.md directly from ledger evidence in autonomous curator runs

## 2026-06-22 — knowledge/c4-crap-report-command run

2026-06-22 | 68d171c9 | coder | convention-gap | promoted→.agents/roles/coder.md | QA step column-by-position extraction silently returns wrong column when report format changes; always name column in comment
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→.agents/roles/coder.md | CRAP back-solve with cc=1 fails for CRAP>2 (cov<0); use concrete cc/cov pairs per target CRAP
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→.agents/roles/coder.md | ctx.cli_argv must be fully populated by Given steps before when_command_runs fires
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→AGENTS.md | gherkin-parser does not include inline data tables in step IR; hardcode in step handler
2026-06-22 | e6bab3b8 | QA | convention-gap | rejected→first-occurrence | exit code masking: never pipe CLI invocation through grep when testing exit codes — skill candidate
2026-06-22 | d8370093 | hardender | convention-gap | promoted→.agents/roles/hardender.md | macOS mutmut survivors in _discovery_io.py are permanently equivalent; do not add platform-faking tests
2026-06-22 | d8370093 | hardender | tool-error | promoted→.agents/roles/hardender.md | mutmut state invalidates after source merge; always re-run coverage then mutmut run before reading results
2026-06-22 | d8370093 | hardender | convention-gap | promoted→.agents/roles/hardender.md | mutmut-stats.json key tests_by_mangled_function_name maps function→tests; use to diagnose covered-but-surviving mutants
2026-06-22 | c531c23f | architect | tool-error | promoted→.agents/roles/architect.md | mutmut cache does not re-test mutants when new tests added; use mutmut run <name> or full re-run to recheck
