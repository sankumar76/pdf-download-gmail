"""User-facing sentences shared by every front end (architecture section 4.1, FR-064).

This module is dependency-free (standard library only, and it imports nothing at all today) so
``gmail_pdf.redaction`` can import it and still load before any other part of the package
(PGD-13 AC-7, assumption A-2). It holds fixed text only: no sentence here is ever built from an
exception message, a token or any other untrusted value.
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
