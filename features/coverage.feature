# mutation-stamp: sha256=06784a323566952827b32574ed060de1e4b547c7486abccfc39f340820384ecc
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-06-22T16:07:42.431787Z","feature_name":"LCOV branch-coverage resolution","feature_path":"/Users/gabadi/workspace/addi/crap4py/.worktrees/coder/features/coverage.feature","background_hash":"1bb1f12caeebec7a3fa7249d2ed6e9d751086568de5215146a8a599d3a9c62bc","implementation_hash":"unknown","scenarios":[{"index":0,"name":"Coverage is the fraction of in-range branches taken","scenario_hash":"8f64d25a2b610b59ac7fa97a22c5611cbced3a4e7ff98a9fc6fd774b6809ad44","mutation_count":9,"result":{"Total":9,"Killed":9,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:40.974233Z"},{"index":1,"name":"A taken value of \"-\" or \"0\" is uncovered but still counts in the denominator","scenario_hash":"76bd841e2b30feecbc1e953fa60078c1901c1bfa1c8913ca3611a475cb4830f6","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:40.974233Z"},{"index":3,"name":"Coverage is N/A when the source file is absent from the LCOV","scenario_hash":"a60dd02bd9f1c734c25f5c5103a028b72ead1de5d812f2e07b34a090520d1a37","mutation_count":1,"result":{"Total":1,"Killed":1,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:40.974233Z"},{"index":4,"name":"A source path is matched to an SF record by suffix matching","scenario_hash":"51e78e043bcf25f1c5b0bddf2d39a257d8a9a5f66ab50f98d7e244f2bec33a4e","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:40.974233Z"},{"index":6,"name":"A textual branch id does not affect resolution","scenario_hash":"80f8fee2f8e9d6b8b22a2c3e6a72fcc639d911d3ebb7cadbe0c00deba6f58932","mutation_count":1,"result":{"Total":1,"Killed":1,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:40.974233Z"}]}
# acceptance-mutation-manifest-end

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
