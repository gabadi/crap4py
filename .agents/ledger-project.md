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

## 2026-06-22 — knowledge/c3-coverage-spec run

2026-06-22 | 3a08e3a5 | specifier | tool-error | rejected→first-occurrence | agent-retro SKILL.md Step 1 fallback: lead with ls ~/.claude/projects/ | grep <last-segment> (update to main skill, not fallback patch)
2026-06-22 | 3a08e3a5 | specifier | tool-error | rejected→swarmforge-only | git reset --hard startup blocked by classifier (2nd occurrence of swarmforge backlog item — no project promotion)
2026-06-22 | e8692053 | cleaner | convention-gap | promoted→.agents/roles/cleaner.md | BoolOp/IfExp each add branch points in Python CC — verify with crap4py before committing
2026-06-22 | e8692053 | cleaner | tool-error | rejected→swarmforge-only | mutmut scan/count mode does not exist — swarmforge local-engineering update
2026-06-22 | e8692053 | cleaner | convention-gap | rejected→first-occurrence | real filesystem (tmp_path) required when testable module wraps a filesystem walker — skill update candidate
2026-06-22 | 38db4a34 | hardender | convention-gap | rejected→inferable | canonical SwarmForge role names inferable from .swarmforge/roles.tsv — no promotion needed
2026-06-22 | 38db4a34 | hardender | tool-error | rejected→swarmforge-only | mutmut targeted re-run shows 0 files mutated — investigate swarmforge item
2026-06-22 | 927abd29 | architect | convention-gap | rejected→swarmforge-only | analyze mutant survivors as batch before targeted reruns — swarmforge/local-engineering update
2026-06-22 | 927abd29 | architect | convention-gap | rejected→inferable | architectural boundary enforcement (IO/_report/AST) inferable from test_arch.py — no promotion needed
2026-06-22 | 927abd29 | architect | tool-error | rejected→swarmforge-only | features/*.feature manifest header updated each run (spurious unstaged) — swarmforge investigation
2026-06-22 | e41b3e44 | QA | convention-gap | rejected→swarmforge-only | git rev-parse --short=10 HEAD for handoff draft — swarmforge rule (existing pattern)
2026-06-22 | e41b3e44 | QA | convention-gap | rejected→inferable | pre-existing Gherkin complexity survivors (C1) inferable from git history and C1 feature file
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→AGENTS.md | acceptance step handlers must use m.group(N) not params.get(key) or m.group(N) — params dict silently overrides step-text literals
2026-06-22 | 68d171c9 | coder | convention-gap | rejected→inferable | normalising parser test design (before vs after normalisation differ at data level) — general test design, inferable
2026-06-22 | 68d171c9 | coder | convention-gap | rejected→swarmforge-only | params.get(x) or m.group(1) audit in existing step handlers — project-level cleanup task
2026-06-22 | 45b70da6 | curator | tool-error | promoted→.agents/roles/curator.md | session-to-skill is interactive; write SKILL.md directly from ledger evidence in autonomous curator runs
2026-06-22 | 45b70da6 | curator | tool-error | rejected→swarmforge-only | extract.py conversation_arc null / token_budget empty (4th curator occurrence) — ongoing investigation
2026-06-22 | 6d7df830 | integrator | convention-gap | rejected→swarmforge-only | integrator merge retro: all actions swarmforge-scoped; no project promotions

## 2026-06-22 — knowledge/c4-crap-report-command run

2026-06-22 | bd628b3f | cleaner | convention-gap | rejected→swarmforge-only | mutmut scan/count mode unavailable — swarmforge local-engineering item
2026-06-22 | bd628b3f | cleaner | tool-error | rejected→swarmforge-only | mutmut stale after refactor — swarmforge investigation item
2026-06-22 | bd628b3f | cleaner | convention-gap | rejected→swarmforge-only | commit hash 10-char reminder — swarmforge rule (recurring)
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→.agents/roles/coder.md | QA step column-by-position extraction silently returns wrong column when report format changes; always name column in comment
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→.agents/roles/coder.md | CRAP back-solve with cc=1 fails for CRAP>2 (cov<0); use concrete cc/cov pairs per target CRAP
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→.agents/roles/coder.md | ctx.cli_argv must be fully populated by Given steps before when_command_runs fires
2026-06-22 | 68d171c9 | coder | convention-gap | promoted→AGENTS.md | gherkin-parser does not include inline data tables in step IR; hardcode in step handler
2026-06-22 | 68d171c9 | coder | convention-gap | rejected→swarmforge-only | positional column extraction comment rule — swarmforge/coder role prompt
2026-06-22 | e6bab3b8 | QA | convention-gap | rejected→swarmforge-only | QA pre-verification: detect un-merged pipeline branches before verifying — swarmforge QA role item
2026-06-22 | e6bab3b8 | QA | convention-gap | rejected→first-occurrence | exit code masking: never pipe CLI invocation through grep when testing exit codes — skill candidate
2026-06-22 | d8370093 | hardender | convention-gap | promoted→.agents/roles/hardender.md | macOS mutmut survivors in _discovery_io.py are permanently equivalent; do not add platform-faking tests
2026-06-22 | d8370093 | hardender | tool-error | promoted→.agents/roles/hardender.md | mutmut state invalidates after source merge; always re-run coverage then mutmut run before reading results
2026-06-22 | d8370093 | hardender | convention-gap | promoted→.agents/roles/hardender.md | mutmut-stats.json key tests_by_mangled_function_name maps function→tests; use to diagnose covered-but-surviving mutants
2026-06-22 | d8370093 | hardender | convention-gap | rejected→swarmforge-only | post-merge re-run reminder — swarmforge hardender role prompt item
2026-06-22 | f2c50b01 | specifier | tool-error | rejected→swarmforge-only | git reset --hard startup blocked by classifier (3rd occurrence) — swarmforge backlog item escalation
2026-06-22 | aee3d2af | curator | tool-error | rejected→swarmforge-only | extract.py null token_budget (5th occurrence) — ongoing swarmforge investigation
2026-06-22 | c531c23f | architect | tool-error | promoted→.agents/roles/architect.md | mutmut cache does not re-test mutants when new tests added; use mutmut run <name> or full re-run to recheck
2026-06-22 | c531c23f | architect | convention-gap | rejected→swarmforge-only | commit hash 10-char reminder for architect — swarmforge rule (recurring)
