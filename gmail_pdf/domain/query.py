"""Gmail search queries (FR-009, architecture 6.2).

Gmail reads a calendar date in ``after:``/``before:`` as Pacific time, so the query uses epoch
seconds. Whether Gmail treats an epoch bound as inclusive or exclusive is not documented (AA-01),
so the bounds are widened by one second on each side; the exact range is then enforced locally
with ``DateRange.contains`` (FR-012). The recall sweep query is STORY-02.09.
"""

from __future__ import annotations

from gmail_pdf.domain.daterange import DateRange

BASELINE_TERMS = "has:attachment filename:pdf"
# AA-01: widening that makes the query a superset under either reading of the epoch bounds.
WIDEN_SECONDS = 1


def baseline_query(date_range: DateRange, user_query: str = "") -> str:
    """The baseline candidate search: PDF attachments inside the widened range.

    Args:
        date_range: The range to search.
        user_query: Extra Gmail search text from ``--query`` (STORY-02.07), appended as given.

    Returns:
        ``has:attachment filename:pdf after:<S-1> before:<E+1>``, then a space and the user text
        only when that text is not blank (no trailing space otherwise).
    """
    query = (
        f"{BASELINE_TERMS} "
        f"after:{date_range.start_epoch_s - WIDEN_SECONDS} "
        f"before:{date_range.end_epoch_s + WIDEN_SECONDS}"
    )
    extra = user_query.strip()
    return f"{query} {extra}" if extra else query
