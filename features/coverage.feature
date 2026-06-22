Feature: LCOV branch-coverage resolution

  # TRACKING: #9
  #
  # CONTRACT:
  #   Input:  a pre-generated LCOV file (coverage.py `--cov-branch` output) and,
  #           per function, its source file path and line range (start, end),
  #           1-based inclusive, produced by C2.
  #   Output: a coverage value per function — either a fraction in [0, 1] or the
  #           sentinel N/A.
  #   Coverage rules are fixed by ADR 0002.
  #
  # CONSTRAINTS:
  #   - Coverage = (# BRDA records in the function's line range whose `taken`
  #     is >= 1) / (# BRDA records in that range). `taken` of `-` (block never
  #     reached) and `0` (reached, branch not taken) are both uncovered for the
  #     numerator but both count toward the denominator.
  #   - A function with no BRDA records in its range is 100% (1.0), even when its
  #     source file is present in the LCOV.
  #   - Coverage is N/A only when the function's source file has no matching `SF`
  #     record in the LCOV.
  #   - A source file path is matched to an `SF` record by path normalization and
  #     suffix matching (LCOV paths may be absolute, relative, or rooted
  #     differently from cwd).
  #   - coverage.py quirks are tolerated: the BRDA `branch` field is opaque text
  #     (not an integer); the `block` field is always 0; BRDA records with
  #     `line` = 0 are ignored.
  #   - Non-BRDA records (`DA`, `FN`, `FNDA`, `LF`, `LH`, `BRF`, `BRH`,
  #     `end_of_record`) are tolerated whether present or absent and never drive
  #     the coverage number. There is no DA line-coverage fallback.
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Deterministic: the same LCOV file and the same line range always yield the
  #     same coverage value.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT discover functions or compute line ranges (C2, #8); the line
  #     range is an input produced there and consumed here.
  #   - Does NOT compute CC (C1, #7).
  #   - Does NOT combine complexity and coverage into a CRAP score, sort, or
  #     format the report (C4, #10).
  #   - Does NOT run tests or invoke coverage.py; it consumes a pre-generated
  #     LCOV file.
  #   - Does NOT parse non-LCOV coverage formats.
  #   - ASSUMED: the LCOV file is well-formed coverage.py `--cov-branch` output;
  #     line ranges are 1-based inclusive over the function's `def` span.
  #
  # UX INTENT: none
  # Design artifacts: none

  Background:
    Given an LCOV file produced by coverage.py and a function with a known line range

  # coverage-1
  Scenario Outline: Coverage is the fraction of in-range branches taken
    Given a function in a file present in the LCOV
    And <taken_count> of its <total_count> in-range BRDA branches have a taken count of at least 1
    When coverage is resolved for the function
    Then the function's coverage is "<coverage>"

    Examples:
      | taken_count | total_count | coverage |
      | 3           | 4           | 0.75     |
      | 4           | 4           | 1.0      |
      | 0           | 4           | 0.0      |

  # coverage-2
  Scenario Outline: A taken value of "-" or "0" is uncovered but still counts in the denominator
    Given a function in a file present in the LCOV
    And it has one in-range BRDA branch with taken "<taken>"
    And it has one in-range BRDA branch with taken "1"
    When coverage is resolved for the function
    Then the function's coverage is "<coverage>"

    Examples:
      | taken | coverage |
      | -     | 0.5      |
      | 0     | 0.5      |

  # coverage-3
  Scenario: A function with no in-range branches is 100% covered
    Given a function in a file present in the LCOV
    And the LCOV has no BRDA records within the function's line range
    When coverage is resolved for the function
    Then the function's coverage is "1.0"

  # coverage-4
  Scenario Outline: Coverage is N/A when the source file is absent from the LCOV
    Given the function's source file "<source>" has no matching SF record in the LCOV
    When coverage is resolved for the function
    Then the function's coverage is "N/A"

    Examples:
      | source                    |
      | src/crap4py/complexity.py |

  # coverage-5
  Scenario Outline: A source path is matched to an SF record by suffix matching
    Given the LCOV has an SF record for "<sf_path>"
    And the function's discovered source path is "<source>"
    When coverage is resolved for the function
    Then the function's source file is matched to the SF record for "<sf_path>"

    Examples:
      | sf_path                            | source                    |
      | /abs/proj/src/crap4py/complexity.py | src/crap4py/complexity.py |

  # coverage-6
  Scenario: BRDA records on line 0 are ignored
    Given a function in a file present in the LCOV
    And the LCOV has a BRDA record on line 0 with taken "0"
    And it has one in-range BRDA branch with taken "1"
    When coverage is resolved for the function
    Then the function's coverage is "1.0"

  # coverage-7
  Scenario Outline: A textual branch id does not affect resolution
    Given a function in a file present in the LCOV
    And it has one in-range BRDA branch with branch id "<branch_id>" and taken "1"
    When coverage is resolved for the function
    Then the function's coverage is "1.0"

    Examples:
      | branch_id      |
      | jump to line 8 |
