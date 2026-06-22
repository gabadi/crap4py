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
