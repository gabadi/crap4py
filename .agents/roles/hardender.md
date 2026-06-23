# Role: hardender

## Known branch-miss artifacts

`_discovery_io.py` lines 86 (`rel == p` in `_match_path_pattern`) and 92 (for-loop body in `_match_name_pattern`) show as partial branch misses even after exhaustive test coverage. Do NOT add tests to fix these — they are coverage tool artifacts: `fnmatch.fnmatch(rel, pat)` already covers exact-string matches so `rel == p` is unreachable, and the `any()` short-circuit creates a phantom branch miss at line 92. (cleaner dede7aa0)

## macOS equivalent mutants — permanent, do not re-investigate

10+ mutmut survivors in `_discovery_io.py` are permanently equivalent on macOS: case-insensitive FS makes backslash-replace and case-fold mutants undetectable; UTF-8 default locale makes encoding-arg mutants equivalent; `None` in `os.path.relpath` is macOS-safe. Do NOT add platform-faking tests — note as equivalent with reason. (hardender d8370093)

## mutmut state invalidated after source merge — always re-run coverage first

After `merge_and_process.sh` or any source merge, all mutants show `not checked` because source changed. Always re-run `pytest --cov=crap4py --cov-branch --cov-report=lcov:coverage.lcov` then `uv run mutmut run` before reading results. (hardender d8370093)

## mutmut-stats.json structure

`mutants/mutmut-stats.json` key `tests_by_mangled_function_name` maps mangled function names → tests mutmut will run against each mutant. Useful for diagnosing why a covered mutant still survives. (hardender d8370093)

## mutmut worker-limit flag is `--max-children`, not `--max-workers`

The role prompt's "worker limits" guidance maps to mutmut's `--max-children N`. mutmut has no `--max-workers` flag — passing it errors. Verified against `mutmut run --help`. (hardender 773c8e94)
