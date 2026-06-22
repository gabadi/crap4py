## Agent skills

### Issue tracker

Issues live in GitHub Issues for `gabadi/crap4py` (uses `gh` CLI); external PRs are not a triage surface. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary — `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo — `CONTEXT.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.

### Python invocation

In all shell scripts in this project, use `uv run python` not bare `python`; no venv is activated on PATH (coder A1, session a546a4bb).
