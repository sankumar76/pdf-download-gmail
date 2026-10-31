"""A real ``GmailGateway`` over a scripted HTTP transport, for tests in several directories.

Only the transport is scripted (``HttpMockSequence``, test-strategy section 3): the Google
library builds the requests and parses the errors, and nothing leaves the process. A fake
sleeper stands behind the cancel token, so a backoff of 16 s takes no time.
"""

from __future__ import annotations

import json
from typing import Any

from googleapiclient.http import HttpMockSequence

from gmail_pdf.infra.gmail_gateway import GmailGateway, build_service
from tests.fakes.fake_time import FakeCancelToken, FakeSleeper

Response = tuple[dict[str, str], str | bytes]
OK_EMPTY: Response = ({"status": "200"}, '{"resultSizeEstimate": 0}')


def ok(body: dict[str, Any]) -> Response:
    return {"status": "200"}, json.dumps(body)


def error(status: int, reason: str = "", **headers: str) -> Response:
    body = {"error": {"code": status, "message": "scripted", "errors": [{"reason": reason}]}}
    return {"status": str(status), **headers}, json.dumps(body)


class Rig:
    """A gateway over a scripted transport, with a fake sleeper behind its cancel token."""

    def __init__(self, *script: Response | BaseException, cancel_during_sleep: int | None = None):
        self.http = ScriptedHttp(list(script))
        self.sleeper = FakeSleeper()
        self.token = FakeCancelToken(self.sleeper, cancel_during_sleep)
        self.gateway = GmailGateway(
            build_service(http=self.http),
            self.token,
            now=self.sleeper.clock.now,
            jitter=lambda low, high: high,
        )

    @property
    def requests(self) -> list[tuple[str, str]]:
        return [(method, uri) for uri, method, _body, _headers in self.http.request_sequence]


class ScriptedHttp(HttpMockSequence):
    """``HttpMockSequence`` that can also raise a scripted transport error."""

    def request(self, uri: str, method: str = "GET", *args: Any, **kwargs: Any) -> Any:
        if self._iterable and isinstance(self._iterable[0], BaseException):
            self.request_sequence.append((uri, method, None, None))
            raise self._iterable.pop(0)
        return super().request(uri, method, *args, **kwargs)
