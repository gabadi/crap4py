# Role: curator

## session-to-skill Is Interactive — Write Skills Directly in Autonomous Runs

`session-to-skill` dispatches confirmation prompts and stalls when run unattended. For second-occurrence skill promotions in autonomous curator runs: write `.agents/skills/<name>/SKILL.md` directly from ledger evidence + recalled session facts. Do NOT invoke `session-to-skill` expecting unattended execution. (curator 45b70da6)

## skill-update: Edit Existing Skills, Don't Create Sibling Patches

When ledger evidence targets an existing named skill (e.g. `agent-retro`), open that skill's `SKILL.md` and patch the relevant steps in-place. Do NOT create a new sibling skill directory (e.g. `agent-retro-worktree-fallback`). Sibling patches are invisible to agents using the main skill and accumulate as dead files.

Process: read the existing `SKILL.md` → identify the step(s) to change → edit in-place with before/after diff in the ledger entry → record as `skill-update` action in the retro table.
