"""Tests for the __main__ CLI adapter shell."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

_SIMPLE_SOURCE = "def add(a, b):\n    return a + b\n"


def test_main_missing_lcov_exits_with_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["crap4py", "--lcov", str(tmp_path / "missing.lcov"), str(tmp_path)],
    )
    from crap4py.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_main_prints_table_for_valid_input(tmp_path, monkeypatch, capsys):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    from crap4py.discovery import discover_functions

    entries = discover_functions([str(tmp_path)])
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{label}\nBRDA:1,0,0,1\nend_of_record\n")
    monkeypatch.setattr(sys, "argv", ["crap4py", "--lcov", str(lcov_file), str(tmp_path)])
    from crap4py.__main__ import main

    main()
    captured = capsys.readouterr()
    assert "Function" in captured.out
    assert "add" in captured.out


def test_main_oserror_from_build_report(tmp_path, monkeypatch, capsys):
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(sys, "argv", ["crap4py", "--lcov", str(lcov_file), str(tmp_path)])

    import crap4py._report as report_mod

    def raise_oserror(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(report_mod, "build_report", raise_oserror)

    from crap4py.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


# --- mutant-killing tests ---


def test_main_lcov_argument_is_required(monkeypatch, capsys):
    # mutmut_12/15/19: required=None / removed / False → --lcov becomes optional
    monkeypatch.setattr(sys, "argv", ["crap4py", "src/"])
    from crap4py.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main()
    # argparse exits with code 2 when a required arg is missing
    assert exc.value.code == 2


def test_main_prog_name_is_crap4py(monkeypatch, capsys):
    # mutmut_2/4/6/7: prog changed — affects --help output
    monkeypatch.setattr(sys, "argv", ["crap4py", "--help"])
    from crap4py.__main__ import main

    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "crap4py" in captured.out


def test_main_description_shown_in_help(monkeypatch, capsys):
    # mutmut_3/5/8/9/10: description changed or set to None
    monkeypatch.setattr(sys, "argv", ["crap4py", "--help"])
    from crap4py.__main__ import main

    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "CRAP" in captured.out or "crap" in captured.out.lower()


def test_main_lcov_help_shown(monkeypatch, capsys):
    # mutmut_13/16/20/21/22: --lcov help string changed or removed
    monkeypatch.setattr(sys, "argv", ["crap4py", "--help"])
    from crap4py.__main__ import main

    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "--lcov" in captured.out


def test_main_paths_argument_accepted(monkeypatch, tmp_path, capsys):
    # mutmut_25/28/32/33/34: paths help string changed — verify paths positional arg still works
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(sys, "argv", ["crap4py", "--lcov", str(lcov_file), str(tmp_path)])
    from crap4py.__main__ import main

    main()
    captured = capsys.readouterr()
    assert "Function" in captured.out


def test_main_paths_accepts_multiple_paths(monkeypatch, tmp_path, capsys):
    # mutmut_24/27: nargs=None / nargs removed — paths becomes a single string, not a list
    # With nargs="+", multiple paths are accepted; without it, only one (or stdin hang)
    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()
    (dir_a / "foo.py").write_text("def fn_a(): pass\n")
    (dir_b / "bar.py").write_text("def fn_b(): pass\n")
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(sys, "argv", ["crap4py", "--lcov", str(lcov_file), str(dir_a), str(dir_b)])
    from crap4py.__main__ import main

    main()
    captured = capsys.readouterr()
    assert "fn_a" in captured.out
    assert "fn_b" in captured.out


def test_main_max_crap_exits_nonzero_when_exceeded(tmp_path, monkeypatch, capsys):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    from crap4py.discovery import discover_functions

    entries = discover_functions([str(tmp_path)])
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{label}\nend_of_record\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["crap4py", "--lcov", str(lcov_file), "--max-crap", "0.5", str(tmp_path)],
    )
    from crap4py.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code != 0


def test_main_max_crap_exits_zero_when_not_exceeded(tmp_path, monkeypatch, capsys):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    from crap4py.discovery import discover_functions

    entries = discover_functions([str(tmp_path)])
    label = entries[0].module_label
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text(f"TN:\nSF:{label}\nBRDA:1,0,0,1\nend_of_record\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["crap4py", "--lcov", str(lcov_file), "--max-crap", "9999", str(tmp_path)],
    )
    from crap4py.__main__ import main

    main()
    captured = capsys.readouterr()
    assert "Function" in captured.out


def test_main_max_workers_invalid_exits_error(tmp_path, monkeypatch, capsys):
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["crap4py", "--lcov", str(lcov_file), "--max-workers", "abc", str(tmp_path)],
    )
    from crap4py.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()


def test_main_max_workers_zero_exits_error(tmp_path, monkeypatch, capsys):
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["crap4py", "--lcov", str(lcov_file), "--max-workers", "0", str(tmp_path)],
    )
    from crap4py.__main__ import main

    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_main_max_workers_valid_runs_normally(tmp_path, monkeypatch, capsys):
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["crap4py", "--lcov", str(lcov_file), "--max-workers", "4", str(tmp_path)],
    )
    from crap4py.__main__ import main

    main()
    captured = capsys.readouterr()
    assert "Function" in captured.out


def test_main_max_crap_na_rows_not_counted_for_gate(tmp_path, monkeypatch, capsys):
    src_file = tmp_path / "foo.py"
    src_file.write_text(_SIMPLE_SOURCE)
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["crap4py", "--lcov", str(lcov_file), "--max-crap", "0.5", str(tmp_path)],
    )
    import crap4py._report as report_mod
    from crap4py.__main__ import main
    from crap4py._crap import ReportRow
    from crap4py.coverage import NA

    na_rows = [ReportRow("add", str(tmp_path / "foo.py"), 1, NA)]
    monkeypatch.setattr(report_mod, "build_report", lambda *a, **kw: na_rows)

    main()
    captured = capsys.readouterr()
    assert "N/A" in captured.out
