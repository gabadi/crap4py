# Enforcement-Gate Backlog

Append-only proposals for mechanical gates, config guards, or CI checks.

Format: `<date> | <source> | <failure-class> | <roles-affected> | <status> | <description>`

---

## Entries

2026-06-22 | swarmforge-pattern | tool-error | architect,cleaner | pending | 1Password GPG signing fails silently in agent worktrees — add --no-gpg-sign to all commit invocations in agent role prompts or local-engineering constitution; affects at least architect and cleaner
2026-06-22 | swarmforge-pattern | tool-error | curator,specifier,cleaner | pending | `entire session current` returns wrong/stale session across 3 roles — agent-retro must verify returned worktree_path matches $PWD before trusting; add sanity-check to SKILL.md
2026-06-22 | swarmforge-pattern | convention-gap | coder,hardender | pending | f-string escaping confusion when generating code that contains f-strings — document two-level escaping rule in APS generation guidance; affects acceptance generator authoring by both roles
2026-06-22 | swarmforge-pattern | tool-error | specifier,integrator | pending | Auto-mode classifier blocks in-role autonomous actions (git reset --hard, gh pr merge) when no explicit per-invocation user direction — both roles blocked in same pipeline run; consider permission pre-authorization or role prompt phrasing adjustment
2026-06-22 | swarmforge-pattern | convention-gap | architect,hardender,ux-engineer,QA | pending | 4 roles used 7-char git log hash instead of required 10-char in handoff drafts — add `git rev-parse --short=10 HEAD` as a mandatory line in the handoff draft template or constitution handoffs article
2026-06-22 | swarmforge-pattern | convention-gap | cleaner,QA | pending | CRAP bootstrap invocation unclear: local-engineering.prompt says `python -m crap4py` but correct form is `uv run python -m crap4py`; update CRAP section to clarify and note rtk prefix breaks the invocation
2026-06-22 | swarmforge-pattern | tool-error | cleaner,hardender,architect | pending | mutmut targeted/incremental run semantics misunderstood by 3 roles — no scan/count mode exists; targeted reruns reset cache and show 0 files mutated; always analyze ALL survivors upfront, never mix targeted+full runs
