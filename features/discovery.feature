Feature: Function discovery and qualified naming

  # TRACKING: #8
  #
  # CONTRACT:
  #   Input:  one or more source paths (files or directories).
  #   Output: an ordered set of function entries, one per `def`/`async def`
  #           found in scope. Each entry has:
  #             - qualified name : str  (def name qualified by enclosing classes)
  #             - module label   : str  (source file path relative to cwd)
  #             - line range     : (start_line, end_line), 1-based inclusive,
  #                                 spanning the `def` node (`lineno`..`end_lineno`)
  #   Naming and discovery rules are fixed by ADR 0003.
  #
  # CONSTRAINTS:
  #   - Every `def`/`async def` in scope is discovered — module-level functions,
  #     methods, nested classes' methods, and nested/inner functions — each as a
  #     separate entry (consistent with C1 CC scoping).
  #   - Qualified name = `def` name prefixed by every enclosing CLASS, dotted:
  #     bare function -> name; method -> `Class.method`; nested class ->
  #     `Outer.Inner.method`. Enclosing FUNCTIONS do not qualify (only classes).
  #   - Decorators never change the name or whether an entry appears. Each
  #     `@overload` stub is its own entry. Properties/static/class methods are
  #     named by their `def`.
  #   - Module label is the source file path relative to the invocation cwd.
  #   - Line range is the `def`'s own ast span; for a decorated function it starts
  #     at the `def` line, not the decorator line.
  #   - Skip rules: a path ignored by the project `.gitignore` is not scored;
  #     test files (`test_*.py`, `*_test.py`) are always skipped on top of that.
  #
  # SEQUENCING: none
  #
  # NFR:
  #   - Deterministic: the same file tree always yields the same entries.
  #
  # SIDE EFFECTS: none
  #
  # SCOPE:
  #   - Does NOT compute CC (C1, #7) — entries carry name/module/range only.
  #   - Does NOT read LCOV or compute coverage (C3, #9); the line range is
  #     produced HERE and consumed there.
  #   - Does NOT sort, score, or format the report (C4, #10).
  #   - Does NOT infer dotted import paths; the module label is a file path.
  #   - ASSUMED: discovered source files are syntactically valid Python parseable
  #     by `ast`.
  #
  # UX INTENT: none
  # Design artifacts: none

  Background:
    Given a Python project whose source is discovered from its root

  # discovery-1
  Scenario Outline: A module-level function is its own qualified name
    Given a source file defining a top-level function "<def_name>"
    When functions are discovered
    Then an entry exists with qualified name "<qualified>"

    Examples:
      | def_name          | qualified         |
      | extract_functions | extract_functions |
      | _private          | _private          |

  # discovery-2
  Scenario Outline: A method is qualified by its enclosing class
    Given a source file defining method "<method>" inside class "<cls>"
    When functions are discovered
    Then an entry exists with qualified name "<qualified>"

    Examples:
      | cls      | method | qualified       |
      | Function | score  | Function.score  |
      | Report   | render | Report.render   |

  # discovery-3
  Scenario Outline: Nested classes qualify with every enclosing class, dotted
    Given a source file defining method "<method>" inside class "<inner>" nested in class "<outer>"
    When functions are discovered
    Then an entry exists with qualified name "<qualified>"

    Examples:
      | outer | inner | method | qualified          |
      | Outer | Inner | run    | Outer.Inner.run    |

  # discovery-4
  Scenario Outline: Nested functions are separate entries named by their own def, not the enclosing function
    Given a source file where function "<outer>" contains a nested function "<inner>"
    When functions are discovered
    Then an entry exists with qualified name "<outer>"
    And an entry exists with qualified name "<inner>"

    Examples:
      | outer    | inner   |
      | compute  | helper  |

  # discovery-5
  Scenario Outline: `async def` is discovered like `def`
    Given a source file defining an async function "<def_name>"
    When functions are discovered
    Then an entry exists with qualified name "<def_name>"

    Examples:
      | def_name |
      | fetch    |

  # discovery-6
  Scenario Outline: Decorators do not change the qualified name
    Given a source file defining method "<method>" in class "<cls>" decorated with "<decorator>"
    When functions are discovered
    Then an entry exists with qualified name "<qualified>"

    Examples:
      | cls  | method | decorator      | qualified  |
      | User | name   | @property      | User.name  |
      | Math | of     | @staticmethod  | Math.of    |

  # discovery-7
  Scenario Outline: Each `@overload` stub is its own entry sharing the name
    Given a source file with <stub_count> `@overload` stubs named "<def_name>" and one implementation named "<def_name>"
    When functions are discovered
    Then <entry_count> entries exist with qualified name "<def_name>"

    Examples:
      | def_name | stub_count | entry_count |
      | parse    | 2          | 3           |

  # discovery-8
  Scenario Outline: The module label is the source file path relative to cwd
    Given a source file at relative path "<rel_path>" defining a function "<def_name>"
    When functions are discovered
    Then the entry for "<def_name>" has module label "<rel_path>"

    Examples:
      | rel_path                  | def_name |
      | src/crap4py/complexity.py | parse    |
      | scripts/tool.py           | main     |

  # discovery-9
  Scenario Outline: The line range spans the def node, starting at the def line
    Given a source file where function "<def_name>" spans lines <start> to <end>
    When functions are discovered
    Then the entry for "<def_name>" has line range <start> to <end>

    Examples:
      | def_name | start | end |
      | plain    | 1     | 2   |
      | wide     | 5     | 12  |

  # discovery-10
  Scenario Outline: A decorated function's range starts at the def line, not the decorator
    Given a source file where function "<def_name>" has a decorator on line <decorator_line> and `def` on line <def_line> ending on line <end>
    When functions are discovered
    Then the entry for "<def_name>" has line range <def_line> to <end>

    Examples:
      | def_name | decorator_line | def_line | end |
      | routed   | 3              | 4        | 6   |

  # discovery-11
  Scenario Outline: Test files are always skipped
    Given a source tree containing a non-test file "<source>" and a test file "<test_file>"
    When functions are discovered
    Then entries come only from "<source>"
    And no entry has module label "<test_file>"

    Examples:
      | source              | test_file               |
      | src/crap4py/cli.py  | tests/test_cli.py       |
      | src/crap4py/cli.py  | tests/cli_test.py       |

  # discovery-12
  Scenario Outline: Paths ignored by `.gitignore` are not scored
    Given a project whose `.gitignore` ignores "<ignored_path>"
    And a non-ignored source file "<kept_path>"
    When functions are discovered
    Then entries come only from "<kept_path>"
    And no entry has module label "<ignored_path>"

    Examples:
      | ignored_path                | kept_path           |
      | .venv/lib/site.py           | src/crap4py/cli.py  |
      | build/generated.py          | src/crap4py/cli.py  |
