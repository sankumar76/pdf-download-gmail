"""PGD-13 AC-1 and AC-2: the secret registry and the token patterns in ``redact()``.

The other surfaces (log handler, ``safe_message``, excepthooks) are tested in
``test_redaction_logging.py``, ``test_redaction_safe_message.py`` and
``test_redaction_hooks.py``; the cross-surface sentinel matrix is ``test_sentinel_matrix.py``.
"""

from __future__ import annotations

import pytest

from gmail_pdf.redaction import MIN_SECRET_LENGTH, REDACTED, clear_secrets, redact, register_secret
from tests.support import sentinels

pytestmark = pytest.mark.req("FR-005", "NFR-012")


# ----------------------------------------------------------------------------------- AC-1
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        pytest.param(
            f"client_secret is {sentinels.CLIENT_SECRET}",
            f"client_secret is {REDACTED}",
            id="at-end",
        ),
        pytest.param(
            f"{sentinels.CLIENT_SECRET} leads the text",
            f"{REDACTED} leads the text",
            id="at-start",
        ),
        pytest.param(
            f"[{sentinels.CLIENT_SECRET}] and again {sentinels.CLIENT_SECRET}",
            f"[{REDACTED}] and again {REDACTED}",
            id="every-occurrence",
        ),
        pytest.param(
            f"not the secret: {sentinels.CLIENT_SECRET.lower()}",
            f"not the secret: {sentinels.CLIENT_SECRET.lower()}",
            id="match-is-case-sensitive",
        ),
        pytest.param(
            f"ключ→{sentinels.CLIENT_SECRET}←键",
            f"ключ→{REDACTED}←键",
            id="next-to-unicode",
        ),
        pytest.param("naïve café – ünïcödé text", "naïve café – ünïcödé text", id="unicode-intact"),
        pytest.param("", "", id="empty-text"),
    ],
)
@pytest.mark.req("AC-1")
def test_registered_secret_is_replaced_everywhere_it_occurs(text: str, expected: str) -> None:
    register_secret(sentinels.CLIENT_SECRET)

    assert redact(text) == expected


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("", id="empty"),
        pytest.param("a" * (MIN_SECRET_LENGTH - 1), id="seven-characters"),
        pytest.param(" " * MIN_SECRET_LENGTH, id="eight-spaces"),
        pytest.param("\t\n" * MIN_SECRET_LENGTH, id="whitespace-only"),
    ],
)
@pytest.mark.req("AC-1")
def test_values_that_are_too_short_or_blank_are_ignored(value: str) -> None:
    register_secret(value)
    text = f"plain text {value} with the value inside"

    assert redact(text) == text


@pytest.mark.req("AC-1")
def test_a_value_of_exactly_the_minimum_length_is_registered() -> None:
    value = "x" * MIN_SECRET_LENGTH
    register_secret(value)

    assert redact(f"a {value} b") == f"a {REDACTED} b"


@pytest.mark.req("AC-1")
def test_registering_the_same_value_twice_changes_nothing() -> None:
    register_secret(sentinels.REFRESH_TOKEN)
    register_secret(sentinels.REFRESH_TOKEN)

    assert redact(f"x {sentinels.REFRESH_TOKEN} y") == f"x {REDACTED} y"


@pytest.mark.req("AC-1")
def test_a_secret_that_contains_another_is_replaced_whole() -> None:
    inner = "SENTINEL-INNER-0001"
    register_secret(inner)
    register_secret(f"{inner}-TAIL-OF-OUTER")

    assert redact(f"v={inner}-TAIL-OF-OUTER.") == f"v={REDACTED}."


@pytest.mark.parametrize(
    ("secret", "encoded"),
    [
        pytest.param("SENTINEL/REFRESH/0001", "SENTINEL%2FREFRESH%2F0001", id="percent-encoded"),
        pytest.param("SENTINEL REFRESH 0001", "SENTINEL+REFRESH+0001", id="form-encoded-space"),
    ],
)
@pytest.mark.req("AC-1")
def test_url_encoded_forms_of_a_registered_secret_are_replaced(secret: str, encoded: str) -> None:
    register_secret(secret)

    assert redact(f"https://example.invalid/cb?token={encoded}&x=1") == (
        f"https://example.invalid/cb?token={REDACTED}&x=1"
    )


