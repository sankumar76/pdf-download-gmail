"""Error types shared by every layer."""


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
