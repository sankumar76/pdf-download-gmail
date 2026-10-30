"""PGD-13 AC-3: the logging filter, ``install_logging_redaction`` and the third-party caps."""

from __future__ import annotations

import io
import logging
import sys
import types
from collections.abc import Iterator

import pytest

from gmail_pdf import redaction
from gmail_pdf.redaction import REDACTED, RedactingFilter, install_logging_redaction
from tests.support import sentinels

pytestmark = pytest.mark.req("FR-005", "NFR-012", "AC-3")

ALL_LEVELS = [
    pytest.param(logging.DEBUG, id="debug"),
    pytest.param(logging.INFO, id="info"),
    pytest.param(logging.WARNING, id="warning"),
    pytest.param(logging.ERROR, id="error"),
    pytest.param(logging.CRITICAL, id="critical"),
]
FORMAT = "%(levelname)s %(name)s %(message)s"


class Capture:
    """A DEBUG-level handler on the root logger that writes to a string."""

    def __init__(self, handler: logging.Handler, stream: io.StringIO) -> None:
        self.handler = handler
        self.stream = stream

    @property
    def text(self) -> str:
        return self.stream.getvalue()


@pytest.fixture
def capture() -> Iterator[Capture]:
    """Root logger at DEBUG with one redacting handler; everything is put back afterwards."""
    redaction.register_secret(sentinels.CLIENT_SECRET)
    redaction.register_secret(sentinels.ACCESS_TOKEN)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(FORMAT))
    install_logging_redaction(handler)
    root = logging.getLogger()
    previous_level = root.level
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    yield Capture(handler, stream)
    root.removeHandler(handler)
    root.setLevel(previous_level)


@pytest.mark.parametrize("level", ALL_LEVELS)
def test_app_logger_output_has_no_sentinel_at_any_level(capture: Capture, level: int) -> None:
    logging.getLogger("gmail_pdf.test").log(level, "value=%s", sentinels.CLIENT_SECRET)

    assert (capture.text.count(sentinels.CLIENT_SECRET), REDACTED in capture.text) == (0, True)


@pytest.mark.parametrize("name", redaction.THIRD_PARTY_LOGGERS)
@pytest.mark.parametrize("level", ALL_LEVELS)
def test_third_party_logger_output_has_no_sentinel_at_any_level(
    capture: Capture, name: str, level: int
) -> None:
    logging.getLogger(name).log(level, "token %s", sentinels.ACCESS_TOKEN)

    assert capture.text.count(sentinels.ACCESS_TOKEN) == 0


@pytest.mark.parametrize("name", redaction.THIRD_PARTY_LOGGERS)
def test_third_party_loggers_are_capped_at_warning(capture: Capture, name: str) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    install_logging_redaction()
    logger.debug("debug detail")
    logger.info("info detail")
    logger.warning("warning detail")

    assert (logger.level, "debug detail" in capture.text, "info detail" in capture.text) == (
        logging.WARNING,
        False,
        False,
    )
    assert "warning detail" in capture.text


@pytest.mark.parametrize("name", redaction.THIRD_PARTY_LOGGERS)
def test_a_stricter_third_party_level_is_kept(name: str) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)

    install_logging_redaction()

    assert logger.level == logging.ERROR


def test_httplib2_debuglevel_is_reset_to_zero_when_the_module_is_loaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = types.SimpleNamespace(debuglevel=2)
    monkeypatch.setitem(sys.modules, "httplib2", fake)

    install_logging_redaction()

    assert fake.debuglevel == 0


def test_a_missing_httplib2_module_is_not_imported_by_the_installer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(sys.modules, "httplib2", raising=False)

    install_logging_redaction()

    assert "httplib2" not in sys.modules


def test_filter_is_added_once_however_often_the_installer_runs() -> None:
    handler = logging.StreamHandler(io.StringIO())

    install_logging_redaction(handler)
    install_logging_redaction(handler)

    assert [type(f) for f in handler.filters] == [RedactingFilter]


def test_last_resort_handler_gets_the_filter() -> None:
    install_logging_redaction()

    assert logging.lastResort is not None
    assert any(isinstance(f, RedactingFilter) for f in logging.lastResort.filters)


