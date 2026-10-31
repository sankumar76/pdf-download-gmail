"""PGD-15 AC-1, AC-3 and AC-10 through the runner: request in, summary out, no output of its own."""

from __future__ import annotations

from datetime import date
from zoneinfo import ZoneInfoNotFoundError

import pytest

from gmail_pdf.app.ports import Deps
from gmail_pdf.app.runner import run
from gmail_pdf.domain import events
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import ExitCode, RunRequest, RunResult
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_gmail import FakeGmail
from tests.fixtures.builders import MessageBuilder, build_messages

pytestmark = pytest.mark.req("FR-008", "FR-012", "AC-1")


class RecordingSink:
    def __init__(self) -> None:
        self.events: list[events.Warning] = []

    def emit(self, event: events.Warning) -> None:
        self.events.append(event)


def january_request(tz: str | None = "Asia/Kolkata") -> RunRequest:
    return RunRequest(date(2026, 1, 1), date(2026, 1, 31), tz)


def mailbox() -> FakeGmail:
    builders = [
        MessageBuilder("in-first").received("2026-01-01T00:00:00", "Asia/Kolkata"),
        MessageBuilder("in-last").received("2026-01-31T23:59:59", "Asia/Kolkata"),
        MessageBuilder("out-after").received("2026-02-01T00:00:00", "Asia/Kolkata"),
        MessageBuilder("out-before").received("2025-12-31T23:59:59", "Asia/Kolkata"),
    ]
    return FakeGmail(build_messages(b.pdf("a.pdf") for b in builders))


def deps_for(fake: FakeGmail) -> Deps:
    return Deps(gmail=fake, resolve_zone=tz_module.resolve_zone)


def test_the_summary_lists_the_messages_in_the_range_and_exits_zero() -> None:
    summary = run(january_request(), deps_for(mailbox()), RecordingSink(), CancelToken())

    assert summary.result is RunResult.COMPLETED
    assert sorted(ref.message_id for ref in summary.messages) == ["in-first", "in-last"]
    assert summary.exit_code is ExitCode.OK


def test_the_run_emits_no_event_in_this_slice() -> None:
    sink = RecordingSink()

    run(january_request(), deps_for(mailbox()), sink, CancelToken())

    assert sink.events == []


@pytest.mark.req("AC-10")
@pytest.mark.parametrize(
    ("system_zone", "expected"),
    [
        pytest.param("Asia/Kolkata", ["in-first", "in-last"], id="kolkata"),
        # 2026-01-01 00:00 IST is 2025-12-31 13:30 in New York (out); 2026-02-01 00:00 IST is
        # 2026-01-31 13:30 in New York (in).
        pytest.param("America/New_York", ["in-last", "out-after"], id="new-york"),
    ],
)
def test_without_tz_the_system_zone_decides_which_messages_are_in(
    monkeypatch: pytest.MonkeyPatch, system_zone: str, expected: list[str]
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lambda: system_zone)

    summary = run(january_request(None), deps_for(mailbox()), RecordingSink(), CancelToken())

    assert sorted(ref.message_id for ref in summary.messages) == expected


def test_only_the_two_read_methods_are_called() -> None:
    fake = mailbox()

    run(january_request(), deps_for(fake), RecordingSink(), CancelToken())

    assert {call.method for call in fake.calls} == {"list_message_ids", "get_message"}


@pytest.mark.req("AC-9")
@pytest.mark.parametrize(
    ("request_", "error"),
    [
        pytest.param(january_request("Mars/Olympus"), ZoneInfoNotFoundError, id="unknown-zone"),
        pytest.param(
            RunRequest(date(2026, 2, 1), date(2026, 1, 31), "UTC"),
            ValueError,
            id="end-before-start",
        ),
        pytest.param(
            RunRequest(date(1970, 1, 1), date(2026, 1, 31), "UTC"),
            ValueError,
            id="before-the-floor",
        ),
    ],
)
def test_a_request_that_was_not_validated_is_refused_before_any_gmail_call(
    request_: RunRequest, error: type[Exception]
) -> None:
    # ``domain.validation`` turns these into sentences first; the runner is the second line.
    fake = mailbox()

    with pytest.raises(error):
        run(request_, deps_for(fake), RecordingSink(), CancelToken())

    assert fake.calls == []


def test_a_cancelled_run_returns_a_cancelled_summary_with_exit_code_one() -> None:
    token = CancelToken()
    token.set()

    summary = run(january_request(), deps_for(mailbox()), RecordingSink(), token)

    assert (summary.result, summary.messages, summary.exit_code) == (
        RunResult.CANCELLED,
        (),
        ExitCode.FAILURE,
    )


def test_the_exit_codes_are_the_closed_set_zero_to_three() -> None:
    assert [(code.name, int(code)) for code in ExitCode] == [
        ("OK", 0),
        ("FAILURE", 1),
        ("USAGE", 2),
        ("AUTH_FAILED", 3),
    ]
