"""PGD-13 AC-6: the sentinel-secret matrix (NFR-012, AC-07, test-strategy section 6).

Every *error path* is forced with sentinel secrets in its messages, arguments and cause chain,
then every *text surface* is read back and must hold 0 sentinel occurrences.

Rule for later stories ("AC in every story that adds a text surface"):

* a new error path: write ``def my_path(harness: Harness) -> None`` that provokes it through the
  real code, and append ``pytest.param(my_path, id="...")`` to ``ERROR_PATHS``;
* a new text surface (CSV writer, manifest, GUI text ...): add a branch to ``Harness.text`` and
  its name to ``SURFACES``.

Each addition is then checked against every existing surface or path with no other change.

How the surfaces are observed: ``Harness.run`` redirects ``sys.stdout`` and ``sys.stderr``
*inside the test body*. Patching them in a fixture does not work, because pytest's own capture
puts its streams back for the call phase. Paths that pytest itself intercepts (an exception
ignored by the interpreter, a library warning) or that end the process (an uncaught exception
whose hook meets a failure) run in a child interpreter, whose output is appended to the same
surfaces. The CLI is exercised in-process;
``tests/e2e/test_redaction_subprocess.py`` repeats the hook paths in a child interpreter.
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
from tests.support.subprocess_env import REPO_ROOT, run_guarded

pytestmark = pytest.mark.req("FR-005", "NFR-012", "AC-6")

SURFACES = ("stdout", "stderr", "log_file", "excepthook_output")
SECRET_TEXT = " ".join(sentinels.ALL)
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

# What a child interpreter does first, in the order the application does it: registry, logging
# redaction (with a log-file handler appended to the harness log), then the excepthooks.
CHILD_PREAMBLE = """\
import gc
import logging
import warnings

from gmail_pdf import redaction
from tests.support import sentinels

SECRET_TEXT = " ".join(sentinels.ALL)
for value in sentinels.REGISTERED:
    redaction.register_secret(value)
handler = logging.FileHandler({log_path!r}, encoding="utf-8")
handler.setLevel(logging.DEBUG)
redaction.install_logging_redaction(handler)
redaction.install_excepthooks()
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().addHandler(handler)
"""


class Harness:
    """The text surfaces of one test run, and helpers that provoke error paths through them."""

    def __init__(self, log_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.monkeypatch = monkeypatch
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.hook_output = io.StringIO()
        self.log_path = log_path
        self.handler = logging.FileHandler(log_path, encoding="utf-8")

    def run(self, path: Callable[[Harness], None]) -> None:
        """Run an error path with stdout and stderr captured for the duration of the call."""
        with contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            path(self)

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

    def in_child_interpreter(self, body: str, expected_returncode: int = 0) -> None:
        """Run ``body`` after the application's start-up in a fresh interpreter.

        Its stdout and stderr are appended to this harness's surfaces; its log records go to
        the same log file. ``expected_returncode`` is 1 for a body that ends in an uncaught
        exception.
        """
        code = CHILD_PREAMBLE.format(log_path=str(self.log_path)) + body
        result = run_guarded([sys.executable, "-c", code], REPO_ROOT)
        assert result.returncode == expected_returncode, (
            f"child interpreter ended with {result.returncode}: {result.stderr[-800:]}"
        )
        self.stdout.write(result.stdout)
        self.stderr.write(result.stderr)


@pytest.fixture
def harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Harness]:
    """Redaction installed the way the application does it, with every surface captured."""
    for value in sentinels.REGISTERED:
        redaction.register_secret(value)
    h = Harness(tmp_path / "run.log", monkeypatch)
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


def unraisable_exception(h: Harness) -> None:
    """An exception in ``__del__``: the interpreter ignores it and prints it to stderr."""
    h.in_child_interpreter(
        "class Leaky:\n"
        "    def __del__(self):\n"
        "        raise RuntimeError(SECRET_TEXT)\n"
        "Leaky()\n"
        "gc.collect()\n"
    )


def library_warning(h: Harness) -> None:
    """A library warning whose text carries a secret: ``warnings`` prints it to stderr."""
    h.in_child_interpreter("warnings.warn(SECRET_TEXT)\n")


def hook_failure(h: Harness) -> None:
    """Hooks that meet an exception whose traceback cannot be formatted (QUA-27).

    ``Hostile.__cause__`` raises a sentinel, so ``traceback.format_exception`` fails inside each
    hook: for an exception ignored in ``__del__``, for an uncaught exception in a worker thread,
    and for the uncaught exception that ends the process (exit code 1). A hook that lets that
    failure escape makes CPython print the original exception, unredacted.
    """
    h.in_child_interpreter(
        "import threading\n"
        "class Hostile(Exception):\n"
        "    @property\n"
        "    def __cause__(self):\n"
        "        raise ValueError(SECRET_TEXT)\n"
        "class Leaky:\n"
        "    def __del__(self):\n"
        "        raise Hostile(SECRET_TEXT)\n"
        "Leaky()\n"
        "gc.collect()\n"
        "def fail():\n"
        "    raise Hostile(SECRET_TEXT)\n"
        "worker = threading.Thread(target=fail)\n"
        "worker.start()\n"
        "worker.join()\n"
        "raise Hostile(SECRET_TEXT)\n",
        expected_returncode=1,
    )


# Append later stories' paths here (see the module docstring).
ERROR_PATHS = [
    pytest.param(uncaught_exception, id="uncaught-exception"),
    pytest.param(third_party_debug_log, id="third-party-debug-log"),
    pytest.param(chained_exception_message, id="chained-exception-message"),
    pytest.param(keyboard_interrupt, id="keyboard-interrupt"),
    pytest.param(unraisable_exception, id="unraisable-exception"),
    pytest.param(library_warning, id="library-warning"),
    pytest.param(hook_failure, id="hook-failure"),
]


@pytest.mark.parametrize("surface", SURFACES)
@pytest.mark.parametrize("path", ERROR_PATHS)
def test_no_sentinel_reaches_the_surface(
    harness: Harness, path: Callable[[Harness], None], surface: str
) -> None:
    harness.run(path)

    assert sentinels.leaked(harness.text(surface)) == []


@pytest.mark.parametrize("surface", SURFACES)
def test_every_surface_receives_text_from_at_least_one_path(harness: Harness, surface: str) -> None:
    """Guards against a surface that is never observed (QUA-22): it must not stay empty."""
    for path in ERROR_PATHS:
        harness.run(path.values[0])

    assert harness.text(surface) != ""


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
