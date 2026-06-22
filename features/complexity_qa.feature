Feature: QA — Cyclomatic complexity is observable through the crap4py CLI

  # TRACKING: #7
  #
  # CONTRACT:
  #   End-to-end QA for C1. Operates only through the user interface:
  #   the `uv run crap4py` command and its printed report. No project API.
  #   The QA agent reads the CC column of the report for a named function.
  #
  # CONSTRAINTS:
  #   - Verification uses committed fixtures: a Python source file plus an LCOV
  #     file. Each fixture states the expected CC for each function in a comment.
  #   - The QA agent asserts on the CC value shown in the report, not on
  #     coverage % or CRAP score (those are C3/C4).
  #   - Coverage data is supplied only so the command runs; CC must be correct
  #     regardless of coverage.
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Re-running the command on the same fixtures yields the same CC values.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT assert coverage % (C3) or CRAP score / sort order / formatting
  #     (C4) beyond locating the CC column for a named function.
  #   - ASSUMED: `uv run crap4py` is the user-facing invocation and prints a
  #     report whose rows expose a per-function CC value.
  #
  # UX INTENT: none
  # Design artifacts: none

  Background:
    Given a committed Python fixture file and a matching LCOV file
    And the command "uv run crap4py --lcov <lcov> <source>" has been run

  # qa-complexity-1
  Scenario Outline: The report shows the expected complexity for a known function
    Given the fixture defines a function "<function>" with expected complexity <cc>
    When the report is produced
    Then the report row for "<function>" shows CC <cc>

    Examples:
      | function       | cc |
      | straight_line  | 1  |
      | one_branch     | 2  |

  # qa-complexity-2
  Scenario: Expression-level branching is reflected end to end
    Given the fixture defines a function "boolean_heavy" using chained `and`/`or`
    And its expected complexity under the radon model is 4
    When the report is produced
    Then the report row for "boolean_heavy" shows CC 4

  # qa-complexity-3
  Scenario: A `with` statement does not change the reported complexity
    Given the fixture defines a function "uses_with" whose only compound statement is a `with`
    When the report is produced
    Then the report row for "uses_with" shows CC 1

  # qa-complexity-4
  Scenario: Nested functions appear as separate rows with independent complexity
    Given the fixture defines an outer function "outer" containing a nested function "inner"
    And "outer" has expected complexity 1 and "inner" has expected complexity 3
    When the report is produced
    Then the report has a row for "outer" showing CC 1
    And the report has a row for "inner" showing CC 3
