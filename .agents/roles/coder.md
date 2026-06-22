# Role: coder

## QA step column extraction — always name the column, never use positional index

When a QA step extracts a CLI report column by position (e.g. `parts[-1]`), add a comment naming which column it is. Update it whenever report column count changes. Silent wrong-column extraction (returning CRAP score instead of coverage%) caused invisible test breakage in C4. (coder 68d171c9)

## CRAP back-solve in step handlers — use concrete cc/cov pairs, check feasibility

With cc=N, minimum achievable CRAP is N (at cov=1.0). Back-solving for target CRAP values with cc=1 fails for CRAP>2 (requires negative cov). Use concrete cc/cov pairs per target CRAP value rather than algebraic back-solve. (coder 68d171c9)

## ctx.cli_argv must be set by Given steps before when_command_runs fires

The `when_command_runs` step requires `ctx.cli_argv` populated by prior Given steps. Fragment-filter and similar scenarios must set up the full argv (including temp files and flags) in their Given step handler — not just store values for later. Verify the argv chain is complete before the When step fires. (coder 68d171c9)
