Feature: QA — Function discovery is observable through the crap4py CLI

  # TRACKING: #8
  #
  # CONTRACT:
  #   End-to-end QA for C2. Operates only through the user interface:
  #   the `uv run crap4py` command and its printed report. No project API.
  #   The QA agent reads the function (qualified name) and module (file path)
  #   columns of the report, and the set of rows present, to verify which
  #   functions were discovered, how they are named, and what was skipped.
  #
  # CONSTRAINTS:
  #   - Verification uses committed fixtures: a small Python source tree plus a
  #     matching LCOV file. Each fixture documents, in a comment, the qualified
  #     names expected (and which files must NOT appear).
  #   - The QA agent asserts on the presence/absence of report rows and on the
  #     function and module columns, NOT on CC, coverage %, or CRAP score
  #     (those are C1/C3/C4).
  #   - Coverage data is supplied only so the command runs; discovery must be
  #     correct regardless of coverage.
  #   - The fixture tree includes a `.gitignore` and a test file so the skip
  #     rules are exercised through the real CLI.
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Re-running the command on the same fixture tree yields the same set of
  #     rows in the same order.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT assert CC (C1), coverage % (C3), or CRAP score / sort order /
  #     numeric formatting (C4) beyond reading the function and module columns.
  #   - ASSUMED: `uv run crap4py` is the user-facing invocation and prints a
  #     report whose rows expose a per-function qualified name and a module
  #     (file path) column.
  #
  # UX INTENT: none
  # Design artifacts: none

  Background:
    Given a committed Python fixture tree and a matching LCOV file
    And the command "uv run crap4py --lcov <lcov> <root>" has been run

  # qa-discovery-1
  Scenario Outline: The report has a row for each discovered function, qualified
    Given the fixture defines a function whose expected qualified name is "<qualified>"
    When the report is produced
    Then the report has a row for "<qualified>"

    Examples:
      | qualified         |
      | extract_functions |
      | Function.score    |
      | Outer.Inner.run   |

  # qa-discovery-2
  Scenario: A nested function appears as its own row, named by its own def
    Given the fixture defines a function "compute" containing a nested function "helper"
    When the report is produced
    Then the report has a row for "compute"
    And the report has a row for "helper"

  # qa-discovery-3
  Scenario: A decorated method keeps its def-based name in the report
    Given the fixture defines a "@property" method "name" on class "User"
    When the report is produced
    Then the report has a row for "User.name"

  # qa-discovery-4
  Scenario Outline: The module column shows the source file path of the function
    Given the fixture defines function "<function>" in file "<rel_path>"
    When the report is produced
    Then the report row for "<function>" shows module "<rel_path>"

    Examples:
      | function          | rel_path                  |
      | extract_functions | src/crap4py/complexity.py |

  # qa-discovery-5
  Scenario Outline: Test files do not appear in the report
    Given the fixture tree includes a test file "<test_file>" defining a function "<test_function>"
    When the report is produced
    Then the report has no row for "<test_function>"

    Examples:
      | test_file         | test_function |
      | tests/test_cli.py | test_runs     |

  # qa-discovery-6
  Scenario Outline: A gitignored file does not appear in the report
    Given the fixture tree's `.gitignore` ignores "<ignored_path>" which defines a function "<ignored_function>"
    When the report is produced
    Then the report has no row for "<ignored_function>"

    Examples:
      | ignored_path      | ignored_function |
      | build/generated.py | generated        |
