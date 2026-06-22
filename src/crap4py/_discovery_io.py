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


def _is_acceptable_source_file(filepath: str, patterns: list[str]) -> bool:
    return (
        filepath.endswith(".py")
        and not _is_test_file(os.path.basename(filepath))
        and not _is_gitignored(filepath, patterns)
    )


def collect_source_files(paths: list[str]) -> list[str]:
    patterns = _load_gitignore_patterns()
    result: list[str] = []
    for path in paths:
        if os.path.isfile(path):
            if _is_acceptable_source_file(path, patterns):
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
        accepted = [
            os.path.join(dirpath, fname)
            for fname in sorted(filenames)
            if _is_acceptable_source_file(os.path.join(dirpath, fname), patterns)
        ]
        files.extend(accepted)
    return files


def _load_gitignore_patterns() -> list[str]:
    gitignore_path = os.path.join(os.getcwd(), ".gitignore")
    if not os.path.isfile(gitignore_path):
        return []
    with open(gitignore_path) as f:
        return [
            line.rstrip("\n")
            for line in f
            if line.rstrip("\n") and not line.startswith("#")
        ]


def _is_gitignored(path: str, patterns: list[str]) -> bool:
    rel = os.path.relpath(path, os.getcwd())
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
