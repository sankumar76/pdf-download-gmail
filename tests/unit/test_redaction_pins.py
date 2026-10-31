"""DEF-005 (#31): the 8-character threshold and the four capped loggers are pinned to literals.

The other redaction tests import ``tests/support/redaction_pins.py`` instead of reading the
production constants, so changing a constant fails here and in the behaviour tests, and a
shortened logger list cannot remove its own test cases.
"""

from __future__ import annotations

import logging

import pytest

from gmail_pdf import redaction
from tests.support import redaction_pins

pytestmark = pytest.mark.req("FR-005", "NFR-012", "DEF-005")


@pytest.mark.req("AC-1")
def test_the_minimum_secret_length_is_eight() -> None:
    assert redaction.MIN_SECRET_LENGTH == 8


@pytest.mark.req("AC-1")
def test_the_boundary_strings_are_seven_and_eight_characters_long() -> None:
    assert (
        len(redaction_pins.SEVEN_CHARACTER_VALUE),
        len(redaction_pins.EIGHT_CHARACTER_VALUE),
    ) == (
        7,
        8,
    )


@pytest.mark.req("AC-1")
def test_a_seven_character_value_is_not_registered_and_an_eight_character_value_is() -> None:
    seven, eight = redaction_pins.SEVEN_CHARACTER_VALUE, redaction_pins.EIGHT_CHARACTER_VALUE
    redaction.register_secret(seven)
    redaction.register_secret(eight)

    assert redaction.redact(f"[{seven}] [{eight}]") == f"[{seven}] [{redaction.REDACTED}]"


@pytest.mark.req("AC-3")
def test_exactly_four_third_party_loggers_are_capped() -> None:
    assert set(redaction.THIRD_PARTY_LOGGERS) == {
        "googleapiclient",
        "google_auth_oauthlib",
        "urllib3",
        "oauthlib",
    }
    assert len(redaction.THIRD_PARTY_LOGGERS) == 4


@pytest.mark.req("AC-3")
@pytest.mark.parametrize("name", redaction_pins.THIRD_PARTY_LOGGERS)
def test_every_pinned_logger_is_capped_at_warning_by_the_installer(name: str) -> None:
    logging.getLogger(name).setLevel(logging.NOTSET)

    redaction.install_logging_redaction()

    assert logging.getLogger(name).level == logging.WARNING
