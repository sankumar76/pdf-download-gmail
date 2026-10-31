"""PGD-15 AC-2 and AC-3: the planner selects exactly the messages inside the range.

The fake search is run with both readings of the epoch bounds (inclusive and exclusive, AA-01),
so the test shows that the one-second widening plus the local ``internalDate`` re-check gives the
same answer either way. Every Google-touching assertion goes through the call recorder.
"""

from __future__ import annotations

from datetime import date
from zoneinfo import ZoneInfo

import pytest

from gmail_pdf.app.planner import plan_range
from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.errors import RunCancelledError
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import MessageRef
from gmail_pdf.domain.query import baseline_query
from tests.fakes.fake_gmail import EpochBounds, FakeGmail
from tests.fixtures.builders import MessageBuilder, build_messages, epoch_ms
from tests.fixtures.canonical import NEW_YORK, RangeCase, boundary_cases, dst_cases

pytestmark = pytest.mark.req("FR-012", "AC-2", "AC-3")

KOLKATA = "Asia/Kolkata"
BOTH_READINGS = [
    pytest.param(EpochBounds.INCLUSIVE, id="inclusive"),
    pytest.param(EpochBounds.EXCLUSIVE, id="exclusive"),
]


def january_in_kolkata() -> DateRange:
    return DateRange.from_days(date(2026, 1, 1), date(2026, 1, 31), ZoneInfo(KOLKATA))


def edge_mailbox(bounds: EpochBounds) -> FakeGmail:
    """The four messages of AC-2, received at Kolkata wall-clock times."""
    builders = [
        MessageBuilder("first-second").received("2026-01-01T00:00:00", KOLKATA),
        MessageBuilder("last-second").received("2026-01-31T23:59:59", KOLKATA),
        MessageBuilder("next-midnight").received("2026-02-01T00:00:00", KOLKATA),
        MessageBuilder("second-before").received("2025-12-31T23:59:59", KOLKATA),
    ]
    return FakeGmail(build_messages(b.pdf("Edge.pdf") for b in builders), epoch_bounds=bounds)


def ids(refs: tuple[MessageRef, ...]) -> list[str]:
    return [ref.message_id for ref in refs]


# ----------------------------------------------------------------------------------- AC-2
@pytest.mark.req("AC-2")
@pytest.mark.parametrize("bounds", BOTH_READINGS)
def test_only_the_messages_inside_the_range_are_selected(bounds: EpochBounds) -> None:
    fake = edge_mailbox(bounds)

    refs = plan_range(fake, january_in_kolkata(), CancelToken())

    assert sorted(ids(refs)) == ["first-second", "last-second"]


@pytest.mark.req("AC-2")
@pytest.mark.parametrize("bounds", BOTH_READINGS)
def test_the_search_returns_edge_messages_that_the_local_check_then_drops(
    bounds: EpochBounds,
) -> None:
    fake = edge_mailbox(bounds)
    date_range = january_in_kolkata()

    listed = fake.list_message_ids(baseline_query(date_range)).message_ids
    selected = plan_range(fake, date_range, CancelToken())

    # Under either reading the widened query returns at least one message outside the range
    # (the one at E for sure), so the local re-check is what removes it.
    assert "next-midnight" in listed
    assert "next-midnight" not in ids(selected)
    assert set(ids(selected)) <= set(listed)


@pytest.mark.req("AC-2")
def test_selected_messages_carry_their_internal_date_in_milliseconds() -> None:
    fake = edge_mailbox(EpochBounds.INCLUSIVE)

    refs = {ref.message_id: ref for ref in plan_range(fake, january_in_kolkata(), CancelToken())}

    assert refs["first-second"].internal_date_ms == epoch_ms("2026-01-01T00:00:00", KOLKATA)
    assert refs["last-second"].internal_date_ms == epoch_ms("2026-01-31T23:59:59", KOLKATA)


def test_an_empty_mailbox_selects_nothing() -> None:
    assert plan_range(FakeGmail(), january_in_kolkata(), CancelToken()) == ()


