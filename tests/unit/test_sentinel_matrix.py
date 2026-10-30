"""PGD-13 AC-6: the sentinel-secret matrix (NFR-012, AC-07, test-strategy section 6).

Every *error path* is forced with sentinel secrets in its messages, arguments and cause chain,
then every *text surface* is read back and must hold 0 sentinel occurrences.

Rule for later stories ("AC in every story that adds a text surface"):

* a new error path: write ``def my_path(harness: Harness) -> None`` that provokes it through the
  real code, and append ``pytest.param(my_path, id="...")`` to ``ERROR_PATHS``;
* a new text surface (CSV writer, manifest, GUI text ...): add a branch to ``Harness.text`` and
  its name to ``SURFACES``.

Each addition is then checked against every existing surface or path with no other change.
The CLI is exercised in-process here; ``tests/e2e/test_redaction_subprocess.py`` repeats the
hook paths in a child interpreter.
"""

from __future__ import annotations

import contextlib
import io
import logging
import sys
import threading
from collections.abc import Callable, Iterator
from pathlib import Path

import httplib2
import pytest
from googleapiclient.errors import HttpError

from gmail_pdf import redaction
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain.errors import GmailPdfError
from gmail_pdf.redaction import install_excepthooks, install_logging_redaction, safe_message
from tests.support import sentinels

pytestmark = pytest.mark.req("FR-005", "NFR-012", "AC-6")

SURFACES = ("stdout", "stderr", "log_file", "excepthook_output")
SECRET_TEXT = " ".join(sentinels.ALL)
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


class Harness:
    """The text surfaces of one test run, and helpers that provoke error paths through them."""

    def __init__(self, log_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.monkeypatch = monkeypatch
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.hook_output = io.StringIO()
        self.log_path = log_path
        self.handler = logging.FileHandler(log_path, encoding="utf-8")

    def text(self, surface: str) -> str:
        """Everything written to ``surface`` so far."""
        self.handler.flush()
        if surface == "stdout":
            return self.stdout.getvalue()
        if surface == "stderr":
            return self.stderr.getvalue()
        if surface == "log_file":
            return self.log_path.read_text(encoding="utf-8")
        if surface == "excepthook_output":
            return self.hook_output.getvalue()
        raise AssertionError(f"unknown surface {surface!r}")

    def through_excepthook(self, exc: BaseException) -> None:
        """Hand ``exc`` to ``sys.excepthook``, capturing what the hook prints."""
        with contextlib.redirect_stderr(self.hook_output):
            sys.excepthook(type(exc), exc, exc.__traceback__)

    def through_thread_excepthook(self, exc: BaseException) -> None:
        """Raise ``exc`` in a worker thread so ``threading.excepthook`` handles it."""

        def fail() -> None:
            raise exc

        worker = threading.Thread(target=fail)
        with contextlib.redirect_stderr(self.hook_output):
            worker.start()
            worker.join(timeout=10)


@pytest.fixture
def harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Harness]:
    """Redaction installed the way the application does it, with every surface captured."""
    for value in sentinels.REGISTERED:
        redaction.register_secret(value)
    h = Harness(tmp_path / "run.log", monkeypatch)
    monkeypatch.setattr(sys, "stdout", h.stdout)
    monkeypatch.setattr(sys, "stderr", h.stderr)
    h.handler.setLevel(logging.DEBUG)
    h.handler.setFormatter(logging.Formatter(LOG_FORMAT))
    install_logging_redaction(h.handler)
    install_excepthooks()
    root = logging.getLogger()
    previous_level = root.level
    root.setLevel(logging.DEBUG)
    root.addHandler(h.handler)
    yield h
    root.removeHandler(h.handler)
    root.setLevel(previous_level)
    h.handler.close()


# ------------------------------------------------------------------------ the error paths
def secret_error() -> RuntimeError:
    """A raised error with sentinels in its message, its args and its cause."""
    try:
        try:
            raise ValueError(f"inner {SECRET_TEXT}")
        except ValueError as inner:
            raise RuntimeError(SECRET_TEXT, {"echo": SECRET_TEXT}) from inner
    except RuntimeError as outer:
        return outer


def gmail_http_error() -> HttpError:
    """The kind of error Gmail returns: its body and URI echo the sentinels."""
    response = httplib2.Response({"status": 401})
    response.reason = SECRET_TEXT
    return HttpError(
        response, SECRET_TEXT.encode(), uri=f"https://example.invalid/?access_token={SECRET_TEXT}"
    )


def uncaught_exception(h: Harness) -> None:
    h.through_excepthook(secret_error())
    h.through_thread_excepthook(secret_error())


def third_party_debug_log(h: Harness) -> None:
    for name in redaction.THIRD_PARTY_LOGGERS:
        logger = logging.getLogger(name)
        for level in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR):
            logger.log(level, "request failed: %s", SECRET_TEXT)
            logger.log(level, f"preformatted {SECRET_TEXT}")
        try:
            raise secret_error()
        except RuntimeError:
            logger.exception("call raised")
    for level in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR):
        logging.getLogger("gmail_pdf.infra.test").log(level, "app log %s", SECRET_TEXT)


def chained_exception_message(h: Harness) -> None:
    try:
        try:
            raise gmail_http_error()
        except HttpError as inner:
            raise GmailPdfError(f"Gmail call failed {SECRET_TEXT}") from inner
    except GmailPdfError as outer:
        line = safe_message(outer)
        print(line, file=sys.stderr)
        print(line, file=sys.stdout)
        logging.getLogger("gmail_pdf.test").error("%s", line)
    line = safe_message(secret_error())
    print(line, file=sys.stderr)
    line = safe_message(gmail_http_error())
    print(line, file=sys.stdout)


def keyboard_interrupt(h: Harness) -> None:
    h.through_excepthook(KeyboardInterrupt(SECRET_TEXT))

    class InterruptedParser:
        def parse_args(self, argv: object = None) -> None:
            raise KeyboardInterrupt(SECRET_TEXT)

    h.monkeypatch.setattr(cli_main, "build_parser", InterruptedParser)
    cli_main.main([])


# Append later stories' paths here (see the module docstring).
ERROR_PATHS = [
    pytest.param(uncaught_exception, id="uncaught-exception"),
    pytest.param(third_party_debug_log, id="third-party-debug-log"),
    pytest.param(chained_exception_message, id="chained-exception-message"),
    pytest.param(keyboard_interrupt, id="keyboard-interrupt"),
]


@pytest.mark.parametrize("surface", SURFACES)
@pytest.mark.parametrize("path", ERROR_PATHS)
def test_no_sentinel_reaches_the_surface(
    harness: Harness, path: Callable[[Harness], None], surface: str
) -> None:
    path(harness)

    assert sentinels.leaked(harness.text(surface)) == []


@pytest.mark.parametrize("path", ERROR_PATHS)
def test_every_path_writes_something_so_the_check_is_not_vacuous(
    harness: Harness, path: Callable[[Harness], None]
) -> None:
    path(harness)

    assert any(harness.text(surface) for surface in SURFACES)


def test_the_detector_sees_a_sentinel_on_an_unprotected_surface() -> None:
    stream = io.StringIO()
    control = logging.getLogger("matrix.control")
    control.propagate = False
    handler = logging.StreamHandler(stream)
    control.addHandler(handler)
    try:
        control.warning("leak %s", sentinels.CLIENT_SECRET)
    finally:
        control.removeHandler(handler)

    assert sentinels.leaked(stream.getvalue()) == [sentinels.CLIENT_SECRET]
