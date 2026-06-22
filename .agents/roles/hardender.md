# Role: hardender

## Known branch-miss artifacts

`_discovery_io.py` lines 86 (`rel == p` in `_match_path_pattern`) and 92 (for-loop body in `_match_name_pattern`) show as partial branch misses even after exhaustive test coverage. Do NOT add tests to fix these — they are coverage tool artifacts: `fnmatch.fnmatch(rel, pat)` already covers exact-string matches so `rel == p` is unreachable, and the `any()` short-circuit creates a phantom branch miss at line 92. (cleaner dede7aa0)
