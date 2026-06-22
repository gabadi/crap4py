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

### Hardender role knowledge

See `.agents/roles/hardender.md` for known branch-miss artifacts in `_discovery_io.py`.
