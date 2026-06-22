Feature: Cyclomatic complexity from Python source

  # TRACKING: #7
  #
  # CONTRACT:
  #   Input:  a Python source function (syntactically valid).
  #   Output: one cyclomatic complexity (CC) integer per function entry, >= 1.
  #   CC = number of decision points + 1. Computed from the `ast`.
  #   Decision points and their weights are fixed by ADR 0001.
  #
  # CONSTRAINTS:
  #   - CC is derived from Python's `ast`, not from text heuristics.
  #   - Minimum CC of any function is 1 (a function with no decision points).
  #   - Counted (+1 each unless noted): if, elif, for, while, loop `else`,
  #     each `except`, ternary, each comprehension `for`/`if` clause, each
  #     non-wildcard `match` case, `assert`. Boolean `and`/`or` add +1 per
  #     EXTRA operand (len(values) - 1 per BoolOp node).
  #   - NOT counted (+0): `else` of an `if`, `try`, `finally`, `with`,
  #     wildcard `case _:` without a guard.
  #   - Every `def`/`async def` (incl. methods and nested functions) is a
  #     separate entry; a nested function's decision points count toward the
  #     nested function, not its enclosing function.
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Deterministic: the same source always yields the same CC.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT discover or walk source files (C2, #8).
  #   - Does NOT read coverage or compute coverage % (C3, #9).
  #   - Does NOT format the report or sort entries (C4, #10).
  #   - ASSUMED: input source is syntactically valid Python parseable by `ast`.
  #
  # UX INTENT: none
  # Design artifacts: none

  Background:
    Given a syntactically valid Python source

  # complexity-1
  Scenario Outline: A function with no decision points has complexity 1
    When the function body is "<body>"
    Then the cyclomatic complexity is <cc>

    Examples:
      | body                          | cc |
      | pass                          | 1  |
      | x = 1; y = 2; return x + y    | 1  |
      | return f(g(h(1)))             | 1  |

  # complexity-2
  Scenario Outline: `if` and `elif` add one each; `else` adds none
    When the function contains <if_count> `if`, <elif_count> `elif`, and <else_count> `else` clauses
    Then the cyclomatic complexity is <cc>

    Examples:
      | if_count | elif_count | else_count | cc |
      | 1        | 0          | 0          | 2  |
      | 1        | 0          | 1          | 2  |
      | 1        | 1          | 0          | 3  |
      | 1        | 2          | 1          | 4  |

  # complexity-3
  Scenario Outline: Loops add one; a loop `else` clause adds one
    When the function contains a "<loop>" loop with else="<has_else>"
    Then the cyclomatic complexity is <cc>

    Examples:
      | loop  | has_else | cc |
      | for   | no       | 2  |
      | for   | yes      | 3  |
      | while | no       | 2  |
      | while | yes      | 3  |

  # complexity-4
  Scenario Outline: Each `except` adds one; `try` and `finally` add none
    When the function contains a try with <except_count> except handlers and finally="<has_finally>"
    Then the cyclomatic complexity is <cc>

    Examples:
      | except_count | has_finally | cc |
      | 1            | no          | 2  |
      | 2            | no          | 3  |
      | 1            | yes         | 2  |
      | 0            | yes         | 1  |

  # complexity-5
  Scenario Outline: Boolean operators add one per extra operand
    When the function condition is "<expression>"
    Then the cyclomatic complexity is <cc>

    Examples:
      | expression      | cc |
      | a and b         | 2  |
      | a or b          | 2  |
      | a and b and c   | 3  |
      | a and b or c    | 3  |

  # complexity-6
  Scenario Outline: A ternary expression adds one
    When the function body is "<body>"
    Then the cyclomatic complexity is <cc>

    Examples:
      | body                       | cc |
      | return a if cond else b    | 2  |

  # complexity-7
  Scenario Outline: Comprehension `for` and `if` clauses add one each
    When the function body is "<body>"
    Then the cyclomatic complexity is <cc>

    Examples:
      | body                                  | cc |
      | return [x for x in xs]                | 2  |
      | return [x for x in xs if x > 0]       | 3  |
      | return [x for xs in g for x in xs]    | 3  |

  # complexity-8
  Scenario Outline: Each non-wildcard `match` case adds one; `case _:` adds none
    When the function contains a match with <case_count> cases and wildcard="<has_wildcard>"
    Then the cyclomatic complexity is <cc>

    Examples:
      | case_count | has_wildcard | cc |
      | 1          | no           | 2  |
      | 2          | no           | 3  |
      | 2          | yes          | 3  |

  # complexity-9
  Scenario Outline: An `assert` adds one
    When the function contains <assert_count> assert statements
    Then the cyclomatic complexity is <cc>

    Examples:
      | assert_count | cc |
      | 1            | 2  |
      | 2            | 3  |

  # complexity-10
  Scenario Outline: A `with` statement adds none
    When the function contains <with_count> with statements
    Then the cyclomatic complexity is <cc>

    Examples:
      | with_count | cc |
      | 1          | 1  |
      | 2          | 1  |

  # complexity-11
  Scenario Outline: Nested functions are scored separately, not folded into the enclosing function
    When the outer function has <outer_dp> decision points and a nested function with <inner_dp> decision points
    Then the cyclomatic complexity of the outer function is <outer_cc>
    And the cyclomatic complexity of the nested function is <inner_cc>

    Examples:
      | outer_dp | inner_dp | outer_cc | inner_cc |
      | 0        | 2        | 1        | 3        |
      | 1        | 1        | 2        | 2        |

  # complexity-12
  Scenario Outline: Mixed constructs sum to the total decision points plus one
    When the function contains <ifs> if, <loops> for loops, <booleans> extra boolean operands, and <asserts> assert statements
    Then the cyclomatic complexity is <cc>

    Examples:
      | ifs | loops | booleans | asserts | cc |
      | 1   | 1     | 1        | 1       | 5  |
      | 2   | 0     | 2        | 0       | 5  |
