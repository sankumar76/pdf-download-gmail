"""The single entry point of a run, shared by the CLI and (later) the GUI (architecture 6.1).

In this slice a run lists the candidate messages and keeps those inside the range. The request
has passed ``domain.validation`` first (the front end calls it before it builds ``Deps``, so a
rejected input reads no credential and creates nothing). Downloading, the manifest and the
report arrive with later stories. ``run`` is synchronous and thread-agnostic; it never prints
(the front end renders the summary).
"""

from __future__ import annotations

from gmail_pdf.app.planner import plan_range
from gmail_pdf.app.ports import Deps, EventSink
from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.errors import RunCancelledError
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import RunRequest, RunResult, RunSummary


def run(request: RunRequest, deps: Deps, sink: EventSink, cancel: CancelToken) -> RunSummary:
    """Select the messages in ``request``'s inclusive date range.

    Args:
        request: What the user asked for.
        deps: The port implementations.
        sink: Receives notices. This slice emits none; the parameter fixes the signature of
            architecture 6.1 so the front ends do not change when events arrive.
        cancel: Checked before every Gmail call.

    Returns:
        A ``COMPLETED`` summary with the messages in range, or a ``CANCELLED`` one.

    Raises:
        ValueError, OverflowError, ZoneInfoNotFoundError: the request did not come from
            ``domain.validation``: a programming error, not user input.
        GmailApiError: Gmail answered a call with a non-retryable HTTP error.
        RetryExhaustedError: a retryable call failed on every attempt.
        KeyError: a message resource has no ``internalDate`` (with ``ValueError`` and
            ``TypeError`` for a malformed one: issue #37, no domain error for it yet).

    ``RunCancelledError`` does not escape: it becomes the ``CANCELLED`` summary. The CLI turns
    the other failures into its one fixed unexpected-failure line.
    """
    zone = deps.resolve_zone(request.tz)
    date_range = DateRange.from_days(request.start, request.end, zone)
    try:
        messages = plan_range(deps.gmail, date_range, cancel)
    except RunCancelledError:
        return RunSummary(RunResult.CANCELLED)
    return RunSummary(RunResult.COMPLETED, messages)
