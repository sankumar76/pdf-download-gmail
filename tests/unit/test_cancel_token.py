"""PGD-15 AC-7 (cancel part): the minimal ``CancelToken`` (architecture 6.9)."""

from __future__ import annotations

import threading
import time

import pytest

from gmail_pdf.domain.events import CancelToken

pytestmark = pytest.mark.req("NFR-004", "NFR-006", "AC-7")


def test_a_new_token_is_not_set() -> None:
    assert CancelToken().is_set() is False


def test_set_is_visible_and_can_be_repeated() -> None:
    token = CancelToken()

    token.set()
    token.set()

    assert token.is_set() is True


def test_wait_times_out_with_false_when_the_token_stays_clear() -> None:
    assert CancelToken().wait(0.01) is False


def test_wait_returns_true_at_once_when_the_token_is_already_set() -> None:
    token = CancelToken()
    token.set()

    started = time.monotonic()
    result = token.wait(30)

    assert (result, time.monotonic() - started < 5) == (True, True)


def test_setting_the_token_from_another_thread_interrupts_a_long_wait() -> None:
    token = CancelToken()
    threading.Timer(0.05, token.set).start()

    started = time.monotonic()
    result = token.wait(30)

    assert (result, time.monotonic() - started < 5) == (True, True)
