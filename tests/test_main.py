"""Tests for the __main__ CLI adapter shell."""
import sys
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

_SIMPLE_SOURCE = "def add(a, b):\n    return a + b\n"


def test_main_missing_lcov_exits_with_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["crap4py", "--lcov", str(tmp_path / "missing.lcov"), str(tmp_path)])
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
    assert "function" in captured.out
    assert "add" in captured.out


def test_main_oserror_from_build_rows(tmp_path, monkeypatch, capsys):
    lcov_file = tmp_path / "coverage.lcov"
    lcov_file.write_text("TN:\nend_of_record\n")
    monkeypatch.setattr(sys, "argv", ["crap4py", "--lcov", str(lcov_file), str(tmp_path)])

    import crap4py._report as report_mod
    def raise_oserror(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr(report_mod, "build_rows", raise_oserror)

    from crap4py.__main__ import main
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "error" in captured.err.lower()
