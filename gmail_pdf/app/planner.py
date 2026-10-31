"""Phases 1 and 2 of a run for one date range (architecture 6.3, ADR-006, FR-012).

Phase 1 lists the candidate ids with the baseline query. Phase 2 reads each message once
(``format=full``), keeps only its id and ``internalDate`` and drops the payload at once
(NFR-009), and re-checks the exact range locally: the query is widened by one second on each
side (AA-01), so it can return messages just outside the range.

This story lists the first page only; following ``nextPageToken`` is STORY-02.04, the recall
sweep is STORY-02.09. Messages are returned in the order Gmail listed them (encounter order);
the deterministic order of FR-014 is STORY-02.05.
"""

from __future__ import annotations

from gmail_pdf.app.ports import GmailPort
from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.errors import RunCancelledError
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import MessageRef
from gmail_pdf.domain.query import baseline_query


def plan_range(
    gmail: GmailPort, date_range: DateRange, cancel: CancelToken
) -> tuple[MessageRef, ...]:
    """Return the messages received inside ``date_range``.

    Args:
        gmail: The Gmail port (the gateway, or ``FakeGmail`` in tests).
        date_range: The exact range to select.
        cancel: Checked before every Gmail call.

    Raises:
        RunCancelledError: ``cancel`` was set before a call.
    """
    if cancel.is_set():
        raise RunCancelledError
    page = gmail.list_message_ids(baseline_query(date_range))
    selected: list[MessageRef] = []
    for message_id in page.message_ids:
        if cancel.is_set():
            raise RunCancelledError
        internal_date_ms = int(gmail.get_message(message_id)["internalDate"])
        if date_range.contains(internal_date_ms):
            selected.append(MessageRef(message_id, internal_date_ms))
    return tuple(selected)
