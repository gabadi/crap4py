# C4 QA fixture: functions with known CC, coverage, and CRAP scores.
# partly_covered: CC=4, coverage=0.75 (3/4 BRDA taken), CRAP=4.2
# worst:          CC=5, coverage=0.0  (0/4 BRDA taken), CRAP=30.0
# Both functions are in the LCOV (SF record present).


def partly_covered(x):
    if x > 0:
        if x > 10:
            return "big positive"
        return "small positive"
    elif x < 0:
        return "negative"
    else:
        return "zero"


def worst(x):
    if x == 1:
        return 1
    if x == 2:
        return 2
    if x == 3:
        return 3
    if x == 4:
        return 4
    return 5
