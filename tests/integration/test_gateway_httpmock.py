"""PGD-15 AC-4, AC-7 and AC-8: the gateway against the real Google client library.

The library builds the requests and parses the errors; only the HTTP transport is scripted
(``HttpMockSequence``, test-strategy section 3), so nothing leaves the process. The socket guard
of ``tests/conftest.py`` is active for every test here. The gateway rig itself is in
``tests/support/gateway_rig.py``, shared with the CLI tests of PGD-17 (AC-4).
"""

from __future__ import annotations

import inspect
import json
import logging
import re
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qs, urlsplit
from zoneinfo import available_timezones

import httplib2
import pytest
from google.oauth2.credentials import Credentials

from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.errors import GmailApiError, RetryExhaustedError, RunCancelledError
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.query import baseline_query
from gmail_pdf.domain.validation import FieldNames, RawInput, validate
from gmail_pdf.infra import gmail_gateway
from gmail_pdf.infra.gmail_gateway import GmailGateway, build_service
from gmail_pdf.infra.tz import resolve_zone
from tests.fakes.fake_time import FakeSleeper, FixedInstantClock
from tests.support import sentinels
from tests.support.gateway_rig import OK_EMPTY, Response, Rig, error, ok

pytestmark = pytest.mark.req("FR-009", "NFR-006", "NFR-011")


def query_of(uri: str) -> dict[str, list[str]]:
    return parse_qs(urlsplit(uri).query, keep_blank_values=True)


# ----------------------------------------------------------------------------------- AC-4
@pytest.mark.req("AC-4")
def test_the_baseline_search_sends_exactly_the_specified_request() -> None:
    rig = Rig(ok({"messages": [{"id": "m1"}, {"id": "m2"}], "nextPageToken": "next"}))
    date_range = DateRange(1767205800, 1769884200)  # Asia/Kolkata, 2026-01-01..2026-01-31

    page = rig.gateway.list_message_ids(baseline_query(date_range))

    [(method, uri)] = rig.requests
    assert method == "GET"
    assert urlsplit(uri).netloc == "gmail.googleapis.com"
    assert urlsplit(uri).path == "/gmail/v1/users/me/messages"
    assert query_of(uri) == {
        "q": ["has:attachment filename:pdf after:1767205799 before:1769884201"],
        "maxResults": ["500"],
        "includeSpamTrash": ["false"],
        "fields": ["messages/id,nextPageToken"],
        "alt": ["json"],
    }
    assert (page.message_ids, page.next_page_token) == (("m1", "m2"), "next")


@pytest.mark.req("AC-4")
def test_a_page_token_and_the_spam_trash_flag_are_passed_on() -> None:
    rig = Rig(ok({"messages": [{"id": "m3"}]}))

    page = rig.gateway.list_message_ids("has:attachment", page_token="tok", include_spam_trash=True)

    [(_, uri)] = rig.requests
    assert query_of(uri)["pageToken"] == ["tok"]
    assert query_of(uri)["includeSpamTrash"] == ["true"]
    assert (page.message_ids, page.next_page_token) == (("m3",), None)


def test_a_search_with_no_match_returns_an_empty_page() -> None:
    page = Rig(OK_EMPTY).gateway.list_message_ids("has:attachment")

    assert (page.message_ids, page.next_page_token) == ((), None)


def test_get_message_asks_for_the_full_format_of_one_message() -> None:
    resource = {"id": "m1", "internalDate": "1767205800000", "payload": {"parts": []}}
    rig = Rig(ok(resource))

    message = rig.gateway.get_message("m1")

    [(method, uri)] = rig.requests
    assert (method, urlsplit(uri).path, query_of(uri)) == (
        "GET",
        "/gmail/v1/users/me/messages/m1",
        {"format": ["full"], "alt": ["json"]},
    )
    assert message == resource


@pytest.mark.req("NFR-011")
def test_the_gateway_has_exactly_the_two_read_methods_of_this_story() -> None:
    public = {
        name
        for name, member in inspect.getmembers(GmailGateway, callable)
        if not name.startswith("_")
    }

    assert public == {"list_message_ids", "get_message"}


# ----------------------------------------------------------------------------------- AC-8
@pytest.mark.req("AC-8")
def test_the_client_builds_offline_from_the_bundled_discovery_document() -> None:
    credentials = Credentials(token=sentinels.ACCESS_TOKEN)

    service = build_service(credentials=credentials)  # the socket guard fails any network use

    assert callable(service.users().messages().list)
    assert callable(service.users().messages().get)


