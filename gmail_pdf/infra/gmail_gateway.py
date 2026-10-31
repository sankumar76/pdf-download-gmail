"""The Gmail gateway: the only module that imports ``googleapiclient`` (NFR-011, architecture 4.1).

It exposes read-only calls and nothing else: ``list_message_ids`` (``users.messages.list``) and
``get_message`` (``users.messages.get``, ``format=full``). ``get_attachment`` is added by
STORY-03.03. No method that modifies a mailbox exists here, and none may be added.

Every call goes through ``infra.retry.call_with_retry`` with ``execute(num_retries=0)``, so the
retry rules of NFR-006 live in one place. The library's ``HttpError`` is turned into the domain
``GmailApiError`` here, keeping only the status, the reason token and the ``Retry-After`` header:
the response body, the URL (which carries the search query) and the headers are dropped.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import datetime
from typing import Any

from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import Http

from gmail_pdf.app.ports import JsonObject, MessageIdPage
from gmail_pdf.domain.errors import GmailApiError
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.infra import retry

USER_ID = "me"
LIST_PAGE_SIZE = 500  # Gmail's documented maximum for users.messages.list
LIST_FIELDS = "messages/id,nextPageToken"
MESSAGE_FORMAT = "full"
# Gmail reason tokens look like ``rateLimitExceeded``; anything else is dropped, so a body that
# echoes a secret cannot reach an error object through the reason.
_REASON = re.compile(r"[A-Za-z][A-Za-z0-9]{0,63}")


def build_service(*, credentials: Credentials | None = None, http: Http | None = None) -> Any:
    """Build the Gmail client once (``cache_discovery=False``, bundled discovery document).

    Exactly one of ``credentials`` (the real run) and ``http`` (tests, a scripted transport)
    must be given. Without either the library would look for ambient credentials, which this
    program never does.

    Raises:
        ValueError: neither or both were given.
    """
    if (credentials is None) == (http is None):
        raise ValueError("give exactly one of credentials and http")
    return build("gmail", "v1", credentials=credentials, http=http, cache_discovery=False)


def _reason_of(error: HttpError) -> str:
    """The Gmail error reason (``errors[0].reason`` of the JSON body), or an empty string."""
    try:
        body = json.loads(error.content.decode("utf-8"))
        reason = body["error"]["errors"][0]["reason"]
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        return ""
    return reason if isinstance(reason, str) and _REASON.fullmatch(reason) else ""


def _to_domain_error(error: HttpError) -> GmailApiError:
    retry_after = error.resp.get("retry-after")
    return GmailApiError(
        int(error.resp.status),
        _reason_of(error),
        retry_after if isinstance(retry_after, str) else None,
    )


class GmailGateway:
    """Read-only access to one mailbox through an already built Gmail client."""

    def __init__(
        self,
        service: Any,
        cancel: CancelToken,
        *,
        now: Callable[[], datetime] = retry.utc_now,
        jitter: Callable[[float, float], float] = retry.SYSTEM_JITTER,
    ) -> None:
        """
        Args:
            service: The client from ``build_service``, built once and reused.
            cancel: Checked before every call and waited on during a backoff.
            now: Clock for HTTP-date ``Retry-After`` values; tests pass a fake.
            jitter: ``uniform(low, high)`` for the backoff; tests pass a seeded one.
        """
        self._service = service
        self._cancel = cancel
        self._now = now
        self._jitter = jitter

    def _execute(self, method: str, request: Any) -> Any:
        def attempt() -> Any:
            try:
                return request.execute(num_retries=0)
            except HttpError as error:
                # ``from None``: the library's error text holds the full request URL.
                raise _to_domain_error(error) from None

        return retry.call_with_retry(
            attempt, method=method, cancel=self._cancel, now=self._now, jitter=self._jitter
        )

    def list_message_ids(
        self,
        query: str,
        *,
        page_token: str | None = None,
        include_spam_trash: bool = False,
    ) -> MessageIdPage:
        """List one page of message ids matching a Gmail search ``query``.

        Following ``next_page_token`` to later pages is the caller's job (STORY-02.04).
        """
        params: dict[str, Any] = {
            "userId": USER_ID,
            "q": query,
            "maxResults": LIST_PAGE_SIZE,
            "includeSpamTrash": include_spam_trash,
            "fields": LIST_FIELDS,
        }
        if page_token is not None:
            params["pageToken"] = page_token
        request = self._service.users().messages().list(**params)
        response = self._execute("list_message_ids", request)
        ids = tuple(str(message["id"]) for message in response.get("messages", ()))
        return MessageIdPage(ids, response.get("nextPageToken"))

    def get_message(self, message_id: str) -> JsonObject:
        """Return the message resource with ``format=full`` (nested part tree included)."""
        request = (
            self._service.users()
            .messages()
            .get(userId=USER_ID, id=message_id, format=MESSAGE_FORMAT)
        )
        message: JsonObject = self._execute("get_message", request)
        return message
