# Enforcement-Gate Backlog

Append-only proposals for mechanical gates, config guards, or CI checks.

Format: `<date> | <source> | <failure-class> | <roles-affected> | <status> | <description>`

--- 

## Entries

2026-06-22 | swarmforge-pattern | tool-error | architect,cleaner | wontfix | 1Password GPG signing fails silently in agent worktrees — add --no-gpg-sign to all commit invocations in agent role prompts or local-engineering constitution; affects at least architect and cleaner
2026-06-22 | swarmforge-pattern | tool-error | curator,specifier,cleaner | applied | `entire session current` returns wrong/stale session across 3 roles — agent-retro must verify returned worktree_path matches $PWD before trusting; add sanity-check to SKILL.md
2026-06-22 | swarmforge-pattern | convention-gap | coder,hardender | wontfix | f-string escaping confusion when generating code that contains f-strings — document two-level escaping rule in APS generation guidance; affects acceptance generator authoring by both roles
2026-06-22 | swarmforge-pattern | tool-error | specifier,integrator | applied | Auto-mode classifier blocks in-role autonomous actions (git reset --hard, gh pr merge) when no explicit per-invocation user direction — both roles blocked in same pipeline run; consider permission pre-authorization or role prompt phrasing adjustment | RESOLVED 2026-06-23: setup-swarm Step 4 already pre-authorizes `gh pr merge*`; broadened reset rule `git reset --hard origin/*`→`git reset --hard*` (canonical PR gabadi/swarm-forge#25; applied to crap4py skill copies + .claude/settings.json)
2026-06-22 | swarmforge-pattern | convention-gap | architect,hardender,ux-engineer,QA | applied | 4 roles used 7-char git log hash instead of required 10-char in handoff drafts — add `git rev-parse --short=10 HEAD` as a mandatory line in the handoff draft template or constitution handoffs article | RESOLVED 2026-06-23: handoffs.prompt git_handoff template already carried the `$(git rev-parse --short=10 HEAD)` token; added explicit mandate that `commit:` MUST be that command's literal output, never a copied 7-char git log/show hash (crap4py-local)
2026-06-22 | swarmforge-pattern | convention-gap | cleaner,QA | applied | CRAP bootstrap invocation unclear: local-engineering.prompt says `python -m crap4py` but correct form is `uv run python -m crap4py`; update CRAP section to clarify and note rtk prefix breaks the invocation | RESOLVED 2026-06-23: local-engineering.prompt CRAP line now uses `uv run python -m crap4py` and warns rtk prefix breaks `-m crap4py` (crap4py-local)
2026-06-22 | swarmforge-pattern | tool-error | cleaner,hardender,architect | pending | mutmut is a workaround tool missing capabilities the pipeline assumes — no `--scan` (count sites without running, cleaner's split gate), and a stateful incremental cache (adding tests doesn't re-test; merge invalidates all). NOT a roles-misunderstood-it problem and NOT fixed by full runs — the model is differential-against-manifest. Structural fix = build `mutate4py` (todo; has `--scan`/`--since-last-run`/`--mutate-all` per docs/tool-analysis-crap-dry-mutation.md). Interim mutmut facts captured 2026-06-23 in .agents/roles/{hardender,cleaner,architect}.md; keep differential model, do not switch to full runs
