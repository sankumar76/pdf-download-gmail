"""Literal values the redaction tests pin, so no test follows a production constant (DEF-005, #31).

``gmail_pdf.redaction`` holds ``MIN_SECRET_LENGTH`` and ``THIRD_PARTY_LOGGERS``. A test that
builds its boundary strings or its parameter list *from* those constants accepts a wrong constant
(a threshold of 4 or 12 still passes) and loses its own cases when the list is shortened. The
tests therefore import these literals and ``test_redaction_pins.py`` asserts that the production
values equal them.

A deliberate change to either value is a security decision (RISK-005): change it here and in the
production module in the same commit, with the reason in the commit message.
"""

from __future__ import annotations

# Registered secrets shorter than this are ignored (PGD-13 AC-1, architecture 8.4 item 1).
MIN_SECRET_LENGTH = 8
# Exactly one character below and exactly at the threshold. Neutral words, not secret-shaped.
SEVEN_CHARACTER_VALUE = "abcdefg"
EIGHT_CHARACTER_VALUE = "abcdefgh"

# Loggers capped at WARNING (PGD-13 AC-3, architecture 8.4 item 4).
THIRD_PARTY_LOGGERS = ("googleapiclient", "google_auth_oauthlib", "urllib3", "oauthlib")
