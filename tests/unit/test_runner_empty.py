"""PGD-17 AC-1, AC-2, AC-4 and AC-5 through the runner: an empty range is a normal, finished run.

"Empty" means no message in the range (extraction does not exist yet). A failed list call is the
opposite: it raises out of ``run`` and never becomes a summary, so it cannot be told as empty.
"""

from __future__ import annotations

from datetime import date

import pytest

from gmail_pdf.app.ports import Deps
from gmail_pdf.app.runner import run
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import ExitCode, MessageRef, RunRequest, RunResult, RunSummary
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_gmail import FakeGmail, FakeGmailHttpError
from tests.support.mailboxes import edge_mailbox, empty_mailbox, outside_mailbox

pytestmark = pytest.mark.req("FR-016", "EC-06")

KOLKATA = "Asia/Kolkata"  # the zone of the January range below


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[object] = []

    def emit(self, event: object) -> None:
        self.events.append(event)


def january() -> RunRequest:
    return RunRequest(date(2026, 1, 1), date(2026, 1, 31), KOLKATA)


def run_on(fake: FakeGmail, sink: RecordingSink | None = None) -> RunSummary:
    deps = Deps(gmail=fake, resolve_zone=tz_module.resolve_zone)
    return run(january(), deps, sink or RecordingSink(), CancelToken())


@pytest.mark.req("AC-1")
def test_a_search_with_no_match_completes_with_no_messages() -> None:
    summary = run_on(empty_mailbox())

    assert (summary.result, summary.messages) == (RunResult.COMPLETED, ())


@pytest.mark.req("AC-1", "AC-5")
def test_a_search_with_no_match_exits_zero() -> None:
    summary = run_on(empty_mailbox())

    assert summary.exit_code is ExitCode.OK
    assert int(summary.exit_code) == 0


@pytest.mark.req("AC-1")
def test_a_search_with_no_match_reads_no_message() -> None:
    fake = empty_mailbox()

    run_on(fake)

    assert [call.method for call in fake.calls] == ["list_message_ids"]


@pytest.mark.req("AC-2")
def test_messages_that_are_all_outside_the_range_complete_with_no_messages() -> None:
    summary = run_on(outside_mailbox())

    assert (summary.result, summary.messages) == (RunResult.COMPLETED, ())


@pytest.mark.req("AC-2", "AC-5")
def test_messages_that_are_all_outside_the_range_exit_zero() -> None:
    assert run_on(outside_mailbox()).exit_code is ExitCode.OK


@pytest.mark.req("AC-2")
def test_the_outside_messages_were_really_returned_by_the_search_and_re_checked() -> None:
    fake = outside_mailbox()

    run_on(fake)

    assert len(fake.calls_to("get_message")) == 2


@pytest.mark.req("AC-1")
def test_the_run_emits_no_notice_for_an_empty_range() -> None:
    sink = RecordingSink()

    run_on(empty_mailbox(), sink)

    assert sink.events == []


@pytest.mark.req("AC-1", "AC-2")
def test_a_completed_run_with_no_messages_is_empty() -> None:
    assert RunSummary(RunResult.COMPLETED, ()).is_empty is True


@pytest.mark.req("AC-1")
def test_a_completed_run_with_a_message_is_not_empty() -> None:
    assert RunSummary(RunResult.COMPLETED, (MessageRef("m1", 1),)).is_empty is False


@pytest.mark.req("AC-4")
def test_a_cancelled_run_is_not_empty() -> None:
    assert RunSummary(RunResult.CANCELLED).is_empty is False


@pytest.mark.req("AC-5")
def test_completed_with_no_messages_maps_to_exit_code_zero() -> None:
    assert RunSummary(RunResult.COMPLETED, ()).exit_code == 0


@pytest.mark.req("AC-5")
def test_cancelled_still_maps_to_exit_code_one() -> None:
    assert RunSummary(RunResult.CANCELLED).exit_code == 1


@pytest.mark.req("AC-4")
def test_a_failed_list_call_raises_out_of_the_run_instead_of_ending_empty() -> None:
    fake = edge_mailbox()
    fake.fail_with_http("list_message_ids", 503, times=None)

    with pytest.raises(FakeGmailHttpError):
        run_on(fake)


@pytest.mark.req("AC-4")
def test_a_failed_list_call_reads_no_message() -> None:
    fake = edge_mailbox()
    fake.fail_with_http("list_message_ids", 503, times=None)

    with pytest.raises(FakeGmailHttpError):
        run_on(fake)

    assert [call.method for call in fake.calls] == ["list_message_ids"]