def test_last_resort_output_has_no_sentinel(monkeypatch: pytest.MonkeyPatch) -> None:
    """With no handler configured Python prints WARNING and above through ``lastResort``."""
    redaction.register_secret(sentinels.CLIENT_SECRET)
    install_logging_redaction()
    root = logging.getLogger()
    monkeypatch.setattr(root, "handlers", [])
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stderr", stream)  # lastResort writes to the current sys.stderr

    logging.getLogger("gmail_pdf.unconfigured").warning("secret=%s", sentinels.CLIENT_SECRET)

    assert (stream.getvalue().count(sentinels.CLIENT_SECRET), REDACTED in stream.getvalue()) == (
        0,
        True,
    )


def test_a_missing_last_resort_handler_is_tolerated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(logging, "lastResort", None)

    install_logging_redaction()  # must not raise


# ------------------------------------------------------------------ what the filter touches
def test_args_are_formatted_then_redacted(capture: Capture) -> None:
    logging.getLogger("gmail_pdf.test").info("a=%s b=%d", sentinels.CLIENT_SECRET, 7)

    assert capture.text.strip() == f"INFO gmail_pdf.test a={REDACTED} b=7"


def test_token_shapes_are_redacted_in_log_messages(capture: Capture) -> None:
    logging.getLogger("gmail_pdf.test").error("%s", sentinels.UNREGISTERED_GOCSPX)

    assert capture.text.count(sentinels.UNREGISTERED_GOCSPX) == 0


def test_the_traceback_of_a_logged_exception_is_redacted(capture: Capture) -> None:
    try:
        raise RuntimeError(f"failed with {sentinels.CLIENT_SECRET}")
    except RuntimeError:
        logging.getLogger("gmail_pdf.test").exception("step failed")

    assert capture.text.count(sentinels.CLIENT_SECRET) == 0
    assert "RuntimeError" in capture.text
    assert "Traceback" in capture.text


def test_a_chained_exception_in_the_traceback_is_redacted(capture: Capture) -> None:
    try:
        try:
            raise ValueError(f"inner {sentinels.ACCESS_TOKEN}")
        except ValueError as inner:
            raise RuntimeError("outer") from inner
    except RuntimeError:
        logging.getLogger("gmail_pdf.test").exception("step failed")

    assert capture.text.count(sentinels.ACCESS_TOKEN) == 0
    assert "ValueError" in capture.text


def test_a_second_handler_without_the_filter_sees_the_redacted_record(capture: Capture) -> None:
    other_stream = io.StringIO()
    other = logging.StreamHandler(other_stream)
    logging.getLogger().addHandler(other)
    try:
        try:
            raise RuntimeError(sentinels.CLIENT_SECRET)
        except RuntimeError:
            logging.getLogger("gmail_pdf.test").exception("boom %s", sentinels.CLIENT_SECRET)
    finally:
        logging.getLogger().removeHandler(other)

    # The redacting handler was added first, so it cleaned the shared record for the other one.
    assert other_stream.getvalue().count(sentinels.CLIENT_SECRET) == 0


def test_stack_info_is_redacted(capture: Capture) -> None:
    redaction.register_secret("def test_stack_info_is_redacted")

    logging.getLogger("gmail_pdf.test").warning("where", stack_info=True)

    assert "def test_stack_info_is_redacted" not in capture.text
    assert "Stack (most recent call last)" in capture.text


def test_an_already_formatted_exception_text_is_redacted() -> None:
    record = logging.LogRecord("n", logging.ERROR, __file__, 1, "m", None, None)
    record.exc_text = f"Traceback ... {sentinels.UNREGISTERED_GOCSPX}"

    assert RedactingFilter().filter(record) is True

    assert record.exc_text == f"Traceback ... {REDACTED}"


def test_a_message_that_cannot_be_formatted_is_replaced_not_raised() -> None:
    record = logging.LogRecord("n", logging.ERROR, __file__, 1, "%d", ("not a number",), None)

    assert RedactingFilter().filter(record) is True

    assert record.getMessage() == redaction.UNFORMATTABLE_LOG_MESSAGE


def test_the_filter_never_drops_a_record() -> None:
    record = logging.LogRecord("n", logging.DEBUG, __file__, 1, "plain", None, None)

    assert RedactingFilter().filter(record) is True
    assert record.getMessage() == "plain"
