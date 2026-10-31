"""PGD-15: ``cli/console.py`` is the only printer, and every line goes through ``redact``."""

from __future__ import annotations

import ast
import io
import sys
from pathlib import Path

import pytest

from gmail_pdf import redaction
from gmail_pdf.cli import console
from gmail_pdf.domain import events
from gmail_pdf.domain.models import MessageRef, RunResult, RunSummary
from tests.support import sentinels
from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("FR-005", "NFR-012")


def test_the_count_line_goes_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    refs = (MessageRef("a", 1), MessageRef("b", 2), MessageRef("c", 3))

    console.print_summary(RunSummary(RunResult.COMPLETED, refs))

    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("Messages in range: 3\n", "")


def test_a_cancelled_run_prints_the_cancel_notice_to_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    console.print_summary(RunSummary(RunResult.CANCELLED))

    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "Run cancelled\n")


def test_error_lines_go_to_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    console.print_error_line("error: something fixed")

    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("", "error: something fixed\n")


@pytest.mark.parametrize("printer", ["error", "sink"])
def test_every_line_passes_through_the_redaction_path(
    capsys: pytest.CaptureFixture[str], printer: str
) -> None:
    redaction.register_secret(sentinels.CLIENT_SECRET)
    text = f"value {sentinels.CLIENT_SECRET} and {sentinels.UNREGISTERED_GOCSPX}"

    if printer == "error":
        console.print_error_line(text)
    else:
        console.ConsoleSink().emit(
            events.Warning(events.WarningCode.TOKEN_OUTSIDE_PROFILE, 1, text)
        )

    captured = capsys.readouterr()
    assert sentinels.leaked(captured.out + captured.err) == []
    assert redaction.REDACTED in captured.err


def test_a_warning_without_text_prints_its_code_name(capsys: pytest.CaptureFixture[str]) -> None:
    console.ConsoleSink().emit(events.Warning(events.WarningCode.TOKEN_OUTSIDE_PROFILE))

    assert capsys.readouterr().err == "warning: token_outside_profile\n"


def test_a_warning_with_text_prints_the_text(capsys: pytest.CaptureFixture[str]) -> None:
    console.ConsoleSink().emit(events.Warning(events.WarningCode.TOKEN_OUTSIDE_PROFILE, 0, "hello"))

    assert capsys.readouterr().err == "warning: hello\n"


def test_a_missing_standard_stream_is_not_an_error_and_not_redirected_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", None)

    console.print_error_line("error: nobody to read this")

    assert stdout.getvalue() == ""


class ClosedPipe(io.StringIO):
    def write(self, text: str, /) -> int:
        raise BrokenPipeError

    def flush(self) -> None:
        raise BrokenPipeError


def test_a_closed_pipe_is_not_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdout", ClosedPipe())

    console.print_summary(RunSummary(RunResult.COMPLETED, ()))


def test_no_module_outside_the_console_calls_print() -> None:
    offenders = []
    for path in sorted((REPO_ROOT / "gmail_pdf").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
                and path != Path(REPO_ROOT / "gmail_pdf" / "cli" / "console.py")
            ):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")

    assert offenders == []
