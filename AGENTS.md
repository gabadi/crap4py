## Agent skills

### Issue tracker

Issues live in GitHub Issues for `gabadi/crap4py` (uses `gh` CLI); external PRs are not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary — `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo — `CONTEXT.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.

### Python invocation

In all shell scripts in this project, use `uv run python` not bare `python`; no venv is activated on PATH (coder A1, session a546a4bb).

### Gitignored fixture

`acceptance/fixtures/c2_fixture/build/generated.py` is intentionally gitignored (tests discovery-skips it); it MUST exist on disk or qa-discovery-6 fails. Create it locally if absent. (ux-engineer ce7a20cc)

### Acceptance step handler capture rule

In acceptance step handlers, always use `m.group(N)` (regex capture) to extract literal values from step text — never `params.get(key) or m.group(N)`. The params dict carries ALL example-row values and silently overrides step-text literals. (coder 68d171c9)

### gherkin-parser inline data tables

`gherkin-parser` does NOT include inline `| col | val |` data tables in step IR. Any step using an inline table MUST hardcode that table in the step handler. (coder 68d171c9)
