"""PGD-13 AC-5, AC-7, AC-8 at the CLI: hooks first, exit 1 for failure and for Ctrl+C."""

from __future__ import annotations

import argparse
import sys
import threading
from collections.abc import Callable

import pytest

from gmail_pdf import redaction
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain import messages
from tests.support import sentinels

pytestmark = pytest.mark.req("FR-005", "NFR-012")

FAILURE = messages.UNEXPECTED_FAILURE_LINE + "\n"
CANCELLED = messages.RUN_CANCELLED_LINE + "\n"


class ParserThatRaises:
    """Stands in for the parser: ``parse_args`` raises ``error``."""

    def __init__(self, error: BaseException) -> None:
        self.error = error

    def parse_args(self, argv: object = None) -> argparse.Namespace:
        raise self.error

    def print_help(self) -> None:  # pragma: no cover - never reached
        raise AssertionError("parse_args should have raised")


def use_parser_that_raises(monkeypatch: pytest.MonkeyPatch, error: BaseException) -> None:
    monkeypatch.setattr(cli_main, "build_parser", lambda: ParserThatRaises(error))


# ----------------------------------------------------------------------------------- AC-7
@pytest.mark.req("AC-7")
def test_hooks_are_installed_before_the_parser_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    real_parser = cli_main.build_parser
    monkeypatch.setattr(
        redaction, "install_logging_redaction", lambda *handlers: calls.append("logging")
    )

    def recording_install_excepthooks() -> Callable[[], None]:
        calls.append("excepthooks")
        return lambda: None

    monkeypatch.setattr(redaction, "install_excepthooks", recording_install_excepthooks)

    def recording_build_parser() -> argparse.ArgumentParser:
        calls.append("build_parser")
        return real_parser()

    monkeypatch.setattr(cli_main, "build_parser", recording_build_parser)

    assert cli_main.main(["--help"]) == 0
    assert calls == ["logging", "excepthooks", "build_parser"]


@pytest.mark.req("AC-7")
def test_hooks_are_installed_before_any_argument_is_read(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[bool] = []
    original_hook = sys.excepthook

    def parser_factory() -> argparse.ArgumentParser:
        seen.append(sys.excepthook is not original_hook)
        return argparse.ArgumentParser()

    monkeypatch.setattr(cli_main, "build_parser", parser_factory)

    cli_main.main([])

    assert seen == [True]


@pytest.mark.req("AC-7")
def test_main_leaves_the_redacting_hooks_installed() -> None:
    before = (sys.excepthook, threading.excepthook)

    cli_main.main([])

    assert sys.excepthook is not before[0]
    assert threading.excepthook is not before[1]


# ----------------------------------------------------------------------------------- AC-5
@pytest.mark.parametrize(
    "error",
    [
        pytest.param(RuntimeError(sentinels.CLIENT_SECRET), id="runtime-error"),
        pytest.param(KeyError(sentinels.ACCESS_TOKEN), id="key-error"),
        pytest.param(OSError(2, sentinels.REFRESH_TOKEN), id="os-error"),
    ],
)
@pytest.mark.req("AC-5")
def test_an_unexpected_failure_prints_one_line_and_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], error: Exception
) -> None:
    use_parser_that_raises(monkeypatch, error)

    code = cli_main.main([])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (1, FAILURE, "")


@pytest.mark.req("AC-5")
def test_an_unexpected_failure_still_returns_one_when_help_is_requested(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    use_parser_that_raises(monkeypatch, ValueError(sentinels.CLIENT_SECRET))

    assert cli_main.main(["--help"]) == 1
    assert capsys.readouterr().err == FAILURE


# ----------------------------------------------------------------------------------- AC-8
@pytest.mark.req("AC-8")
def test_ctrl_c_prints_run_cancelled_and_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    use_parser_that_raises(monkeypatch, KeyboardInterrupt(sentinels.CLIENT_SECRET))

    code = cli_main.main([])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (1, CANCELLED, "")


# ------------------------------------------------------------ the earlier exit codes still hold
@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        pytest.param(["--help"], cli_main.EXIT_OK, id="help"),
        pytest.param(["--no-such-flag"], cli_main.EXIT_USAGE, id="usage-error"),
    ],
)
def test_exit_codes_for_help_and_usage_errors_are_unchanged(
    capsys: pytest.CaptureFixture[str], argv: list[str], expected: int
) -> None:
    assert cli_main.main(argv) == expected
    capsys.readouterr()


def test_the_failure_exit_code_is_one() -> None:
    assert cli_main.EXIT_FAILURE == 1
