# Ledger — Project Knowledge

Permanent, append-only. Contains only `rejected` and `promoted` items (never ephemerals).

Format: `<date> | <session-id> | <role> | <failure-class> | <verdict> | <one-line summary>`

---

## 2026-06-22 — knowledge/c1-complexity-spec run

2026-06-22 | 4b9a255f | curator | tool-error | rejected→first-occurrence | agent-retro: conversation_arc content fields empty in extract.py (skill action #2)
2026-06-22 | 4b9a255f | curator | tool-error | rejected→first-occurrence | agent-retro: session turn_count and estimated_cost_usd null in extract output (skill action #3)
2026-06-22 | 6cfc6d2b | hardender | convention-gap | rejected→machine-specific | cost-driver note: redirect mutation output to files, summarize before advisor (memory-update, not promotable)
2026-06-22 | a546a4bb | coder | convention-gap | promoted→AGENTS.md | In shell scripts, use `uv run python` not bare `python`; no venv is activated on PATH in this project
2026-06-22 | 970fac14 | cleaner | tool-error | rejected→machine-specific | git commit --no-gpg-sign required in this worktree (machine env fact, not promotable)
2026-06-22 | a546a4bb | coder | convention-gap | rejected→first-occurrence | acceptance generator f-string escaping guidance (skill action #4)
2026-06-22 | a546a4bb | coder | convention-gap | rejected→first-occurrence | coder startup: sketch module boundary before writing first file (skill action #6)
2026-06-22 | 6c891396 | specifier | tool-error | rejected→first-occurrence | agent-retro: entire session current worktree mismatch — verify branch before trusting (skill action #1)
2026-06-22 | 6c891396 | specifier | tool-error | rejected→first-occurrence | agent-retro: Claude Code project-dir path uses double-dash for /. boundary (skill action #2)
2026-06-22 | 62904c66 | QA | convention-gap | rejected→inferable | generator fix for non-outline Scenarios (fix is in code; acknowledgement only)
2026-06-22 | 62904c66 | QA | missing-artifact | rejected→machine-specific | 6 Gherkin mutation survivors are known spec-coverage gaps — specifier to address in C2+ (memory-update, not project knowledge)
2026-06-22 | c0e959b9 | specifier | convention-gap | rejected→swarmforge-only | completion-handoff retro: all actions swarmforge-scoped; no project promotions
2026-06-22 | 633ecaab | integrator | tool-error | rejected→swarmforge-only | integrator merge retro: all actions swarmforge-scoped; no project promotions

## 2026-06-22 — knowledge/c2-discovery run

2026-06-22 | 53a47bde | architect | convention-gap | rejected→swarmforge-only | handoff draft reminder (short hash, role name check) — swarmforge-scoped
2026-06-22 | 53a47bde | architect | convention-gap | rejected→swarmforge-only | long pre-action deliberation forcing function — swarmforge investigation
2026-06-22 | dede7aa0 | cleaner | convention-gap | rejected→first-occurrence | gitignored fixture must exist on disk for qa-discovery-6 (acceptance/fixtures/c2_fixture/build/generated.py)
2026-06-22 | dede7aa0 | cleaner | convention-gap | rejected→swarmforge-only | CRAP estimation bootstrap pattern — swarmforge/local-engineering update
2026-06-22 | dede7aa0 | cleaner | tool-error | rejected→phenomenon | lines 86/92 partial branch misses in _discovery_io.py — promoted to hardender role file
2026-06-22 | d161025e | coder | convention-gap | rejected→first-occurrence | replace_all unsafe when search string is substring of new name — use targeted Edit (skill action #1)
2026-06-22 | d161025e | coder | convention-gap | rejected→first-occurrence | drywall step duplication: prefer named class in step_lib.py over module-level mutable state (skill action #4)
2026-06-22 | d737e296 | hardender | convention-gap | rejected→swarmforge-only | check roles.tsv before handoff draft — swarmforge rule
2026-06-22 | d737e296 | hardender | tool-error | rejected→swarmforge-only | mutmut timeout investigation (or→and guard) — swarmforge item
2026-06-22 | (not-captured) | specifier | convention-gap | rejected→swarmforge-only | approval gate must be AskUserQuestion not passive trailing prose — swarmforge rule
2026-06-22 | (not-captured) | specifier | tool-error | rejected→swarmforge-only | entire session current worktree mismatch in specifier — swarmforge investigation
2026-06-22 | ce7a20cc | ux-engineer | missing-artifact | promoted→AGENTS.md | acceptance/fixtures/c2_fixture/build/generated.py must exist on disk (gitignored); absence fails qa-discovery-6
2026-06-22 | ce7a20cc | ux-engineer | tool-error | promoted→.agents/skills/agent-retro-worktree-fallback | entire session current worktree mismatch (2nd occurrence): skip session info, use JSONL fallback
2026-06-22 | ce7a20cc | ux-engineer | tool-error | promoted→.agents/skills/agent-retro-arc-fallback | conversation arc content null (2nd occurrence): fallback to in-context reconstruction
2026-06-22 | ce7a20cc | ux-engineer | tool-error | rejected→machine-specific | rtk find produces garbled output with extra spaces — machine-local RTK behavior
2026-06-22 | ce7a20cc | ux-engineer | convention-gap | rejected→swarmforge-only | git rev-parse --short=10 HEAD for handoff draft — swarmforge rule (recurring)
2026-06-22 | 4ae7dcbc | curator | tool-error | rejected→first-occurrence | entire session info returns Session not found for active sessions — JSONL fallback is primary
2026-06-22 | 4ae7dcbc | curator | tool-error | promoted→.agents/skills/agent-retro-worktree-fallback | agent-retro: after stale entire result, skip session info, go directly to JSONL (curator evidence)
2026-06-22 | 2833ecee | QA | convention-gap | rejected→swarmforge-only | git rev-parse --short=10 HEAD for handoff draft — swarmforge rule (recurring)
2026-06-22 | 2833ecee | QA | convention-gap | rejected→inferable | NOT AUTOMATED CLI absent guard in QA steps is correct — inferable from code
2026-06-22 | 2833ecee | QA | convention-gap | rejected→swarmforge-only | rtk python -m crap4py fails — CRAP invocation is uv run python -m crap4py (swarmforge/local-engineering)
2026-06-22 | f3652fc0 | specifier | tool-error | rejected→swarmforge-only | completion-notice retro: entire session current stale (existing backlog); dot-encoding fix applied to agent-retro-worktree-fallback skill
2026-06-22 | 07f1de1c | integrator | convention-gap | rejected→swarmforge-only | integrator merge retro: all actions swarmforge-scoped; no project promotions
