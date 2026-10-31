"""User-facing sentences shared by every front end (architecture section 4.1, FR-064).

This module is dependency-free (it imports nothing), so ``gmail_pdf.redaction`` can import it
and still load before any other part of the package (PGD-13 AC-7, assumption A-2). It holds
fixed text only: no sentence here is ever built from an exception message, a token or any
other untrusted value.
"""

from __future__ import annotations

# First lines of the two outcomes that end a run abnormally (UX section 12, decision D-21).
# The unexpected-failure line has no ": <path>" suffix because no run log exists yet
# (assumption A-1, accepted by the product owner; the log arrives with STORY-07.02).
UNEXPECTED_FAILURE_LINE = "error: unexpected failure, see the run log"
RUN_CANCELLED_LINE = "Run cancelled"

# ``safe_message`` sentences. Each is one line and ends with an action the user can take.
GENERIC_ERROR_LINE = "error: the operation failed. See the run log for details."
NETWORK_ERROR_LINE = "error: the network connection failed. Check your connection and try again."
GMAIL_REQUEST_ERROR_LINE = (
    "error: Gmail rejected the request. Check your access and try the same range again."
)
SIGN_IN_ERROR_LINE = "error: Gmail sign-in failed or has expired. Sign in again."
FILE_ACCESS_ERROR_LINE = (
    "error: a file or folder could not be used. Check the path and its permissions."
)

# Interim run output (PGD-15 A-5): both lines are placeholders. STORY-07.04 replaces the count
# line with the FR-042 summary and STORY-01.04/01.06 replace the sign-in line.
MESSAGES_IN_RANGE_TEMPLATE = "Messages in range: {count}"
SIGN_IN_UNAVAILABLE_LINE = "error: Gmail sign-in is not available in this build yet."

# Test-hook failures at the command line (PGD-15 AC-6, decision on test-plan OQ-1). Test-only
# wording that reuses the PGD-12 sentences; not part of the UX first-line table. None of them
# carries a path, file content or exception text.
FAKE_MAILBOX_HOOK_REFUSED_LINE = (
    "error: GMAIL_PDF_TEST_FAKE_MAILBOX is a test-only setting and needs GMAIL_PDF_TESTING=1."
)
FAKE_MAILBOX_UNREADABLE_LINE = (
    "error: The fake mailbox file could not be read; check GMAIL_PDF_TEST_FAKE_MAILBOX."
)
FAKE_MAILBOX_NOT_IMPORTABLE_LINE = (
    "error: The fake mailbox is only available from a source checkout (tests/ not importable)."
)

# Interim input rejections (PGD-15). The wording of the rejections is STORY-02.03's; these keep
# a bad date or zone from being reported as an unexpected failure. They never echo the input.
DATE_FORMAT_TEMPLATE = "{flag} must be a date written as YYYY-MM-DD."
DATES_REQUIRED_TOGETHER = "--start and --end must be given together."
END_BEFORE_START = "The end date must not be before the start date."
DATE_OUT_OF_RANGE = "The dates are outside the range this program can handle."
ZONE_UNKNOWN = "The time zone is not a known IANA zone name, for example Asia/Kolkata."
SYSTEM_ZONE_UNAVAILABLE = "The system time zone could not be determined; give one with --tz."

# Gateway and retry (PGD-15 AC-7): fixed sentences, no URL, query or response text.
GMAIL_HTTP_ERROR_TEMPLATE = "Gmail answered the request with HTTP {status}."
RETRY_EXHAUSTED_TEMPLATE = "Gmail could not be reached after {attempts} attempts."
