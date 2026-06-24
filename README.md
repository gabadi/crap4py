# crap4py

[![CI](https://github.com/gabadi/crap4py/actions/workflows/ci.yml/badge.svg)](https://github.com/gabadi/crap4py/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/crap4py)](https://pypi.org/project/crap4py/)

Python port of Uncle Bob's [crap4go](https://github.com/unclebob/crap4go) and [crap4clj](https://github.com/unclebob/crap4clj) — CRAP score per function for Python source files.

**CRAP** (Change Risk Anti-Pattern) = `CC² × (1 − coverage)³ + CC` — a per-function metric combining cyclomatic complexity and branch coverage. Higher means riskier to change. Conventional threshold: 30.

## Install

```sh
# Run without installing
uvx crap4py

# Persistent install
uv tool install crap4py
```

## Usage

```sh
crap4py src/ --lcov lcov.info
```

Generate `lcov.info` with [coverage.py](https://coverage.readthedocs.io/):

```sh
pytest --cov --cov-branch --cov-report=lcov:lcov.info
```

### Output

```
CRAP Report
Function                    | Module                        | CC | Cov%  | CRAP
----------------------------+-------------------------------+----+-------+-----
_sort_key                   | src/crap4py/_crap.py          |  3 |  33.3 |  9.9
main                        | src/crap4py/__main__.py       |  2 | 100.0 |  2.0
```

### Options

| Flag | Description |
|------|-------------|
| `--lcov PATH` | LCOV branch-coverage file (required) |
| `--max-crap N` | Exit non-zero if any function exceeds N (CI gate) |
| `--max-workers N` | Parallel workers for large codebases |
| `--fragment TEXT` | Only analyse files whose path contains TEXT |

### CI gate

```sh
crap4py src/ --lcov lcov.info --max-crap 30
```

Exits non-zero if any function's CRAP score exceeds the threshold. N/A functions (no coverage data) never trip the gate.

## How it works

- **Complexity** — cyclomatic complexity from Python's `ast` per `def`/`async def`
- **Coverage** — branch coverage from LCOV `BRDA` records intersected with each function's line range
- **Skips** — `.gitignore`-ignored paths and test files (`test_*.py`, `*_test.py`) are excluded automatically

See also: [crap4go](https://github.com/unclebob/crap4go), [crap4clj](https://github.com/unclebob/crap4clj).
