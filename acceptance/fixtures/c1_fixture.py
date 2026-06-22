# QA fixture for C1 (cyclomatic complexity).
# Each function has a comment stating its expected CC.

# expected CC: 1
def straight_line(x):
    return x + 1


# expected CC: 2
def one_branch(x):
    if x > 0:
        return x
    return -x


# expected CC: 4  (BoolOp with 4 values → 3 extra operands = 3 DPs + 1)
def boolean_heavy(a, b, c, d):
    return a and b and c and d


# expected CC: 1
def uses_with(ctx):
    with ctx as f:
        return f.read()


# expected CC: 1 (outer has no decision points)
# inner expected CC: 3 (2 ifs → 2 DPs + 1)
def outer():
    def inner(x, y):
        if x:
            pass
        if y:
            pass
