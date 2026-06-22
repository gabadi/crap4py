Feature: QA — Branch coverage is observable through the crap4py CLI

  # TRACKING: #9
  #
  # CONTRACT:
  #   End-to-end QA for C3. Operates only through the user interface:
  #   the `uv run crap4py` command and its printed report. No project API.
  #   The QA agent reads the coverage column of the report (per function row)
  #   to verify the branch-coverage value resolved from the supplied LCOV file.
  #
  # CONSTRAINTS:
  #   - Verification uses committed fixtures: a small Python source tree plus a
  #     matching LCOV file whose BRDA records are authored to produce known
  #     per-function coverage values. Each fixture documents, in a comment, the
  #     expected coverage for each function row.
  #   - The QA agent asserts on the coverage column only, NOT on CC, qualified
  #     name beyond locating the row, or CRAP score / sort order (C1/C2/C4).
  #   - Fixtures exercise the load-bearing cases through the real CLI: a partially
  #     covered function, a fully covered function, a zero-branch function (100%),
  #     and a function whose file is absent from the LCOV (N/A).
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Re-running the command on the same fixture tree and LCOV yields the same
  #     coverage value for every row.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT assert CC (C1), discovery/naming beyond finding the row (C2), or
  #     CRAP score / sort order / numeric formatting of other columns (C4).
  #   - Does NOT run coverage.py; the LCOV fixture is pre-generated and committed.
  #   - ASSUMED: `uv run crap4py --lcov <lcov> <root>` is the user-facing
  #     invocation and prints a report whose rows expose a per-function coverage
  #     column showing a fraction (or N/A).
  #
  # UX INTENT: none
  # Design artifacts: none

  Background:
    Given a committed Python fixture tree and a matching LCOV file
    And the command "uv run crap4py --lcov <lcov> <root>" has been run

  # qa-coverage-1
  Scenario Outline: The coverage column shows the fraction of branches taken
    Given the fixture's function "<function>" has <taken_count> of <total_count> branches taken in the LCOV
    When the report is produced
    Then the report row for "<function>" shows coverage "<coverage>"

    Examples:
      | function       | taken_count | total_count | coverage |
      | partly_covered | 3           | 4           | 0.75     |
      | fully_covered  | 2           | 2           | 1.0      |

  # qa-coverage-2
  Scenario Outline: A zero-branch function shows 100% coverage
    Given the fixture's function "<function>" has no branches and its file is in the LCOV
    When the report is produced
    Then the report row for "<function>" shows coverage "1.0"

    Examples:
      | function |
      | trivial  |

  # qa-coverage-3
  Scenario Outline: A function whose file is absent from the LCOV shows N/A
    Given the fixture's function "<function>" is in a file with no SF record in the LCOV
    When the report is produced
    Then the report row for "<function>" shows coverage "N/A"

    Examples:
      | function   |
      | uncovered_file_fn |
