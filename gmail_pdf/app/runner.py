"""The single entry point of a run, shared by the CLI and (later) the GUI (architecture 6.1).

In this slice a run validates the range, lists the candidate messages and keeps those inside the
range. Downloading, the manifest and the report arrive with later stories. ``run`` is
synchronous and thread-agnostic; it never prints (the front end renders the summary).
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
        InputValidationError: the zone is unknown or the end day is before the start day.
    """
    zone = deps.resolve_zone(request.tz)
    date_range = DateRange.from_days(request.start, request.end, zone)
    try:
        messages = plan_range(deps.gmail, date_range, cancel)
    except RunCancelledError:
        return RunSummary(RunResult.CANCELLED)
    return RunSummary(RunResult.COMPLETED, messages)
