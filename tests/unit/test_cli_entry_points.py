"""AC-1 (in-process): the CLI entry points print usage and exit 0.

The subprocess runs of the same entry points are in ``tests/e2e/test_cli_subprocess.py``.
"""

from __future__ import annotations

import runpy
import sys
from importlib import metadata

import pytest

from gmail_pdf import __version__
from gmail_pdf.cli import main as cli_main
from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("NFR-020", "AC-1")

SHIM = REPO_ROOT / "gmail_pdf_downloader.py"


def test_version_is_the_development_version() -> None:
    assert __version__ == "0.9.0.dev0"


def test_main_help_prints_usage_and_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = cli_main.main(["--help"])

    out = capsys.readouterr().out
    assert code == 0
    assert out.startswith("usage: gmail-pdf")


def test_main_short_help_flag_returns_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli_main.main(["-h"]) == 0
    assert "usage: gmail-pdf" in capsys.readouterr().out


def test_main_without_arguments_prints_usage_and_returns_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli_main.main([]) == 0
    assert "usage: gmail-pdf" in capsys.readouterr().out


def test_main_unknown_flag_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    code = cli_main.main(["--no-such-flag"])

    assert code == 2
    assert "unrecognized arguments" in capsys.readouterr().err


def test_main_reads_sys_argv_when_argv_is_none(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["gmail-pdf", "--help"])

    assert cli_main.main() == 0
    assert "usage: gmail-pdf" in capsys.readouterr().out


def test_exit_code_maps_none_int_and_text_codes() -> None:
    assert cli_main._exit_code(SystemExit(None)) == 0
    assert cli_main._exit_code(SystemExit(5)) == 5
    assert cli_main._exit_code(SystemExit("message")) == 2


def test_entry_uses_process_arguments(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["gmail-pdf", "--help"])

    assert cli_main.entry() == 0
    assert "usage: gmail-pdf" in capsys.readouterr().out


def test_dunder_main_exits_zero_for_help(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["gmail_pdf", "--help"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("gmail_pdf", run_name="__main__")

    assert exc_info.value.code == 0
    assert "usage: gmail-pdf" in capsys.readouterr().out


def test_shim_exits_zero_for_help(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", [str(SHIM), "--help"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(SHIM), run_name="__main__")

    assert exc_info.value.code == 0
    assert "usage: gmail-pdf" in capsys.readouterr().out


def test_console_script_is_declared_for_the_cli_entry() -> None:
    scripts = {
        ep.name: ep.value
        for ep in metadata.entry_points(group="console_scripts")
        if ep.name == "gmail-pdf"
    }

    # Fails with an empty dict if `pip install --no-deps -e .` was not run.
    assert scripts == {"gmail-pdf": "gmail_pdf.cli.main:entry"}
    # ADR-005: the GUI launcher is an R2 deliverable and must not exist yet.
    assert "gmail-pdf-gui" not in metadata.entry_points(group="gui_scripts").names
    assert "gmail-pdf-gui" not in metadata.entry_points(group="console_scripts").names
