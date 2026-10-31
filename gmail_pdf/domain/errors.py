"""Error types shared by every layer."""

from __future__ import annotations

from gmail_pdf.domain import messages


class GmailPdfError(Exception):
    """Base class of every error this application raises on purpose.

    Messages are written for the user and must never contain secrets (FR-005).
    """


class FakeMailboxHookRefusedError(GmailPdfError):
    """The fake-mailbox hook was requested outside a test run (``GMAIL_PDF_TESTING`` is not 1)."""


class AdapterUnavailableError(GmailPdfError):
    """The requested adapter is not wired into this build yet."""


class FakeMailboxUnavailableError(AdapterUnavailableError):
    """The test-only fake mailbox was requested correctly but its file cannot be used.

    A missing, unreadable or malformed file. Never a fall-back to the real adapter: the CLI
    treats it as final (PGD-15 AC-6 (iii)). The message never contains the path.
    """


class FakeMailboxNotImportableError(FakeMailboxUnavailableError):
    """The fake mailbox lives in ``tests/``, which is not importable (installed wheel)."""


class PrivateFileError(GmailPdfError):
    """A private (secret-bearing) folder or file could not be created or written.

    The message names the operation only: never the file content and never a path taken from
    the operating-system error text.
    """


class InputValidationError(GmailPdfError):
    """A value the user gave (date, zone) is not usable. The CLI reports it with exit code 2.

    The message is a fixed sentence and never echoes the rejected input.
    """


class RunCancelledError(GmailPdfError):
    """The run was cancelled (``CancelToken`` set) before or between Gmail calls."""

    def __init__(self) -> None:
        super().__init__(messages.RUN_CANCELLED_LINE)


class GmailApiError(GmailPdfError):
    """Gmail answered a request with an HTTP error status.

    Built at the gateway boundary from the library's error, so nothing above it depends on
    ``googleapiclient``. Only the status, the short reason token (for example
    ``rateLimitExceeded``) and the raw ``Retry-After`` header value are kept; the response body,
    the URL and the headers are dropped because they can carry a query or a secret. The
    gateway raises it outside the handler of the library's error, so that error is not
    attached either (``__cause__`` and ``__context__`` are ``None``).

    Attributes:
        status: HTTP status code.
        reason: Gmail's error reason token, or an empty string.
        retry_after: The ``Retry-After`` header value (seconds or an HTTP date), if any.
    """

    def __init__(self, status: int, reason: str = "", retry_after: str | None = None) -> None:
        super().__init__(messages.GMAIL_HTTP_ERROR_TEMPLATE.format(status=status))
        self.status = status
        self.reason = reason
        self.retry_after = retry_after


class RetryExhaustedError(GmailPdfError):
    """Every attempt of a retryable Gmail call failed. The last failure is the ``__cause__``."""

    def __init__(self, attempts: int) -> None:
        super().__init__(messages.RETRY_EXHAUSTED_TEMPLATE.format(attempts=attempts))
        self.attempts = attempts
