# mutation-stamp: sha256=f3770e3240e4746dc1f00fe441c4e90b7588900ec27bbd22d92578a11419ad9b
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-06-22T19:01:39.297536Z","feature_name":"CRAP report command","feature_path":"/Users/gabadi/workspace/addi/crap4py/.worktrees/QA/features/report.feature","background_hash":"74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b","implementation_hash":"unknown","scenarios":[{"index":0,"name":"The CRAP score combines complexity and coverage","scenario_hash":"39636970ae71027ee609d585558513c8d87a97ad28fc6a08a05836f4dbdeef39","mutation_count":9,"result":{"Total":9,"Killed":9,"Survived":0,"Errors":0},"tested_at":"2026-06-22T18:58:26.271121Z"},{"index":6,"name":"A path-fragment filter narrows the analysed source set","scenario_hash":"150a4dba39c40fe2aceaaef94aae0b964f6b65c252186310161393629c3bb3fd","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-06-22T18:58:26.271121Z"},{"index":7,"name":"Help and invalid arguments behave predictably","scenario_hash":"2f6d8066270a49218c540294bd45c0d4e44bf10796252440e19d340596c8b371","mutation_count":6,"result":{"Total":6,"Killed":6,"Survived":0,"Errors":0},"tested_at":"2026-06-22T18:58:26.271121Z"},{"index":8,"name":"--max-crap gates the exit code on the worst CRAP score","scenario_hash":"0efb7cebd7e62ed46117c1c465c719da1b8c2b4ab114745c9d9554444e182b1c","mutation_count":6,"result":{"Total":6,"Killed":6,"Survived":0,"Errors":0},"tested_at":"2026-06-22T18:58:26.271121Z"},{"index":10,"name":"--max-workers does not change the report","scenario_hash":"051102aa31898718f8bc5e033e5f012fd40b5046d0636dbcbee616d03076f6fa","mutation_count":1,"result":{"Total":1,"Killed":1,"Survived":0,"Errors":0},"tested_at":"2026-06-22T18:58:26.271121Z"},{"index":11,"name":"--max-workers requires a positive integer","scenario_hash":"aedb41f40a51d578f450c1d6a206ad9f436613a560559ccda219f13f13ff42d0","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-06-22T18:58:26.271121Z"}]}
# acceptance-mutation-manifest-end

