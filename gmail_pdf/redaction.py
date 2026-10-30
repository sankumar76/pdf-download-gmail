"""The one redaction path (FR-005, NFR-012, ADR-003 section 6, architecture section 8.4).

This is the code that turns an exception or other untrusted text into text a person can see.
It covers these surfaces: log records (a ``logging.Filter``), one-line error text
(``safe_message``), uncaught exceptions on the main and worker threads, exceptions the
interpreter ignores (``sys.unraisablehook``) and warnings routed through ``logging``. Anything
else that writes to the console on its own, such as ``argparse`` usage errors, is not covered
(tracked in issue #23). Four parts:

1. A registry of known secrets (``register_secret``): exact matches become ``[REDACTED]``.
2. Patterns for Google token shapes and key/value forms, as defence in depth (``redact``).
3. Surfaces: a ``logging.Filter`` (``RedactingFilter``, ``install_logging_redaction``),
   ``safe_message`` for one-line error text, and the ``sys.excepthook`` /
   ``threading.excepthook`` / ``sys.unraisablehook`` installers (``install_excepthooks``).
4. Structural rules for the rest of the code base (not enforceable here): never format a
   ``Credentials`` object, HTTP headers or request URIs into any message.

Import rule (PGD-13 AC-7): this module imports only the standard library and
``gmail_pdf.domain.messages`` (itself dependency-free), so ``cli.main`` can load it before
anything else exists. Third-party exception types are therefore recognised by their qualified
class name, never imported.
"""

from __future__ import annotations

import logging
import re
import sys
import threading
import traceback
from collections.abc import Callable, Iterator
from types import TracebackType
from urllib.parse import quote, quote_plus

from gmail_pdf.domain.messages import (
    FILE_ACCESS_ERROR_LINE,
    GENERIC_ERROR_LINE,
    GMAIL_REQUEST_ERROR_LINE,
    NETWORK_ERROR_LINE,
    RUN_CANCELLED_LINE,
    SIGN_IN_ERROR_LINE,
    UNEXPECTED_FAILURE_LINE,
)

__all__ = [
    "REDACTED",
    "MIN_SECRET_LENGTH",
    "RedactingFilter",
    "clear_secrets",
    "install_excepthooks",
    "install_logging_redaction",
    "redact",
    "register_secret",
    "report_cancelled",
    "report_unexpected_failure",
    "safe_message",
]

logger = logging.getLogger(__name__)

REDACTED = "[REDACTED]"
# Shorter values are ignored: they would also match ordinary words and hide useful text.
MIN_SECRET_LENGTH = 8
# One-line messages are cut here; nothing a person needs to act on is longer.
MAX_MESSAGE_LENGTH = 300
# Longest ``__cause__`` / ``__context__`` chain ``safe_message`` follows (guards cycles too).
MAX_CHAIN_DEPTH = 16
UNFORMATTABLE_LOG_MESSAGE = "<log message could not be formatted>"
THIRD_PARTY_LOGGERS = ("googleapiclient", "google_auth_oauthlib", "urllib3", "oauthlib")

# ------------------------------------------------------------------------------ registry
_registry_lock = threading.Lock()
_registered: set[str] = set()
# Longest first, so a secret that contains another one is replaced whole. Rebuilt on every
# change and swapped in as one object, so ``redact`` never needs the lock.
_replacements: tuple[str, ...] = ()


def register_secret(value: str) -> None:
    """Add a secret whose exact text must never be shown.

    Register ``client_secret``, ``refresh_token`` and the current access token whenever they
    are loaded or refreshed. The URL-encoded forms are registered too, because a token that
    reaches a query string or form body is percent-encoded (``/`` becomes ``%2F``).

    Values shorter than ``MIN_SECRET_LENGTH`` characters, and blank values, are ignored.
    Registering the same value twice is harmless.
    """
    global _replacements
    if len(value) < MIN_SECRET_LENGTH or not value.strip():
        return
    with _registry_lock:
        _registered.update({value, quote(value, safe=""), quote_plus(value)})
        _replacements = tuple(sorted(_registered, key=len, reverse=True))


def clear_secrets() -> None:
    """Forget every registered secret (sign-out, and test isolation)."""
    global _replacements
    with _registry_lock:
        _registered.clear()
        _replacements = ()


# ------------------------------------------------------------------------------ patterns
# (pattern, replacement) pairs from architecture section 8.4 / AA-10. Key names stay visible.
# Decision D-44 (architect): the bare ``code`` key must not be the tail of a longer word, so
# ``status_code: 404`` and ``zipcode=10001`` are not mistaken for an OAuth ``code=`` value; the
# OAuth ``*_code`` secrets are listed as explicit keys. A new secret parameter is added to the
# explicit list with a test row, never by loosening the ``code`` guard.
_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"ya29\.[\w.-]+"), REDACTED),
    (re.compile(r"1//[\w.-]+"), REDACTED),
    (re.compile(r"GOCSPX-[\w-]+"), REDACTED),
    (
        re.compile(
            r"""(?ix)
            ((?:access_token|refresh_token|client_secret|id_token|code_verifier|auth_code|device_code)|(?<!\w)code)
            (["']?\s*[:=]\s*["']?)
            [^"'&\s,}]+
            """
        ),
        rf"\1\2{REDACTED}",
    ),
    (re.compile(r"(?i)(authorization:\s*bearer\s+)\S+"), rf"\1{REDACTED}"),
)


