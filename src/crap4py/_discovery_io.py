"""IO adapter for function discovery (C2, #8).

Owns filesystem access: file walking, gitignore reading, source reading.
Keeps src/crap4py/discovery.py free of IO imports so the arch test passes.

All functions that produce CWD-relative output accept an explicit ``root``
parameter (defaulting to the actual cwd) so callers can be tested without
``os.chdir``.
"""
import fnmatch
import os


def relative_label(filepath: str, root: str | None = None) -> str:
    return os.path.relpath(filepath, root or os.getcwd())


def read_source(filepath: str) -> str | None:
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def _is_test_file(name: str) -> bool:
    return name.startswith("test_") or name.endswith("_test.py")


def _is_acceptable_source_file(filepath: str, patterns: list[str], root: str) -> bool:
    return (
        filepath.endswith(".py")
        and not _is_test_file(os.path.basename(filepath))
        and not _is_gitignored(filepath, patterns, root)
    )


def collect_source_files(paths: list[str], root: str | None = None) -> list[str]:
    cwd = root or os.getcwd()
    patterns = _load_gitignore_patterns(cwd)
    result: list[str] = []
    for path in paths:
        if os.path.isfile(path):
            if _is_acceptable_source_file(path, patterns, cwd):
                result.append(path)
        elif os.path.isdir(path):
            result.extend(_walk_dir(path, patterns, cwd))
    return result


def _walk_dir(dir_root: str, patterns: list[str], cwd: str) -> list[str]:
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(dir_root):
        dirnames[:] = sorted(
            d for d in dirnames
            if not _is_gitignored(os.path.join(dirpath, d), patterns, cwd)
        )
        accepted = [
            os.path.join(dirpath, fname)
            for fname in sorted(filenames)
            if _is_acceptable_source_file(os.path.join(dirpath, fname), patterns, cwd)
        ]
        files.extend(accepted)
    return files


def _load_gitignore_patterns(cwd: str) -> list[str]:
    gitignore_path = os.path.join(cwd, ".gitignore")
    if not os.path.isfile(gitignore_path):
        return []
    with open(gitignore_path) as f:
        return [
            line.rstrip("\n")
            for line in f
            if line.rstrip("\n") and not line.startswith("#")
        ]


def _is_gitignored(path: str, patterns: list[str], cwd: str) -> bool:
    rel = os.path.relpath(path, cwd)
    rel_fwd = rel.replace("\\", "/")
    name = os.path.basename(path)
    return any(_fnmatch_path(rel_fwd, name, pattern) for pattern in patterns)


def _fnmatch_path(rel: str, name: str, pattern: str) -> bool:
    pat = pattern.rstrip("/")
    if "/" in pat:
        return _match_path_pattern(rel, pat.lstrip("/"))
    return _match_name_pattern(rel, name, pat)


def _match_path_pattern(rel: str, pat: str) -> bool:
    return fnmatch.fnmatch(rel, pat) or rel.startswith(pat + "/") or rel == pat


def _match_name_pattern(rel: str, name: str, pat: str) -> bool:
    return fnmatch.fnmatch(name, pat) or any(
        fnmatch.fnmatch(part, pat) for part in rel.split("/")
    )
