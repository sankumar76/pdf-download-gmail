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


SWEEP_QUERY = "has:attachment -filename:pdf"


@pytest.mark.req("QUA-03", "issue-11")
def test_a_baseline_token_sent_with_the_sweep_query_is_http_400() -> None:
    fake = numbered_mailbox(5, page_size=2)
    token = fake.list_message_ids(BASELINE_QUERY).next_page_token

    with pytest.raises(FakeGmailHttpError) as exc_info:
        fake.list_message_ids(SWEEP_QUERY, page_token=token)

    assert (exc_info.value.status, exc_info.value.reason) == (400, "invalidPageToken")


@pytest.mark.req("QUA-03", "issue-11")
def test_a_token_sent_with_another_spam_trash_flag_is_http_400() -> None:
    fake = numbered_mailbox(5, page_size=2)
    token = fake.list_message_ids(BASELINE_QUERY, include_spam_trash=False).next_page_token

    with pytest.raises(FakeGmailHttpError) as exc_info:
        fake.list_message_ids(BASELINE_QUERY, page_token=token, include_spam_trash=True)

    assert (exc_info.value.status, exc_info.value.reason) == (400, "invalidPageToken")


@pytest.mark.req("QUA-03", "issue-11")
def test_two_searches_page_independently_with_their_own_tokens() -> None:
    fake = FakeGmail(
        build_messages(
            [
                MessageBuilder("pdf-1").pdf("a.pdf"),
                MessageBuilder("pdf-2").pdf("b.pdf"),
                MessageBuilder("pdf-3").pdf("c.pdf"),
                MessageBuilder("png-1").attachment("a.png", "image/png", b"x"),
                MessageBuilder("png-2").attachment("b.png", "image/png", b"x"),
                MessageBuilder("png-3").attachment("c.png", "image/png", b"x"),
            ]
        ),
        page_size=2,
    )

    baseline_first = fake.list_message_ids(BASELINE_QUERY)
    sweep_first = fake.list_message_ids(SWEEP_QUERY)
    assert baseline_first.next_page_token and sweep_first.next_page_token
    baseline_rest = fake.list_message_ids(BASELINE_QUERY, page_token=baseline_first.next_page_token)
    sweep_rest = fake.list_message_ids(SWEEP_QUERY, page_token=sweep_first.next_page_token)

    assert sorted([*baseline_first.message_ids, *baseline_rest.message_ids]) == [
        "pdf-1",
        "pdf-2",
        "pdf-3",
    ]
    assert sorted([*sweep_first.message_ids, *sweep_rest.message_ids]) == [
        "png-1",
        "png-2",
        "png-3",
    ]


@pytest.mark.req("DEF-001", "issue-15")
@pytest.mark.parametrize(
    "offset",
    [
        pytest.param("²", id="superscript-two"),
        pytest.param("٣", id="arabic-indic-three"),
        pytest.param("１", id="fullwidth-one"),
        pytest.param("", id="empty"),
        pytest.param("-1", id="negative"),
    ],
)
def test_a_page_token_offset_that_is_not_an_ascii_number_is_http_400(offset: str) -> None:
    fake = numbered_mailbox(5, page_size=2)
    token = fake.list_message_ids(BASELINE_QUERY).next_page_token
    assert token is not None
    forged = f"{token.rpartition(':')[0]}:{offset}"

    with pytest.raises(FakeGmailHttpError) as exc_info:
        fake.list_message_ids(BASELINE_QUERY, page_token=forged)

    assert (exc_info.value.status, exc_info.value.reason) == (400, "invalidPageToken")


@pytest.mark.req("DEF-001", "issue-15")
@pytest.mark.parametrize("digits", ["²", "٣", "１"])
@pytest.mark.parametrize("term", ["after", "before"])
def test_an_epoch_term_that_is_not_an_ascii_number_is_an_unsupported_query(
    term: str, digits: str
) -> None:
    with pytest.raises(UnsupportedQueryError):
        numbered_mailbox(1).list_message_ids(f"{term}:{digits}")


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
