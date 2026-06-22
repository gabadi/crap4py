Feature: QA — The CRAP report is observable through the crap4py CLI

  # TRACKING: #10
  #
  # CONTRACT:
  #   End-to-end QA for C4. Operates only through the user interface: the
  #   `uv run crap4py` command, its printed report, and its exit code. No project
  #   API. The QA agent reads the printed table (the CRAP column, row order, and
  #   the header block) and observes the process exit status to verify the score,
  #   sort, format, and the --max-crap / --max-workers CLI affordances.
  #
  # CONSTRAINTS:
  #   - Verification uses committed fixtures: a small Python source tree plus a
  #     matching LCOV file authored so each function has a known CC and coverage,
  #     and therefore a known CRAP score. The fixture documents, in a comment,
  #     the expected CC, coverage, and CRAP for each function row.
  #   - The QA agent asserts on the CRAP column, the relative row order, the
  #     header block, and the process exit code — through the CLI only.
  #   - Fixtures exercise the load-bearing cases through the real CLI: a function
  #     with a finite CRAP score, a function whose coverage (and so CRAP) is N/A,
  #     a worst-CRAP function that sorts first, and an N/A row that sorts last.
  #   - --max-crap is exercised with a threshold below and at the worst score to
  #     observe the breach (non-zero) and clean (zero) exit codes; the strict
  #     "greater than" boundary at the worst score is verified.
  #   - --max-workers is exercised by comparing its full report text to the
  #     serial report over the same fixture.
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Re-running the command on the same fixture tree, LCOV, and flags yields
  #     the same report text and the same exit code.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT assert CC alone (C1), discovery/naming/module beyond locating a
  #     row (C2), or the coverage column in isolation (C3) — only the C4 surface:
  #     CRAP value, order, format, and exit code.
  #   - Does NOT run coverage.py; the LCOV fixture is pre-generated and committed.
  #   - ASSUMED: `uv run crap4py --lcov <lcov> <root>` prints the `CRAP Report`
  #     table and exits 0 on a clean run; --max-crap and --max-workers are
  #     user-facing flags on that command.
  #
  # UX INTENT: none
  # Design artifacts: none

  Background:
    Given a committed Python fixture tree and a matching LCOV file
    And the command "uv run crap4py --lcov <lcov> <root>" has been run

  # qa-report-1
  Scenario Outline: The CRAP column shows the score from the function's CC and coverage
    Given the fixture's function "<function>" has cyclomatic complexity <cc> and coverage "<coverage>"
    When the report is produced
    Then the report row for "<function>" shows CRAP "<crap>"

    Examples:
      | function       | cc | coverage | crap |
      | partly_covered | 4  | 0.75     | 4.2  |
      | worst          | 5  | 0.0      | 30.0 |

  # qa-report-2
  Scenario Outline: A function with N/A coverage shows an N/A CRAP score
    Given the fixture's function "<function>" is in a file with no SF record in the LCOV
    When the report is produced
    Then the report row for "<function>" shows CRAP "N/A"

    Examples:
      | function          |
      | uncovered_file_fn |

  # qa-report-3
  Scenario: The worst-CRAP function sorts first and an N/A row sorts last
    Given the fixture has a worst-CRAP function "worst" and an N/A-CRAP function "uncovered_file_fn"
    When the report is produced
    Then the row for "worst" appears before the row for "partly_covered"
    And the row for "uncovered_file_fn" appears after every non-N/A row

  # qa-report-4
  Scenario: The report opens with the CRAP Report header block
    When the report is produced
    Then the first printed line is "CRAP Report"
    And a header row names "Function", "Module", "CC", "Cov%", and "CRAP"

  # qa-report-5
  Scenario Outline: --max-crap gates the exit code on the worst CRAP score
    Given the fixture's worst CRAP score is 30.0
    When the command runs with "--max-crap <threshold>"
    Then the command exits with status "<exit>"

    Examples:
      | threshold | exit     |
      | 29        | non-zero |
      | 30        | zero     |

  # qa-report-6
  Scenario: An N/A CRAP row never trips the --max-crap gate
    Given the fixture has an N/A-CRAP function and its worst finite CRAP score is 30.0
    When the command runs with "--max-crap 30"
    Then the command exits with status "zero"

  # qa-report-7
  Scenario Outline: --max-workers produces the same report as a serial run
    When the command runs the fixture with "--max-workers <workers>"
    Then the report text is identical to the serial report over the same fixture

    Examples:
      | workers |
      | 4       |
