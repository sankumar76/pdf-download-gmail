"""PGD-13 AC-4: ``safe_message(exc)`` gives one safe line for any exception."""

from __future__ import annotations

import socket
from collections.abc import Callable

import httplib2
import pytest
from google.auth import exceptions as auth_exceptions
from googleapiclient.errors import HttpError

from gmail_pdf import redaction
from gmail_pdf.domain import messages
from gmail_pdf.domain.errors import AdapterUnavailableError, GmailPdfError
from gmail_pdf.redaction import MAX_CHAIN_DEPTH, MAX_MESSAGE_LENGTH, REDACTED, safe_message
from tests.support import sentinels

pytestmark = pytest.mark.req("FR-005", "NFR-012", "AC-4")

SECRET_TEXT = f"{sentinels.CLIENT_SECRET} {sentinels.REFRESH_TOKEN} {sentinels.ACCESS_TOKEN}"


@pytest.fixture(autouse=True)
def _registered_secrets() -> None:
    for value in sentinels.REGISTERED:
        redaction.register_secret(value)


def http_error(status: int = 403) -> HttpError:
    """An ``HttpError`` whose response body echoes every sentinel."""
    response = httplib2.Response({"status": status})
    response.reason = f"Forbidden {sentinels.ACCESS_TOKEN}"
    body = f'{{"error": "denied", "echo": "{SECRET_TEXT}"}}'.encode()
    return HttpError(response, body, uri=f"https://example.invalid/?access_token={SECRET_TEXT}")


def refresh_error() -> auth_exceptions.RefreshError:
    return auth_exceptions.RefreshError(f"invalid_grant {SECRET_TEXT}", {"echo": SECRET_TEXT})


class RaisingStr(Exception):
    def __str__(self) -> str:
        raise RuntimeError(SECRET_TEXT)


class RaisingStrApp(GmailPdfError):
    def __str__(self) -> str:
        raise RuntimeError(SECRET_TEXT)


def chained(outer: BaseException, inner: BaseException) -> BaseException:
    outer.__cause__ = inner
    return outer


def fail_during_cleanup() -> None:
    raise RuntimeError(f"cleanup failed {SECRET_TEXT}")


def raised_during(inner: BaseException) -> BaseException:
    """A RuntimeError raised while ``inner`` was being handled (implicit ``__context__``)."""
    with pytest.raises(RuntimeError) as caught:
        try:
            raise inner
        except BaseException:
            fail_during_cleanup()
    return caught.value


def raised_from_none(inner: BaseException) -> BaseException:
    with pytest.raises(RuntimeError) as caught:
        try:
            raise inner
        except BaseException:
            raise RuntimeError(SECRET_TEXT) from None
    return caught.value


CASES: list[tuple[str, Callable[[], BaseException], str | None]] = [
    # (id, factory, fixed line the result must equal; None = checked elsewhere)
    ("http-error", http_error, messages.GMAIL_REQUEST_ERROR_LINE),
    ("http-error-429", lambda: http_error(429), messages.GMAIL_REQUEST_ERROR_LINE),
    ("refresh-error", refresh_error, messages.SIGN_IN_ERROR_LINE),
    (
        "transport-error",
        lambda: auth_exceptions.TransportError(SECRET_TEXT),
        messages.NETWORK_ERROR_LINE,
    ),
    ("connection-error", lambda: ConnectionResetError(SECRET_TEXT), messages.NETWORK_ERROR_LINE),
    ("timeout", lambda: TimeoutError(SECRET_TEXT), messages.NETWORK_ERROR_LINE),
    ("dns-failure", lambda: socket.gaierror(11001, SECRET_TEXT), messages.NETWORK_ERROR_LINE),
    ("file-not-found", lambda: FileNotFoundError(2, SECRET_TEXT), messages.FILE_ACCESS_ERROR_LINE),
    ("permission", lambda: PermissionError(13, SECRET_TEXT), messages.FILE_ACCESS_ERROR_LINE),
    ("cancel", lambda: KeyboardInterrupt(SECRET_TEXT), messages.RUN_CANCELLED_LINE),
    ("unknown-runtime", lambda: RuntimeError(SECRET_TEXT), messages.GENERIC_ERROR_LINE),
    (
        "unknown-with-args",
        lambda: Exception(SECRET_TEXT, {"k": SECRET_TEXT}),
        messages.GENERIC_ERROR_LINE,
    ),
    ("unknown-key-error", lambda: KeyError(SECRET_TEXT), messages.GENERIC_ERROR_LINE),
    ("str-raises", RaisingStr, messages.GENERIC_ERROR_LINE),
    ("str-raises-app-error", RaisingStrApp, messages.GENERIC_ERROR_LINE),
    ("empty-app-error", GmailPdfError, messages.GENERIC_ERROR_LINE),
    (
        "cause-is-refresh-error",
        lambda: chained(RuntimeError(SECRET_TEXT), refresh_error()),
        messages.SIGN_IN_ERROR_LINE,
    ),
    (
        "cause-is-http-error",
        lambda: chained(ValueError(SECRET_TEXT), http_error()),
        messages.GMAIL_REQUEST_ERROR_LINE,
    ),
    (
        "context-is-network-error",
        lambda: raised_during(TimeoutError(SECRET_TEXT)),
        messages.NETWORK_ERROR_LINE,
    ),
    (
        "context-hidden-by-from-none",
        lambda: raised_from_none(refresh_error()),
        messages.GENERIC_ERROR_LINE,
    ),
    (
        "chain-beyond-the-depth-limit",
        lambda: deep_chain(MAX_CHAIN_DEPTH + 4),
        messages.GENERIC_ERROR_LINE,
    ),
    ("chain-cycle", lambda: cyclic_chain(), messages.GENERIC_ERROR_LINE),
]


