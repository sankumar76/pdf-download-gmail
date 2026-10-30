"""Error types shared by every layer."""


class GmailPdfError(Exception):
    """Base class of every error this application raises on purpose.

    Messages are written for the user and must never contain secrets (FR-005).
    """


class FakeMailboxHookRefusedError(GmailPdfError):
    """The fake-mailbox hook was requested outside a test run (``GMAIL_PDF_TESTING`` is not 1)."""


class AdapterUnavailableError(GmailPdfError):
    """The requested adapter is not wired into this build yet."""
