---
name: agent-retro-worktree-fallback
description: Patch for agent-retro Step 1 — use when `entire session current` returns a session whose worktree_path does not match $PWD (stale/wrong-repo result). Skip `entire session info` and go directly to the JSONL fallback. Second-occurrence promotion from ux-engineer ce7a20cc + specifier 6c891396.
---

# agent-retro — Worktree Fallback Patch

## Problem

`entire session current` can return a stale **ended** session from the parent repo checkout instead of the active worktree session. This happens when:
- The agent runs in a worktree path (e.g. `.worktrees/ux-engineer`) not yet indexed by `entire`
- The most-recently ended session in `entire`'s index belongs to the parent repo (`/crap4py`), not the worktree

Calling `entire session info <id>` after receiving a stale result also fails ("Session not found") because `entire`'s index lags running processes.

**Confirmed in**: specifier (6c891396), ux-engineer (ce7a20cc), curator (4ae7dcbc) — three pipeline roles across two pipeline runs.

## Patch: Replace agent-retro Step 1 Primary Path

After running `entire session current --json`:

1. Parse the returned JSON and check `worktree_path`.
2. **If `worktree_path` does NOT match `$PWD`** (or the result is empty/error) → stale result. **Skip `entire session info` entirely.** Go directly to the JSONL fallback below.
3. **If `worktree_path` matches `$PWD`** → proceed normally with `entire session info <id>`.

## JSONL Fallback Steps

When stale/wrong worktree detected:

```bash
# Encode $PWD for Claude Code project dir path
# Replace / with - (except leading /), then leading / becomes -Users-...
# Or: ls ~/.claude/projects/ | grep <last-segment-of-PWD>

ENCODED=$(echo "$PWD" | sed 's|/|-|g' | sed 's|^-||')
PROJECT_DIR="$HOME/.claude/projects/$ENCODED"

# Find most recently modified JSONL for this worktree
ls -t "$PROJECT_DIR"/*.jsonl 2>/dev/null | head -1
```

This gives you the transcript path. Pass it directly to `extract.py`:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/extract.py <transcript_path> --metadata-only
python3 ${CLAUDE_SKILL_DIR}/scripts/extract.py <transcript_path> --summary > /tmp/retro-extract.json
```

## Notes

- Do NOT call `entire session info <id>` for a stale result — it returns "Session not found" even for sessions visible in pid files.
- The Claude Code project-dir encoding replaces every `/` with `-` and drops the leading `/`. The worktree path `/Users/gabadi/workspace/addi/crap4py/.worktrees/ux-engineer` encodes to `-Users-gabadi-workspace-addi-crap4py--worktrees-ux-engineer` (double-dash at `/` boundaries of path segments that start with `.`).
- Multiple JSONL files may exist in the project dir (one per session). `ls -t` picks the most recently modified, which is the running session.