def deep_chain(depth: int) -> BaseException:
    """``depth`` plain exceptions, then a RefreshError too far down to be reached."""
    exc: BaseException = refresh_error()
    for _ in range(depth):
        exc = chained(RuntimeError(SECRET_TEXT), exc)
    return exc


def cyclic_chain() -> BaseException:
    first, second = RuntimeError(SECRET_TEXT), ValueError(SECRET_TEXT)
    first.__cause__ = second
    second.__cause__ = first
    return first


@pytest.mark.parametrize(
    ("factory", "expected"),
    [pytest.param(factory, expected, id=case_id) for case_id, factory, expected in CASES],
)
def test_the_result_is_the_fixed_sentence_for_the_type(
    factory: Callable[[], BaseException], expected: str
) -> None:
    assert safe_message(factory()) == expected


@pytest.mark.parametrize(
    "factory", [pytest.param(factory, id=case_id) for case_id, factory, _ in CASES]
)
def test_the_result_is_one_line(factory: Callable[[], BaseException]) -> None:
    line = safe_message(factory())

    assert line.splitlines() == [line]


@pytest.mark.parametrize(
    "factory", [pytest.param(factory, id=case_id) for case_id, factory, _ in CASES]
)
def test_the_result_has_no_traceback(factory: Callable[[], BaseException]) -> None:
    assert "Traceback" not in safe_message(factory())


@pytest.mark.parametrize(
    "factory", [pytest.param(factory, id=case_id) for case_id, factory, _ in CASES]
)
def test_the_result_has_no_sentinel(factory: Callable[[], BaseException]) -> None:
    assert sentinels.leaked(safe_message(factory())) == []


# ------------------------------------------------------------- errors this application raises
def test_an_application_error_shows_its_own_message() -> None:
    line = safe_message(AdapterUnavailableError("The Gmail adapter is not available."))

    assert line == "The Gmail adapter is not available."


def test_an_application_error_message_is_redacted() -> None:
    line = safe_message(GmailPdfError(f"could not use {sentinels.CLIENT_SECRET}"))

    assert line == f"could not use {REDACTED}"


def test_an_application_error_message_is_redacted_by_pattern_too() -> None:
    line = safe_message(GmailPdfError(f"sent {sentinels.UNREGISTERED_GOCSPX}"))

    assert line == f"sent {REDACTED}"


def test_an_application_error_message_is_cut_to_one_line() -> None:
    line = safe_message(GmailPdfError("first line\nsecond\r\nthird\t\x1b[31mred\x00end"))

    assert line == "first line second third [31mred end"


def test_a_long_application_error_message_is_truncated() -> None:
    line = safe_message(GmailPdfError("word " * 200))

    assert len(line) == MAX_MESSAGE_LENGTH
    assert line.endswith("...")


def test_an_application_error_with_a_secret_split_over_two_lines_is_not_leaked() -> None:
    half = len(sentinels.CLIENT_SECRET) // 2
    split = f"{sentinels.CLIENT_SECRET[:half]}\n{sentinels.CLIENT_SECRET[half:]}"

    line = safe_message(GmailPdfError(split))

    # The registry only matches the whole value; the two halves are not the secret any more.
    assert sentinels.CLIENT_SECRET not in line


def test_an_application_error_raised_from_a_secret_bearing_error_keeps_only_its_own_text() -> None:
    try:
        try:
            raise http_error()
        except HttpError as inner:
            raise GmailPdfError("Gmail request failed.") from inner
    except GmailPdfError as outer:
        line = safe_message(outer)

    assert line == "Gmail request failed."


def test_unicode_in_an_application_error_message_is_kept() -> None:
    assert safe_message(GmailPdfError("Ordner „Größe“ nicht gefunden")) == (
        "Ordner „Größe“ nicht gefunden"
    )
