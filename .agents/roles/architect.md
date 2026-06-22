# Role: architect

## mutmut cache freshness — adding tests does NOT re-run existing mutants

When mutmut shows surviving mutants after writing new kill-tests, do NOT assume the tests were ineffective. mutmut only re-tests mutants in *changed functions* — adding tests to a test file does NOT trigger re-testing of mutants in unchanged source functions. Use `uv run mutmut run <mutant-name>` to force a specific recheck, or re-run full coverage + `uv run mutmut run` to refresh all. (architect c531c23f)
