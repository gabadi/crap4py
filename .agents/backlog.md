# Enforcement-Gate Backlog

Append-only proposals for mechanical gates, config guards, or CI checks.

Format: `<date> | <source> | <failure-class> | <roles-affected> | <status> | <description>`

---

## Entries

2026-06-22 | swarmforge-pattern | tool-error | architect,cleaner | machine-specific | 1Password GPG signing fails silently in agent worktrees — machine-local 1Password env; not promotable
2026-06-22 | swarmforge-pattern | tool-error | curator,specifier,cleaner | applied | `entire session current` returns wrong/stale session across 3 roles — fixed in agent-retro SKILL.md: worktree_path validation added to Step 1 primary path
2026-06-22 | swarmforge-pattern | convention-gap | coder,hardender | pending | f-string escaping confusion when generating code that contains f-strings — document two-level escaping rule in APS generation guidance; affects acceptance generator authoring by both roles
2026-06-22 | swarmforge-pattern | tool-error | specifier,integrator | applied | Auto-mode classifier blocks in-role autonomous actions — fixed via settings.local.json allow rules: Bash(git reset --hard origin/*) and Bash(gh pr merge*)
2026-06-22 | swarmforge-pattern | convention-gap | architect,hardender,ux-engineer,QA | applied | 7-char git log hash in handoff drafts — fixed in handoffs.prompt: explicit pre-step rule + template uses <HASH> placeholder with run instruction
2026-06-22 | swarmforge-pattern | convention-gap | cleaner,QA | applied | CRAP bootstrap invocation — fixed in local-engineering.prompt: python -m crap4py → uv run python -m crap4py
2026-06-22 | swarmforge-pattern | tool-error | cleaner,hardender,architect | applied | mutmut semantics — fixed in local-engineering.prompt and cleaner.prompt: no scan/count mode, no targeted reruns, re-run coverage after merge
