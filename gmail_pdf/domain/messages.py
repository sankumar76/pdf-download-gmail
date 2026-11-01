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

# The two stdout lines of a run that finds nothing (UX section 12, PGD-17 AC-1). The first line
# is the outcome heading, the second the count. Today "nothing" means no message in the range;
# STORY-03.02 and STORY-07.04 keep the same wording for "messages found, no PDF candidate".
NO_PDFS_FOUND = "No PDFs found"
ZERO_PDFS_LINE = "0 PDFs found."

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

# Input validation (STORY-02.03, FR-015, FR-064): the one table the command line and the window
# share. No sentence echoes raw input; ``RANGE_REVERSED_TEMPLATE`` prints the two parsed dates
# (AC-2). ``{field}`` and the ``*_field`` places take the name the front end gives the input (the
# CLI passes its ``FLAG_*`` constants from ``cli/args.py``), so no flag name is written in this
# module (STD-55). The bounds in ``DATE_OUT_OF_BOUNDS_TEMPLATE`` come from
# ``domain/validation.py``.
DATE_NOT_ISO_TEMPLATE = "{field}: Enter the date as YYYY-MM-DD, for example 2026-01-31."
DATE_OUT_OF_BOUNDS_TEMPLATE = "{field}: Enter a date from {earliest} to {latest}."
RANGE_REVERSED_TEMPLATE = (
    "Start date must be on or before the end date. ({start_field} {start} {end_field} {end})"
)
ZONE_NOT_IANA_TEMPLATE = "{field}: Unknown time zone. Use an IANA name such as Asia/Kolkata."
END_IN_FUTURE_WARNING = "End date is in the future. Only mail received so far is included."

# Gateway and retry (PGD-15 AC-7): fixed sentences, no URL, query or response text.
GMAIL_HTTP_ERROR_TEMPLATE = "Gmail answered the request with HTTP {status}."
RETRY_EXHAUSTED_TEMPLATE = "Gmail could not be reached after {attempts} attempts."
