"""AC-7: FakeGmail listing: paging, order, search terms and epoch interpretation."""

from __future__ import annotations

import pytest

from tests.fakes.fake_gmail import EpochBounds, FakeGmail, FakeGmailHttpError, UnsupportedQueryError
from tests.fixtures.builders import MessageBuilder, build_messages, epoch_ms
from tests.fixtures.helpers import BASELINE_QUERY, list_all, numbered_mailbox

pytestmark = pytest.mark.req("NFR-022", "AC-7")


# ------------------------------------------------------------------ paging and order
def test_first_page_holds_page_size_ids_and_a_next_token() -> None:
    page = numbered_mailbox(5, page_size=2).list_message_ids(BASELINE_QUERY)

    assert len(page.message_ids) == 2
    assert page.next_page_token is not None


def test_following_the_tokens_returns_every_id_once() -> None:
    assert len(list_all(numbered_mailbox(5, page_size=2))) == 5


def test_last_page_has_no_next_token() -> None:
    page = numbered_mailbox(3, page_size=3).list_message_ids(BASELINE_QUERY)

    assert page.next_page_token is None


def test_default_order_is_newest_first() -> None:
    assert list_all(numbered_mailbox(4)) == ["m03", "m02", "m01", "m00"]


def test_shuffled_order_differs_from_newest_first_but_is_complete() -> None:
    ordered = list_all(numbered_mailbox(12))
    shuffled = list_all(numbered_mailbox(12, shuffle_seed=7))

    assert shuffled != ordered
    assert sorted(shuffled) == sorted(ordered)


def test_shuffled_order_is_reproducible_for_a_seed() -> None:
    assert list_all(numbered_mailbox(12, shuffle_seed=7)) == list_all(
        numbered_mailbox(12, shuffle_seed=7)
    )


def test_shuffle_changes_between_list_calls_on_one_fake() -> None:
    fake = numbered_mailbox(12, shuffle_seed=7)

    assert list_all(fake) != list_all(fake)


def test_paging_is_stable_within_one_shuffled_listing() -> None:
    ids = list_all(numbered_mailbox(9, page_size=4, shuffle_seed=3))

    assert len(ids) == len(set(ids)) == 9


def test_unknown_page_token_is_http_400() -> None:
    with pytest.raises(FakeGmailHttpError) as exc_info:
        numbered_mailbox(1).list_message_ids(BASELINE_QUERY, page_token="bogus")

    assert exc_info.value.status == 400


def test_page_size_must_be_positive() -> None:
    with pytest.raises(ValueError, match="page_size"):
        FakeGmail(page_size=0)


def test_duplicate_message_id_is_rejected() -> None:
    message = MessageBuilder("dup").pdf("a.pdf").build()

    with pytest.raises(ValueError, match="duplicate"):
        FakeGmail([message, message])


# ------------------------------------------------------------------ query terms
SEARCH_MAILBOX = build_messages(
    [
        MessageBuilder("with-pdf").pdf("a.pdf"),
        MessageBuilder("with-png").attachment("a.png", "image/png", b"x"),
        MessageBuilder("text-only").text(),
        MessageBuilder("upper").pdf("B.PDF").subject("Quarterly Report"),
    ]
)


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        pytest.param("has:attachment", ["upper", "with-pdf", "with-png"], id="has-attachment"),
        pytest.param("filename:pdf", ["upper", "with-pdf"], id="filename-is-case-insensitive"),
        pytest.param("has:attachment -filename:pdf", ["with-png"], id="negated-term"),
        pytest.param("quarterly", ["upper"], id="plain-word-matches-subject"),
    ],
)
def test_search_terms(query: str, expected: list[str]) -> None:
    assert sorted(list_all(FakeGmail(SEARCH_MAILBOX), query)) == expected


@pytest.mark.parametrize(
    "query",
    [
        pytest.param("label:inbox", id="unknown-operator"),
        pytest.param("a OR b", id="or"),
        pytest.param("a AND b", id="and"),
        pytest.param("{filename:pdf filename:png}", id="braces"),
        pytest.param("(a b)", id="parentheses"),
        pytest.param('"exact phrase"', id="quoted-phrase"),
    ],
)
def test_unsupported_search_syntax_is_rejected(query: str) -> None:
    with pytest.raises(UnsupportedQueryError):
        list_all(FakeGmail(SEARCH_MAILBOX), query)


def test_spam_and_trash_are_excluded_by_default() -> None:
    fake = FakeGmail(
        build_messages(
            [MessageBuilder("ok").pdf("a.pdf"), MessageBuilder("bad").pdf("a.pdf").labels("SPAM")]
        )
    )

    assert list_all(fake) == ["ok"]


def test_spam_and_trash_are_included_on_request() -> None:
    fake = FakeGmail(
        build_messages(
            [MessageBuilder("ok").pdf("a.pdf"), MessageBuilder("bad").pdf("a.pdf").labels("SPAM")]
        )
    )

    page = fake.list_message_ids(BASELINE_QUERY, include_spam_trash=True)

    assert sorted(page.message_ids) == ["bad", "ok"]


# ------------------------------------------------------------------ epoch interpretation
EDGE_SECOND = epoch_ms("2026-01-15T00:00:00") // 1000


def _edge_mailbox(bounds: EpochBounds) -> FakeGmail:
    message = MessageBuilder("edge").received("2026-01-15T00:00:00").pdf("a.pdf").build()
    return FakeGmail([message], epoch_bounds=bounds)


@pytest.mark.parametrize(
    ("bounds", "term", "expected"),
    [
        pytest.param(EpochBounds.INCLUSIVE, "after", ["edge"], id="inclusive-after"),
        pytest.param(EpochBounds.INCLUSIVE, "before", ["edge"], id="inclusive-before"),
        pytest.param(EpochBounds.EXCLUSIVE, "after", [], id="exclusive-after"),
        pytest.param(EpochBounds.EXCLUSIVE, "before", [], id="exclusive-before"),
    ],
)
def test_epoch_term_at_the_exact_second_follows_the_interpretation(
    bounds: EpochBounds, term: str, expected: list[str]
) -> None:
    assert list_all(_edge_mailbox(bounds), f"{term}:{EDGE_SECOND}") == expected


def test_epoch_interpretation_can_be_switched_on_a_live_fake() -> None:
    fake = _edge_mailbox(EpochBounds.INCLUSIVE)
    before_switch = list_all(fake, f"after:{EDGE_SECOND}")

    fake.epoch_bounds = EpochBounds.EXCLUSIVE

    assert (before_switch, list_all(fake, f"after:{EDGE_SECOND}")) == (["edge"], [])
