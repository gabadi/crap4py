# mutation-stamp: sha256=8d165bc54c26449209ef25a2e5806499be93966591a63c9ac7a76b5fc045f83b
# acceptance-mutation-manifest-begin
# {"version":1,"tested_at":"2026-06-22T16:07:42.795486Z","feature_name":"Function discovery and qualified naming","feature_path":"/Users/gabadi/workspace/addi/crap4py/.worktrees/coder/features/discovery.feature","background_hash":"3fe72281467c0f4f8b8a0a108c0dd9cf1c3df9b57a38a20423f62968725dac2c","implementation_hash":"unknown","scenarios":[{"index":0,"name":"A module-level function is its own qualified name","scenario_hash":"2417ce361e66055e801166d233f77178645dce2585b302521a258b79193be4e9","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":1,"name":"A method is qualified by its enclosing class","scenario_hash":"e51c9670a33d92d51447fb0ce01854ed6880627ffa958c5914a8298da77d0a15","mutation_count":6,"result":{"Total":6,"Killed":6,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":2,"name":"Nested classes qualify with every enclosing class, dotted","scenario_hash":"c7d274c052ab7219c86022e067ae6b61ebafcbfa7f08c7ae47148ab68ad3de0c","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":3,"name":"Nested functions are separate entries named by their own def, not the enclosing function","scenario_hash":"8fdc3154902bd38ef6ebac5d000b0bfc37e6b95f83aa2fb1336556c43a5a55f6","mutation_count":2,"result":{"Total":2,"Killed":2,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":4,"name":"`async def` is discovered like `def`","scenario_hash":"2ab95f3d94a631da8d8ec1d8d6f44e35d05ac0e9e04951c9b5d76beecdf17672","mutation_count":1,"result":{"Total":1,"Killed":1,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":5,"name":"Decorators do not change the qualified name","scenario_hash":"cc668b97c9dff586765363f23225f9abe27e12ec75d8bc6294c833f6212124ea","mutation_count":8,"result":{"Total":8,"Killed":8,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":6,"name":"Each `@overload` stub is its own entry sharing the name","scenario_hash":"7252419e98b7833edd0cf342febbbd77510e90dd7eae00d438f570a940886521","mutation_count":3,"result":{"Total":3,"Killed":3,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":7,"name":"The module label is the source file path relative to cwd","scenario_hash":"1d0f87d65ad6859f955520bfaa330c4a31cc23b8470ed1f477a208373db4841a","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":8,"name":"The line range spans the def node, starting at the def line","scenario_hash":"c455b4c08f7e48976bb6bb636570c4b916e938f8fa51cbf9809c2bc2d948a146","mutation_count":6,"result":{"Total":6,"Killed":6,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":9,"name":"A decorated function's range starts at the def line, not the decorator","scenario_hash":"01d2f1a699d95b32d5ff16a51567470e189afa6d64e084a64192afd51c99a984","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":10,"name":"Test files are always skipped","scenario_hash":"d91fae144e17a8ea6cb632ffd4809798b8d2f038d6da8082a6295260b3ea331b","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"},{"index":11,"name":"Paths ignored by `.gitignore` are not scored","scenario_hash":"ff96d92f0ff4fd724508df62e227918111223903d56376e63db8e742e99b5cff","mutation_count":4,"result":{"Total":4,"Killed":4,"Survived":0,"Errors":0},"tested_at":"2026-06-22T16:05:42.558610Z"}]}
# acceptance-mutation-manifest-end

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
