"""AC-7: FakeGmail scripted faults, latency and the call recorder."""

from __future__ import annotations

import pytest

from tests.fakes.fake_gmail import FakeGmail, FakeGmailHttpError, FakeGmailTimeout
from tests.fixtures.builders import MessageBuilder
from tests.fixtures.helpers import BASELINE_QUERY, numbered_mailbox

pytestmark = pytest.mark.req("NFR-022", "AC-7")


def _one_message() -> FakeGmail:
    return FakeGmail([MessageBuilder("m1").pdf("a.pdf").build()])


# ------------------------------------------------------------------ faults
@pytest.mark.parametrize(
    ("status", "reason"),
    [
        pytest.param(429, "rateLimitExceeded", id="429"),
        pytest.param(500, "", id="500"),
        pytest.param(503, "backendError", id="503"),
        pytest.param(403, "rateLimitExceeded", id="403-rate-limit"),
        pytest.param(400, "", id="400"),
        pytest.param(404, "", id="404"),
    ],
)
def test_scripted_http_fault_carries_status_reason_and_retry_after(
    status: int, reason: str
) -> None:
    fake = _one_message()
    fake.fail_with_http("get_message", status, reason, retry_after=3.0)

    with pytest.raises(FakeGmailHttpError) as exc_info:
        fake.get_message("m1")

    error = exc_info.value
    assert (error.status, error.reason, error.retry_after) == (status, reason, 3.0)


def test_scripted_http_fault_fires_once_then_the_call_succeeds() -> None:
    fake = _one_message()
    fake.fail_with_http("get_message", 500)
    with pytest.raises(FakeGmailHttpError):
        fake.get_message("m1")

    assert fake.get_message("m1")["id"] == "m1"


def test_scripted_timeout_raises_once() -> None:
    fake = _one_message()
    fake.fail_with_timeout("get_message")

    with pytest.raises(FakeGmailTimeout):
        fake.get_message("m1")


def test_call_after_a_scripted_timeout_succeeds() -> None:
    fake = _one_message()
    fake.fail_with_timeout("get_message")
    with pytest.raises(FakeGmailTimeout):
        fake.get_message("m1")

    assert fake.get_message("m1")["id"] == "m1"


def test_fault_with_a_parameter_match_ignores_other_messages() -> None:
    fake = numbered_mailbox(3)
    fake.fail_with_http("get_message", 500, message_id="m01")

    assert fake.get_message("m00")["id"] == "m00"


def test_fault_skip_lets_the_first_matching_calls_succeed() -> None:
    fake = numbered_mailbox(2)
    fake.fail_with_http("get_message", 500, skip=1)

    assert fake.get_message("m00")["id"] == "m00"
    with pytest.raises(FakeGmailHttpError):
        fake.get_message("m00")


def test_fault_times_limits_how_many_calls_fail() -> None:
    fake = numbered_mailbox(1)
    fake.fail_with_http("get_message", 500, times=2)
    for _ in range(2):
        with pytest.raises(FakeGmailHttpError):
            fake.get_message("m00")

    assert fake.get_message("m00")["id"] == "m00"


def test_fault_with_unlimited_times_keeps_failing() -> None:
    fake = numbered_mailbox(1)
    fake.fail_with_http("get_message", 503, times=None)

    for _ in range(3):
        with pytest.raises(FakeGmailHttpError):
            fake.get_message("m00")


def test_wildcard_fault_applies_to_every_method() -> None:
    fake = numbered_mailbox(1)
    fake.fail_with_http("*", 503, times=None)

    with pytest.raises(FakeGmailHttpError):
        fake.list_message_ids(BASELINE_QUERY)
    with pytest.raises(FakeGmailHttpError):
        fake.get_message("m00")


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        pytest.param({"times": 0}, "times", id="times-zero"),
        pytest.param({"times": -1}, "times", id="times-negative"),
        pytest.param({"skip": -1}, "skip", id="skip-negative"),
    ],
)
def test_invalid_fault_arguments_are_rejected(kwargs: dict[str, int], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        _one_message().fail_with_http("get_message", 500, **kwargs)


def test_timeout_fault_arguments_are_validated_too() -> None:
    with pytest.raises(ValueError, match="times"):
        _one_message().fail_with_timeout("get_message", times=0)


# ------------------------------------------------------------------ latency
def test_latency_sleeps_before_each_call() -> None:
    slept: list[float] = []
    fake = numbered_mailbox(1, latency_s=0.3, sleep=slept.append)

    fake.list_message_ids(BASELINE_QUERY)
    fake.get_message("m00")

    assert slept == [0.3, 0.3]


def test_latency_also_applies_to_faulted_calls() -> None:
    slept: list[float] = []
    fake = numbered_mailbox(1, latency_s=0.3, sleep=slept.append)
    fake.fail_with_http("get_message", 500)

    with pytest.raises(FakeGmailHttpError):
        fake.get_message("m00")

    assert slept == [0.3]


def test_no_sleep_without_latency() -> None:
    slept: list[float] = []

    numbered_mailbox(1, sleep=slept.append).list_message_ids(BASELINE_QUERY)

    assert slept == []


# ------------------------------------------------------------------ call recorder
def test_recorder_keeps_methods_in_call_order() -> None:
    fake = numbered_mailbox(1)

    fake.list_message_ids(BASELINE_QUERY)
    fake.get_message("m00")

    assert [call.method for call in fake.calls] == ["list_message_ids", "get_message"]


def test_recorder_keeps_list_parameters() -> None:
    fake = numbered_mailbox(1)

    fake.list_message_ids(BASELINE_QUERY, include_spam_trash=True)

    assert fake.calls[0].params == {
        "query": BASELINE_QUERY,
        "page_token": None,
        "include_spam_trash": True,
    }


def test_recorder_keeps_attachment_parameters() -> None:
    fake = numbered_mailbox(1)
    attachment_id = fake.get_message("m00")["payload"]["parts"][0]["body"]["attachmentId"]

    fake.get_attachment("m00", attachment_id)

    assert fake.calls[-1].params == {"message_id": "m00", "attachment_id": attachment_id}


def test_recorder_flags_faulted_calls() -> None:
    fake = numbered_mailbox(1)
    fake.fail_with_http("get_message", 500)

    with pytest.raises(FakeGmailHttpError):
        fake.get_message("m00")
    fake.get_message("m00")

    assert [call.faulted for call in fake.calls] == [True, False]


def test_calls_to_filters_by_method() -> None:
    fake = numbered_mailbox(1)
    fake.list_message_ids(BASELINE_QUERY)
    fake.get_message("m00")
    fake.get_message("m00")

    assert len(fake.calls_to("get_message")) == 2


def test_only_allow_listed_methods_are_recorded() -> None:
    fake = numbered_mailbox(1)
    fake.list_message_ids(BASELINE_QUERY)
    fake.get_message("m00")

    assert {call.method for call in fake.calls} <= {
        "list_message_ids",
        "get_message",
        "get_attachment",
    }
