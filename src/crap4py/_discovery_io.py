"""IO adapter for function discovery (C2, #8).

Owns filesystem access: file walking, gitignore reading, source reading.
Keeps src/crap4py/discovery.py free of IO imports so the arch test passes.
"""
import fnmatch
import os


def relative_label(filepath: str) -> str:
    return os.path.relpath(filepath, os.getcwd())


def read_source(filepath: str) -> str | None:
    try:
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def _is_test_file(name: str) -> bool:
    return name.startswith("test_") or name.endswith("_test.py")


def collect_source_files(paths: list[str]) -> list[str]:
    patterns = _load_gitignore_patterns()
    result: list[str] = []
    for path in paths:
        if os.path.isfile(path):
            if path.endswith(".py") and not _is_test_file(os.path.basename(path)):
                if not _is_gitignored(path, patterns):
                    result.append(path)
        elif os.path.isdir(path):
            result.extend(_walk_dir(path, patterns))
    return result


def _walk_dir(root: str, patterns: list[str]) -> list[str]:
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames
            if not _is_gitignored(os.path.join(dirpath, d), patterns)
        )
        for fname in sorted(filenames):
            if not fname.endswith(".py"):
                continue
            if _is_test_file(fname):
                continue
            fpath = os.path.join(dirpath, fname)
            if not _is_gitignored(fpath, patterns):
                files.append(fpath)
    return files


def _load_gitignore_patterns() -> list[str]:
    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    patterns: list[str] = []
    if os.path.isfile(gitignore_path):
        with open(gitignore_path) as f:
            for line in f:
                line = line.rstrip("\n")
                if line and not line.startswith("#"):
                    patterns.append(line)
    return patterns


def _is_gitignored(path: str, patterns: list[str]) -> bool:
    rel = os.path.relpath(path, os.getcwd())
    rel_fwd = rel.replace("\\", "/")
    name = os.path.basename(path)
    for pattern in patterns:
        if _fnmatch_path(rel_fwd, name, pattern):
            return True
    return False


def _fnmatch_path(rel: str, name: str, pattern: str) -> bool:
    pat = pattern.rstrip("/")
    if "/" in pat:
        p = pat.lstrip("/")
        if fnmatch.fnmatch(rel, p):
            return True
        if rel.startswith(p + "/") or rel == p:
            return True
    else:
        if fnmatch.fnmatch(name, pat):
            return True
        for part in rel.split("/"):
            if fnmatch.fnmatch(part, pat):
                return True
    return False