@pytest.mark.req("AC-2")
def test_messages_are_returned_in_the_order_gmail_listed_them() -> None:
    builders = [
        MessageBuilder(f"m{n}").received(f"2026-01-{n:02d}T12:00:00", KOLKATA).pdf("a.pdf")
        for n in range(1, 8)
    ]
    fake = FakeGmail(build_messages(builders), shuffle_seed=11)
    date_range = january_in_kolkata()
    listing_order = list(fake.list_message_ids(baseline_query(date_range)).message_ids)
    fake_again = FakeGmail(build_messages(builders), shuffle_seed=11)

    # An identically seeded fake lists in the same order; the planner must not re-sort.
    assert ids(plan_range(fake_again, date_range, CancelToken())) == listing_order


# ----------------------------------------------------------------------------------- AC-3
def _case_id(case: RangeCase) -> str:
    return f"{case.day}-{case.label}"


@pytest.mark.req("AC-3")
@pytest.mark.parametrize("bounds", BOTH_READINGS)
@pytest.mark.parametrize("case", [*boundary_cases(), *dst_cases()], ids=_case_id)
def test_edge_messages_of_ordinary_and_dst_days_are_in_or_out_by_calendar_day(
    case: RangeCase, bounds: EpochBounds
) -> None:
    fake = FakeGmail([case.message], epoch_bounds=bounds)
    day = date.fromisoformat(case.day)
    date_range = DateRange.from_days(day, day, ZoneInfo(case.tz))

    refs = plan_range(fake, date_range, CancelToken())

    assert (ids(refs) == [case.message.message_id]) is case.in_range


@pytest.mark.req("AC-3")
@pytest.mark.parametrize("bounds", BOTH_READINGS)
def test_a_range_spanning_both_dst_changes_keeps_every_day_whole(bounds: EpochBounds) -> None:
    builders = [
        MessageBuilder("before").received("2026-03-07T23:59:59", NEW_YORK),
        MessageBuilder("spring-start").received("2026-03-08T00:00:00", NEW_YORK),
        MessageBuilder("summer").received("2026-07-04T12:00:00", NEW_YORK),
        MessageBuilder("fall-last-second").received("2026-11-01T23:59:59", NEW_YORK),
        MessageBuilder("after").received("2026-11-02T00:00:00", NEW_YORK),
    ]
    fake = FakeGmail(build_messages(b.pdf("a.pdf") for b in builders), epoch_bounds=bounds)
    date_range = DateRange.from_days(date(2026, 3, 8), date(2026, 11, 1), ZoneInfo(NEW_YORK))

    refs = plan_range(fake, date_range, CancelToken())

    assert sorted(ids(refs)) == ["fall-last-second", "spring-start", "summer"]


# ------------------------------------------------------------- what is sent to Google
@pytest.mark.req("AC-4", "NFR-011")
def test_one_search_then_one_get_per_listed_message_and_nothing_else() -> None:
    fake = edge_mailbox(EpochBounds.INCLUSIVE)
    date_range = january_in_kolkata()

    plan_range(fake, date_range, CancelToken())

    searches = fake.calls_to("list_message_ids")
    assert [call.params["query"] for call in searches] == [baseline_query(date_range)]
    assert searches[0].params["include_spam_trash"] is False
    assert {call.method for call in fake.calls} == {"list_message_ids", "get_message"}
    assert len(fake.calls_to("get_message")) == len(fake.calls) - 1


# ----------------------------------------------------------------------------------- cancel
def test_a_set_token_stops_before_the_first_call() -> None:
    fake = edge_mailbox(EpochBounds.INCLUSIVE)
    token = CancelToken()
    token.set()

    with pytest.raises(RunCancelledError):
        plan_range(fake, january_in_kolkata(), token)

    assert fake.calls == []


def test_cancelling_during_the_search_stops_before_any_message_is_read() -> None:
    token = CancelToken()
    # The fake calls ``sleep`` at the start of every call; here that is "the user pressed Cancel".
    fake = FakeGmail(
        build_messages(
            [MessageBuilder("m1").received("2026-01-10T12:00:00", KOLKATA).pdf("a.pdf")]
        ),
        latency_s=1.0,
        sleep=lambda _seconds: token.set(),
    )

    with pytest.raises(RunCancelledError):
        plan_range(fake, january_in_kolkata(), token)

    assert [call.method for call in fake.calls] == ["list_message_ids"]
