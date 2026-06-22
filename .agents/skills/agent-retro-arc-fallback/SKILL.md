---
name: agent-retro-arc-fallback
description: Patch for agent-retro Step 2 — use when extract.py returns conversation_arc with all content fields null/empty. Fall back to in-context reconstruction for the retro body. Second-occurrence promotion from curator 4b9a255f + ux-engineer ce7a20cc.
---

# agent-retro — Conversation Arc Fallback Patch

## Problem

`extract.py --summary` populates `conversation_arc` with entries where every `content` field is `null` or empty string. This means the arc cannot be used to identify user corrections, redirects, or friction moments.

Separately, `token_budget` may also be empty (all null fields).

**Confirmed in**: curator (4b9a255f), ux-engineer (ce7a20cc) — two pipeline roles across two pipeline runs.

## Detection

After running `extract.py --summary > /tmp/retro-extract.json`, check:

```bash
python3 -c "
import json
d = json.load(open('/tmp/retro-extract.json'))
arc = d.get('conversation_arc', [])
non_null = sum(1 for e in arc if e.get('content'))
print(f'arc entries: {len(arc)}, non-null content: {non_null}')
"
```

If `non_null == 0` and `len(arc) > 0`, the extractor failed silently.

## Fallback: In-Context Reconstruction

When the arc is empty, write the retro from live session memory instead:

1. **What Worked** — recall tool calls, commands, and outputs that succeeded cleanly on the first attempt.
2. **What Didn't Work** — recall tool calls that failed, required retries, or produced unexpected output.
3. **User corrections / redirects** — recall any user pushback during the session.
4. **Token budget** — if `token_budget` fields are also null, mark as `(unavailable — extract.py returned no cost data)` and note the known issue.

Do not fabricate metrics. Mark unavailable data explicitly rather than guessing.

## Notes

- Root cause unknown as of 2026-06-22. May be a transcript format change or an extractor bug with certain JSONL structures.
- The `token_budget` null issue is tracked separately; both failures often co-occur.
- This is a known limitation; retros written from live context are still valid — they lack token/cost precision but capture all behavioral observations.