Feature: CRAP report command

  # TRACKING: #10
  #
  # CONTRACT:
  #   The integration surface: the single command
  #   `uv run crap4py --lcov <lcov> [path-fragment ...] <paths>` that combines
  #   complexity (C1), discovery/naming + module label (C2), and coverage (C3)
  #   into a CRAP score per function, sorts them, and prints the report.
  #   Inputs:
  #     --lcov PATH        — required path to a pre-generated LCOV file.
  #     <paths>            — one or more source paths to analyse.
  #     path-fragment ...  — optional positional substring filters; only source
  #                          files whose path contains a fragment are analysed.
  #     --max-crap N       — optional CI gate (see CONSTRAINTS / exit codes).
  #     --max-workers N    — optional parallelism (performance only).
  #     -h / --help        — print usage and exit 0.
  #   Output: a fixed-width table on stdout — a `CRAP Report` title, a `=`
  #     underline, a `Function | Module | CC | Cov% | CRAP` header, a `-`
  #     separator, then one row per function. Empty input still prints the
  #     header block.
  #   CRAP and report rules are fixed by ADR 0004.
  #
  # CONSTRAINTS:
  #   - CRAP score = CC² × (1 − coverage)³ + CC, where coverage is the C3
  #     fraction in [0, 1]. When coverage is N/A (indeterminate, ADR 0002) the
  #     CRAP score is N/A; indeterminacy propagates and is never coerced to 0.
  #   - Rows sort worst-CRAP-first (descending); N/A-CRAP rows sort last; ties
  #     (equal CRAP, or two N/A rows) break stably by qualified name ascending.
  #   - --lcov is REQUIRED; omitting it is a usage error (clear stderr message +
  #     non-zero exit), not an all-N/A run — crap4py cannot generate coverage.
  #   - --max-crap N: when supplied, exit non-zero iff some function's CRAP is
  #     strictly greater than N; N/A-CRAP rows never trip it. No default gate.
  #   - --max-workers N: performance only — output is identical to a serial run.
  #     Requires a positive integer.
  #   - Exit codes: 0 on a clean run (and no --max-crap breach); non-zero on a
  #     usage/IO error (bad args, omitted/missing/unreadable --lcov); non-zero on
  #     a --max-crap breach.
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Deterministic: the same paths, LCOV, and flags always produce the same
  #     report text and the same exit code.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT compute CC (C1, #7), discover functions / qualified names /
  #     module labels (C2, #8), or resolve coverage (C3, #9); those are consumed
  #     here as produced upstream.
  #   - Does NOT run tests or invoke coverage.py; the LCOV is pre-supplied.
  #   - Does NOT emit risk-band labels, colours, or any fixed-threshold
  #     annotation in normal output (the only threshold is the opt-in --max-crap).
  #   - Does NOT parse non-LCOV formats or infer dotted-import module names.
  #   - ASSUMED: --max-workers output-invariance is the only behaviour parallelism
  #     adds; it never changes rows, order, or values versus serial.
  #
  # UX INTENT: none
  # Design artifacts: none

  # report-1
  Scenario Outline: The CRAP score combines complexity and coverage
    Given a function with cyclomatic complexity <cc> and coverage "<coverage>"
    When the CRAP score is computed
    Then the function's CRAP score is "<crap>"

    Examples:
      | cc | coverage | crap |
      | 4  | 0.75     | 4.2  |
      | 5  | 0.0      | 30.0 |
      | 1  | 1.0      | 1.0  |

  # report-2
  Scenario: An N/A coverage propagates to an N/A CRAP score
    Given a function whose coverage is "N/A"
    When the CRAP score is computed
    Then the function's CRAP score is "N/A"

  # report-3
  Scenario: Functions sort worst CRAP first with N/A last and a stable name tiebreak
    Given functions with CRAP scores and qualified names:
      | name    | crap |
      | alpha   | 4.2  |
      | bravo   | N/A  |
      | charlie | 30.0 |
      | delta   | 4.2  |
      | echo    | N/A  |
    When the functions are sorted for the report
    Then the report rows appear in the order "charlie, alpha, delta, bravo, echo"

  # report-4
  Scenario: The report prints a titled fixed-width table with the five columns
    Given a discovered function reported as one row
    When the report is formatted
    Then the output's first line is "CRAP Report"
    And the output has a column header naming "Function", "Module", "CC", "Cov%", and "CRAP"
    And a separator line follows the column header

  # report-5
  Scenario: Empty input still prints the report header block
    Given no functions are discovered under the given paths
    When the report is formatted
    Then the output's first line is "CRAP Report"
    And the output has no function rows

  # report-6
  Scenario: Omitting --lcov is a usage error
    Given the command is invoked with source paths but no "--lcov" argument
    When the command runs
    Then the command exits with a non-zero status
    And it prints an error message about the missing "--lcov" argument

  # report-7
  Scenario Outline: A path-fragment filter narrows the analysed source set
    Given discovered source files "<files>"
    And the command is given the path-fragment filter "<fragment>"
    When the command runs
    Then only the source files matching "<fragment>" are analysed

    Examples:
      | files                                       | fragment   |
      | src/crap4py/complexity.py,src/crap4py/cli.py | complexity |

  # report-8
  Scenario Outline: Help and invalid arguments behave predictably
    Given the command is invoked with the argument "<argument>"
    When the command runs
    Then the command exits with status "<exit>"
    And it writes "<stream>"

    Examples:
      | argument | exit     | stream         |
      | --help   | zero     | usage to stdout |
      | --bogus  | non-zero | error to stderr |

  # report-9
  Scenario Outline: --max-crap gates the exit code on the worst CRAP score
    Given a report whose highest CRAP score is <worst>
    When the command runs with "--max-crap <threshold>"
    Then the command exits with status "<exit>"

    Examples:
      | worst | threshold | exit     |
      | 30.0  | 29        | non-zero |
      | 30.0  | 30        | zero     |

  # report-10
  Scenario: An N/A CRAP score never trips the --max-crap gate
    Given a report whose only non-N/A CRAP score is 5.0 and which also has N/A rows
    When the command runs with "--max-crap 10"
    Then the command exits with status "zero"

  # report-11
  Scenario Outline: --max-workers does not change the report
    Given a fixture analysed serially produces a known report
    When the command runs the same fixture with "--max-workers <workers>"
    Then the report text is identical to the serial report

    Examples:
      | workers |
      | 4       |

  # report-12
  Scenario Outline: --max-workers requires a positive integer
    Given the command is invoked with "--max-workers <value>"
    When the command runs
    Then the command exits with a non-zero status
    And it prints an error message about "--max-workers"

    Examples:
      | value |
      | 0     |
      | abc   |