@pytest.mark.req("AC-8")
def test_the_client_is_built_for_gmail_v1_without_the_discovery_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    built: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def record(*args: Any, **kwargs: Any) -> object:
        built.append((args, kwargs))
        return object()

    monkeypatch.setattr(gmail_gateway, "build", record)

    build_service(http=httplib2.Http())

    [(args, kwargs)] = built
    assert args == ("gmail", "v1")
    assert kwargs["cache_discovery"] is False


@pytest.mark.req("AC-8")
@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param({}, id="neither"),
        pytest.param(
            {"credentials": Credentials(token="x"), "http": httplib2.Http()},
            id="both",
        ),
    ],
)
def test_the_client_needs_exactly_one_of_credentials_and_transport(
    arguments: dict[str, Any],
) -> None:
    with pytest.raises(ValueError, match="exactly one"):
        build_service(**arguments)


@pytest.mark.req("AC-8")
def test_requests_are_executed_with_num_retries_zero() -> None:
    class Request:
        def __init__(self) -> None:
            self.execute_calls: list[dict[str, Any]] = []

        def execute(self, **kwargs: Any) -> dict[str, Any]:
            self.execute_calls.append(kwargs)
            return {"id": "m1"}

    request = Request()

    class Messages:
        def get(self, **_: Any) -> Request:
            return request

    class Users:
        def messages(self) -> Messages:
            return Messages()

    class Service:
        def users(self) -> Users:
            return Users()

    GmailGateway(Service(), CancelToken()).get_message("m1")

    assert request.execute_calls == [{"num_retries": 0}]


# ----------------------------------------------------------------------------------- AC-7
@pytest.mark.req("AC-7")
@pytest.mark.parametrize(
    "failure",
    [
        pytest.param(error(429, "rateLimitExceeded"), id="429"),
        pytest.param(error(503), id="503"),
        pytest.param(error(403, "rateLimitExceeded"), id="403-rate-limit"),
        pytest.param(error(403, "userRateLimitExceeded"), id="403-user-rate-limit"),
        pytest.param(TimeoutError("scripted"), id="timeout"),
        pytest.param(httplib2.ServerNotFoundError("scripted"), id="dns"),
    ],
)
def test_a_retryable_failure_is_retried_and_the_second_answer_is_used(
    failure: Response | BaseException,
) -> None:
    rig = Rig(failure, ok({"messages": [{"id": "m1"}]}))

    page = rig.gateway.list_message_ids("has:attachment")

    assert page.message_ids == ("m1",)
    assert len(rig.requests) == 2
    assert rig.sleeper.delays == [1.0]


@pytest.mark.req("AC-7")
@pytest.mark.parametrize(
    ("failure", "status"),
    [
        pytest.param(error(401), 401, id="401"),
        pytest.param(error(403, "insufficientPermissions"), 403, id="403-other"),
        pytest.param(error(404), 404, id="404"),
    ],
)
def test_a_permanent_failure_raises_the_domain_error_at_once(
    failure: Response, status: int
) -> None:
    rig = Rig(failure)

    with pytest.raises(GmailApiError) as exc_info:
        rig.gateway.get_message("m1")

    assert exc_info.value.status == status
    assert len(rig.requests) == 1
    assert rig.sleeper.delays == []


@pytest.mark.req("AC-7")
@pytest.mark.parametrize(
    ("method", "call"),
    [
        pytest.param("list_message_ids", lambda g: g.list_message_ids("has:attachment"), id="list"),
        pytest.param("get_message", lambda g: g.get_message("m1"), id="get"),
    ],
)
def test_a_retry_is_logged_under_the_name_of_the_gateway_method(
    method: str, call: Callable[[GmailGateway], object], caplog: pytest.LogCaptureFixture
) -> None:
    rig = Rig(error(503), ok({"id": "m1", "messages": []}))

    with caplog.at_level(logging.WARNING):
        call(rig.gateway)

    assert [r.getMessage() for r in caplog.records if r.name == "gmail_pdf.infra.retry"] == [
        f"Retrying {method}: attempt 2 of 6 after 1.0 s"
    ]


@pytest.mark.req("AC-7")
def test_six_failed_attempts_end_in_the_exhaustion_error() -> None:
    rig = Rig(*[error(503)] * 6)

    with pytest.raises(RetryExhaustedError):
        rig.gateway.get_message("m1")

    assert len(rig.requests) == 6
    assert rig.sleeper.delays == [1.0, 2.0, 4.0, 8.0, 16.0]


@pytest.mark.req("AC-7")
def test_retry_after_seconds_header_sets_the_delay() -> None:
    rig = Rig(error(429, "rateLimitExceeded", **{"retry-after": "7"}), OK_EMPTY)

    rig.gateway.list_message_ids("has:attachment")

    assert rig.sleeper.delays == [7.0]