def redact(text: str) -> str:
    """Return ``text`` with every registered secret and every known token shape replaced.

    The result is the same text with ``[REDACTED]`` in place of the secret part; key names
    (``access_token`` ...) stay. Running ``redact`` on its own output changes nothing.
    """
    for secret in _replacements:
        text = text.replace(secret, REDACTED)
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


# ------------------------------------------------------------------------------ logging
class RedactingFilter(logging.Filter):
    """Redacts the message, the exception text and the stack text of every record it sees.

    Attach it to a handler (a filter on a logger does not see records from child loggers).
    It never drops a record. Only the message, ``args``, exception and stack text are
    sanitised; values passed through ``extra=`` are left alone, so do not put secrets there.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # a broken __str__ or format must not leak or crash
            message = UNFORMATTABLE_LOG_MESSAGE
        record.msg = redact(message)
        record.args = None
        if record.exc_info:
            # exc_text is what Formatter prints; clearing exc_info stops a handler without
            # this filter from formatting the unredacted traceback again.
            text = "".join(traceback.format_exception(*record.exc_info)).rstrip("\n")
            record.exc_text = redact(text)
            record.exc_info = None
        elif record.exc_text:
            record.exc_text = redact(record.exc_text)
        if record.stack_info:
            record.stack_info = redact(record.stack_info)
        return True


def _attach_filter(handler: logging.Handler) -> None:
    if not any(isinstance(existing, RedactingFilter) for existing in handler.filters):
        handler.addFilter(RedactingFilter())


def install_logging_redaction(*handlers: logging.Handler) -> None:
    """Put the redaction filter on ``handlers`` and cap the noisy third-party loggers.

    * Every handler passed in gets a ``RedactingFilter`` (once). ``logging.lastResort``, the
      stderr handler Python uses when nothing is configured, gets one too. A handler created
      later is not covered until it is passed to this function.
    * ``googleapiclient``, ``google_auth_oauthlib``, ``urllib3`` and ``oauthlib`` are capped at
      WARNING (a level that is already stricter is kept).
    * ``logging.captureWarnings(True)``: ``warnings.warn`` text goes to the ``py.warnings``
      logger, so the filtered handlers see it instead of ``warnings`` writing raw text to
      stderr.
    * If ``httplib2`` has already been imported its ``debuglevel`` is set to 0 (it prints
      requests and headers to stdout otherwise). A later import starts at 0 by default.

    The function may be called any number of times, with no handlers at all.
    """
    for handler in handlers:
        _attach_filter(handler)
    if logging.lastResort is not None:
        _attach_filter(logging.lastResort)
    logging.captureWarnings(True)
    for name in THIRD_PARTY_LOGGERS:
        third_party = logging.getLogger(name)
        if third_party.level < logging.WARNING:  # includes NOTSET (0)
            third_party.setLevel(logging.WARNING)
    httplib2 = sys.modules.get("httplib2")
    if httplib2 is not None:
        # Written through the module namespace: the module is only known by name here, so
        # the type checker (rightly) cannot see the attribute.
        vars(httplib2)["debuglevel"] = 0


# ------------------------------------------------------------------------------ safe_message
# Recognised by qualified class name so no third-party module is imported (see module docs).
# The first row whose names meet an exception's class hierarchy wins, so the specific rows
# (network, sign-in, Gmail) come before ``OSError``, which is their base class in places.
_GMAIL_PDF_ERROR = "gmail_pdf.domain.errors.GmailPdfError"
_HINTS: tuple[tuple[frozenset[str], str], ...] = (
    (frozenset({"builtins.KeyboardInterrupt"}), RUN_CANCELLED_LINE),
    (
        frozenset(
            {
                "builtins.ConnectionError",
                "builtins.TimeoutError",
                "socket.gaierror",
                "ssl.SSLError",
                "google.auth.exceptions.TransportError",
                "httplib2.HttpLib2Error",
                "httplib2.error.HttpLib2Error",
            }
        ),
        NETWORK_ERROR_LINE,
    ),
    (
        frozenset(
            {
                "google.auth.exceptions.GoogleAuthError",
                "oauthlib.oauth2.rfc6749.errors.OAuth2Error",
            }
        ),
        SIGN_IN_ERROR_LINE,
    ),
    (frozenset({"googleapiclient.errors.HttpError"}), GMAIL_REQUEST_ERROR_LINE),
    (frozenset({"builtins.OSError"}), FILE_ACCESS_ERROR_LINE),
)


def _qualified_names(exc: BaseException) -> frozenset[str]:
    return frozenset(f"{cls.__module__}.{cls.__qualname__}" for cls in type(exc).__mro__)


def _chain(exc: BaseException) -> Iterator[BaseException]:
    """``exc`` and the exceptions it was raised from or during, nearest first (bounded)."""
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen and len(seen) < MAX_CHAIN_DEPTH:
        seen.add(id(current))
        yield current
        if current.__cause__ is not None:
            current = current.__cause__
        elif not current.__suppress_context__:
            current = current.__context__
        else:
            current = None


def _hint_for(exc: BaseException) -> str | None:
    names = _qualified_names(exc)
    for hint_names, hint in _HINTS:
        if names & hint_names:
            return hint
    return None


def _one_line(text: str) -> str:
    """Collapse every run of whitespace and control characters into a single space."""
    cleaned = "".join(ch if ch.isprintable() else " " for ch in text)
    line = " ".join(cleaned.split())
    if len(line) > MAX_MESSAGE_LENGTH:
        line = line[: MAX_MESSAGE_LENGTH - 3] + "..."
    return line


def _own_message(exc: BaseException) -> str:
    """The text of an error this application raised on purpose; empty if it cannot be read."""
    try:
        return str(exc)
    except Exception:  # a user-defined __str__ may raise anything
        return ""


def safe_message(exc: BaseException) -> str:
    """Return one displayable line for ``exc``: no newline, no traceback, no registered secret
    or known token shape.

    * An error this application raises on purpose (``GmailPdfError``) shows its own message,
      redacted: those messages are written for the user.
    * Any other exception shows a fixed sentence chosen by its type, or by the type of the
      exception it was raised from or during, with an action hint (network, sign-in, Gmail
      request, file access, cancel). Its own message, arguments and chain text are never used.
    * An unknown type gives ``GENERIC_ERROR_LINE``.
    """
    if _GMAIL_PDF_ERROR in _qualified_names(exc):
        line = _one_line(redact(_own_message(exc)))
        if line:
            return line
    for link in _chain(exc):
        hint = _hint_for(link)
        if hint is not None:
            return hint
    return GENERIC_ERROR_LINE


# ------------------------------------------------------------------------------ excepthooks
def _write_stderr(line: str) -> None:
    stream = sys.stderr
    if stream is None:  # pythonw, or a closed standard stream: there is nowhere to write
        return
    try:
        stream.write(redact(line) + "\n")
        stream.flush()
    except (OSError, ValueError):
        # stderr is gone (closed pipe); this is the handler of last resort, so there is no
        # better surface to report it on.
        return


def report_cancelled() -> None:
    """Print the one-line cancel notice (``Run cancelled``) to stderr (AC-8)."""
    _write_stderr(RUN_CANCELLED_LINE)


def report_unexpected_failure(
    exc_type: type[BaseException],
    exc_value: BaseException | None,
    exc_traceback: TracebackType | None,
) -> None:
    """Print the unexpected-failure line to stderr; send the redacted traceback to DEBUG.

    The traceback is redacted here, before it reaches the logger, so it is safe even if a
    handler has no ``RedactingFilter``. Nothing but the one fixed line reaches stderr (AC-5).
    """
    _write_stderr(UNEXPECTED_FAILURE_LINE)
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.debug("Unexpected failure (redacted traceback):\n%s", redact(text))


def _handle_uncaught(
    exc_type: type[BaseException],
    exc_value: BaseException | None,
    exc_traceback: TracebackType | None,
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        report_cancelled()
    else:
        report_unexpected_failure(exc_type, exc_value, exc_traceback)


def _main_thread_hook(
    exc_type: type[BaseException], exc_value: BaseException, exc_traceback: TracebackType | None
) -> None:
    _handle_uncaught(exc_type, exc_value, exc_traceback)


def _worker_thread_hook(args: threading.ExceptHookArgs) -> None:
    if args.exc_type is SystemExit:  # threading ignores it by default; keep that behaviour
        return
    _handle_uncaught(args.exc_type, args.exc_value, args.exc_traceback)


def _unraisable_hook(args: sys.UnraisableHookArgs) -> None:
    """Exceptions the interpreter must ignore (``__del__``, callbacks): redacted, DEBUG only."""
    text = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
    logger.debug("Ignored exception (redacted traceback):\n%s", redact(text))


def install_excepthooks() -> Callable[[], None]:
    """Replace ``sys.excepthook``, ``threading.excepthook`` and ``sys.unraisablehook``.

    An uncaught exception on any thread then prints ``error: unexpected failure, see the run
    log`` (or ``Run cancelled`` for Ctrl+C) to stderr, and nothing else. An exception the
    interpreter ignores (for example in ``__del__``) prints nothing; its redacted traceback goes
    to the logger at DEBUG. The hooks do not call the previous hooks.

    Returns:
        A function that puts back the hooks that were installed before this call.
    """
    previous_main = sys.excepthook
    previous_thread = threading.excepthook
    previous_unraisable = sys.unraisablehook
    sys.excepthook = _main_thread_hook
    threading.excepthook = _worker_thread_hook
    sys.unraisablehook = _unraisable_hook

    def restore() -> None:
        sys.excepthook = previous_main
        threading.excepthook = previous_thread
        sys.unraisablehook = previous_unraisable

    return restore