@pytest.mark.req("AC-1")
def test_clear_secrets_forgets_every_registered_value() -> None:
    register_secret(sentinels.CLIENT_SECRET)
    clear_secrets()

    assert redact(sentinels.CLIENT_SECRET) == sentinels.CLIENT_SECRET


# ----------------------------------------------------------------------------------- AC-2
PATTERN_CASES = [
    pytest.param("token ya29.SENTINEL0001 end", f"token {REDACTED} end", id="access-token-ya29"),
    pytest.param(
        f"refresh {sentinels.UNREGISTERED_REFRESH_SHAPE}!", f"refresh {REDACTED}!", id="refresh-1//"
    ),
    pytest.param(
        f"secret {sentinels.UNREGISTERED_GOCSPX} ok", f"secret {REDACTED} ok", id="gocspx-secret"
    ),
    pytest.param(
        '{"access_token": "abc.DEF-123", "expires_in": 3599}',
        f'{{"access_token": "{REDACTED}", "expires_in": 3599}}',
        id="json-access_token",
    ),
    pytest.param(
        "{'refresh_token':'rt-value-1','scope':'x'}",
        f"{{'refresh_token':'{REDACTED}','scope':'x'}}",
        id="json-single-quotes-refresh_token",
    ),
    pytest.param(
        '{"client_secret" : "cs-value"}',
        f'{{"client_secret" : "{REDACTED}"}}',
        id="json-client_secret-spaced",
    ),
    pytest.param(
        '{"id_token": "eyJhbGciOi.payload.sig"}',
        f'{{"id_token": "{REDACTED}"}}',
        id="json-id_token",
    ),
    pytest.param(
        "GET /cb?state=s1&code=4/0AbCdEf&scope=x",
        f"GET /cb?state=s1&code={REDACTED}&scope=x",
        id="query-string-code",
    ),
    pytest.param(
        "grant_type=refresh_token&refresh_token=rt-value-2&client_id=cid",
        f"grant_type=refresh_token&refresh_token={REDACTED}&client_id=cid",
        id="query-string-refresh_token",
    ),
    pytest.param(
        "ACCESS_TOKEN=Mixed.Case-1 end", f"ACCESS_TOKEN={REDACTED} end", id="key-case-folded"
    ),
    pytest.param(
        "Authorization: Bearer opaque-token-value rest",
        f"Authorization: Bearer {REDACTED} rest",
        id="authorization-bearer",
    ),
    pytest.param(
        "authorization:bearer   lower-case-value",
        f"authorization:bearer   {REDACTED}",
        id="authorization-bearer-lower-case",
    ),
    pytest.param(
        "bad Authorization: Bearer ya29.SENTINEL0001",
        f"bad Authorization: Bearer {REDACTED}",
        id="bearer-with-ya29",
    ),
    pytest.param("code=4/0AbCdEf", f"code={REDACTED}", id="code-at-start-of-text"),
]


@pytest.mark.parametrize(("text", "expected"), PATTERN_CASES)
@pytest.mark.req("AC-2")
def test_token_shapes_are_redacted_without_any_registered_secret(text: str, expected: str) -> None:
    assert redact(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("Downloaded 3 PDFs from 12 messages.", id="ordinary-sentence"),
        pytest.param("The access token is mentioned but has no value.", id="words-only"),
        pytest.param("status_code: 404 for the request", id="status_code-is-not-code"),
        pytest.param("zipcode=10001", id="zipcode-is-not-code"),
        pytest.param("error_code=7", id="error_code-is-not-code"),
        pytest.param("ya29 is a prefix but this has no dot", id="ya29-without-dot"),
        pytest.param("path C:/data/1/report.pdf", id="digit-slash-path"),
        pytest.param("GOCSPX alone, no dash", id="gocspx-without-dash"),
        pytest.param("Authorization header was missing", id="authorization-without-bearer"),
    ],
)
@pytest.mark.req("AC-2")
def test_ordinary_text_is_left_unchanged(text: str) -> None:
    assert redact(text) == text


@pytest.mark.parametrize(
    "text", [pytest.param(case.values[0], id=str(case.id)) for case in PATTERN_CASES]
)
@pytest.mark.req("AC-2")
def test_redacting_twice_gives_the_same_result(text: str) -> None:
    once = redact(text)

    assert redact(once) == once