@pytest.mark.req("AC-7")
def test_retry_after_http_date_header_sets_the_delay() -> None:
    clock_now = FakeSleeper().clock.now()
    date = (clock_now + timedelta(seconds=11)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    rig = Rig(error(503, **{"retry-after": date}), OK_EMPTY)

    rig.gateway.list_message_ids("has:attachment")

    assert rig.sleeper.delays == [11.0]


@pytest.mark.req("AC-7")
def test_cancelling_during_the_backoff_stops_before_the_next_request() -> None:
    rig = Rig(error(503), OK_EMPTY, cancel_during_sleep=1)

    with pytest.raises(RunCancelledError):
        rig.gateway.list_message_ids("has:attachment")

    assert len(rig.requests) == 1


@pytest.mark.req("AC-7")
def test_a_set_token_stops_before_any_request_is_sent() -> None:
    rig = Rig(OK_EMPTY)
    rig.token.set()

    with pytest.raises(RunCancelledError):
        rig.gateway.list_message_ids("has:attachment")

    assert rig.requests == []


# ----------------------------------------------------------------- what the error keeps
def _failure_text(rig: Rig, call: Callable[[GmailGateway], object]) -> tuple[str, GmailApiError]:
    with pytest.raises(GmailApiError) as exc_info:
        call(rig.gateway)
    return str(exc_info.value), exc_info.value


def test_the_domain_error_carries_neither_the_body_nor_the_query_nor_a_chain() -> None:
    body = {
        "error": {
            "code": 401,
            "message": f"bad token {sentinels.ACCESS_TOKEN}",
            "errors": [{"reason": f"x {sentinels.REFRESH_TOKEN}"}],
        }
    }
    rig = Rig(({"status": "401"}, json.dumps(body)))

    text, error_ = _failure_text(
        rig, lambda g: g.list_message_ids(f"has:attachment {sentinels.CLIENT_SECRET}")
    )

    assert text == "Gmail answered the request with HTTP 401."
    assert error_.reason == ""
    assert error_.__cause__ is None
    assert error_.__context__ is None  # the library's HttpError (URL, body) is really dropped
    assert error_.__suppress_context__ is True
    assert sentinels.leaked(repr(vars(error_)) + text) == []


@pytest.mark.parametrize(
    "content",
    [b"", b"not json", b"[]", b'{"error": 5}', b'{"error": {"errors": []}}', b"\xff\xfe"],
)
def test_an_error_body_that_cannot_be_read_gives_an_empty_reason(content: bytes) -> None:
    rig = Rig(({"status": "404"}, content))

    _, error_ = _failure_text(rig, lambda g: g.get_message("m1"))

    assert (error_.status, error_.reason) == (404, "")


# ----------------------------------------------------------------------------------- AC-9 (PGD-16)
@pytest.mark.req("AC-9", "DEF-007")
def test_every_zone_at_the_floor_and_the_ceiling_sends_a_query_with_no_negative_bound() -> None:
    """DEF-007 / RISK-026: no ``q`` that reaches the real gateway carries a negative bound.

    Every name in ``available_timezones()`` goes through validation, the range and the real
    gateway on the scripted transport, once at 1970-01-02 and once at 9999-12-30.
    """
    zones = sorted(available_timezones())
    days = ("1970-01-02", "9999-12-30")
    names = FieldNames(start="--start", end="--end", tz="--tz")
    clock = FixedInstantClock(datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc))
    rig = Rig(*[OK_EMPTY] * (len(zones) * len(days)))
    expected: list[tuple[str, str]] = []

    for zone_name in zones:
        for day in days:
            request = validate(RawInput(day, day, zone_name, names), clock.today).request
            assert request is not None, (zone_name, day)
            date_range = DateRange.from_days(request.start, request.end, resolve_zone(zone_name))
            rig.gateway.list_message_ids(baseline_query(date_range))
            expected.append((zone_name, day))

    queries = [query_of(uri)["q"][0] for _, uri in rig.requests]
    assert len(queries) == len(expected) > 800
    bounds = []
    for query, case in zip(queries, expected, strict=True):
        match = re.fullmatch(r"has:attachment filename:pdf after:(\d+) before:(\d+)", query)
        assert match is not None, (case, query)  # no minus sign anywhere
        bounds.append((int(match[1]), int(match[2])))
    floor_after = [
        after for (after, _), (_, day) in zip(bounds, expected, strict=True) if day == days[0]
    ]
    # Etc/GMT-14 is the zone with the earliest local midnight: 1970-01-01T10:00:00Z = 36000 s.
    assert min(floor_after) == 35999
    assert all(before > after >= 0 for after, before in bounds)
