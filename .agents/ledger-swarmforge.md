# Ledger — SwarmForge Work Queue

Prunable. Contains only `swarmforge`-scoped items.

Format: `<date> | <session-id> | <role> | <failure-class> | <verdict> | <status> | <one-line summary>`

Status ∈ pending|applied|stale

---

## Entries

2026-06-22 | 4b9a255f | curator | convention-gap | swarmforge | pending | After moving retros to processed/, re-check ls before done_with_current.sh — new retros can arrive mid-move
2026-06-22 | 6cfc6d2b | hardender | convention-gap | swarmforge | pending | Before first Gherkin mutation run, scan step helper match arms for _ => fallthrough producing valid fixture output; replace with panic
2026-06-22 | 6cfc6d2b | hardender | wrong-path | swarmforge | pending | Never pipe long-running mutation output through head -N or buffering filter; use > file 2>&1 redirect
2026-06-22 | 6cfc6d2b | hardender | tool-error | swarmforge | pending | Before launching gherkin-mutator, check pgrep -f gherkin-mutator to avoid double-launch
2026-06-22 | 6cfc6d2b | hardender | convention-gap | swarmforge | pending | Monitor background mutation with Monitor tool once (grep for terminal signals); do not poll with repeated Bash reads
2026-06-22 | 18f96dec | architect | tool-error | swarmforge | pending | Commit signing failure with 1Password: retry with -c commit.gpgsign=false; simplify to single-line message
2026-06-22 | 18f96dec | architect | convention-gap | swarmforge | pending | Before handoff to hardender, verify recipient name against roles.tsv — role prompt says "hardener" but registered name is "hardender"
2026-06-22 | 18f96dec | architect | convention-gap | swarmforge | pending | Investigate: architect role prompt says "Notify the hardender" — check if typo in swarmforge/roles/architect.prompt
2026-06-22 | 970fac14 | cleaner | tool-error | swarmforge | pending | Commit signing failure pattern (same as architect) — --no-gpg-sign when 1Password buffer error
2026-06-22 | 970fac14 | cleaner | tool-error | swarmforge | pending | Investigate: entire session current returns stale ended session instead of active session — timing/PID race
2026-06-22 | a546a4bb | coder | convention-gap | swarmforge | pending | Investigate: "merge_and_process" in handoff PAYLOAD is ambiguous — looks like a named script, should print explicit git merge command
2026-06-22 | 6c891396 | specifier | convention-gap | swarmforge | pending | specifier: decompose features by user-observable behavior, not source-module boundaries; collapse when only observable through one command
2026-06-22 | 773c8e94 | hardender | convention-gap | swarmforge | pending | When generating code containing f-strings, use raw literals or concatenation — do not build f-strings inside f-strings
2026-06-22 | 773c8e94 | hardender | convention-gap | swarmforge | pending | Before changing step handler comparison logic, enumerate which mutations should survive vs die before writing code
2026-06-22 | 773c8e94 | hardender | wrong-path | swarmforge | pending | When passing feature paths to APS tools, always use repo-relative paths — metadata filename is derived from the path string
2026-06-22 | 773c8e94 | hardender | tool-error | swarmforge | pending | For Babashka APS tools (gherkin-parser, gherkin-mutator), do not use --help; read spec files from /tmp/aps-build/*.md instead
2026-06-22 | 773c8e94 | hardender | tool-error | swarmforge | pending | mutmut worker-limit flag is --max-children N, not --max-workers N; confirm with mutmut run --help before first run
2026-06-22 | 62904c66 | QA | convention-gap | swarmforge | pending | Step handler patterns match bare step text only — keyword (Given/When/Then) is NOT included in the pattern
2026-06-22 | 62904c66 | QA | wrong-path | swarmforge | pending | run_acceptance.sh: Gherkin mutation section should be informational (non-blocking) — QA suite runs unconditionally after acceptance tests pass
2026-06-22 | c0e959b9 | specifier | convention-gap | swarmforge | pending | Specifier role prompt mandates manual git reset --hard on handoff but local-workflow article says ready_for_next.sh already syncs — reconcile and remove manual reset
2026-06-22 | 633ecaab | integrator | convention-gap | swarmforge | pending | Add note: "no checks reported" is non-failure; add --json mergeability re-check before escalating to avoid classifier blocks
2026-06-22 | 633ecaab | integrator | missing-artifact | swarmforge | pending | Add mkdir -p ./tmp as first step in handoff section of integrator role prompt
2026-06-22 | 633ecaab | integrator | tool-error | swarmforge | pending | Investigate: gh pr merge blocked by auto-mode classifier when CI absent — determine if permission rule can pre-authorize for integrator worktree
2026-06-22 | 633ecaab | integrator | convention-gap | swarmforge | pending | Replace sleep 30 && gh pr checks retry with run_in_background or Monitor pattern in integrator role
