# C3 QA fixture: function in a file with no SF record in the LCOV.
# expected: uncovered_file_fn → N/A (source absent from LCOV)


def uncovered_file_fn(x):
    return x * 2
