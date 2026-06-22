# C3 QA fixture: functions with known branch coverage.
# expected: partly_covered → 0.75 (3 of 4 branches taken)
# expected: fully_covered  → 1.0  (2 of 2 branches taken)
# expected: trivial        → 1.0  (zero-branch; file is in LCOV)


def partly_covered(x):
    if x > 0:
        return "positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"
    return None


def fully_covered(x):
    if x:
        return True
    return False


def trivial():
    return 42
