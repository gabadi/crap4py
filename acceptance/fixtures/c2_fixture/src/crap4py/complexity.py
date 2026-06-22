# C2 QA fixture: src/crap4py/complexity.py
# Expected qualified names:
#   extract_functions  (module-level)
#   Function.score     (method on class Function)
#   Outer.Inner.run    (nested class method)
#   compute            (module-level, outer)
#   helper             (nested inside compute)
#   User.name          (@property — decorator ignored)
#
# NOT expected: test_runs (in tests/test_cli.py), generated (in build/generated.py)


def extract_functions():
    return []


class Function:
    def score(self):
        return 0


class Outer:
    class Inner:
        def run(self):
            pass


def compute():
    def helper():
        pass
    return helper


class User:
    @property
    def name(self):
        return self._name
