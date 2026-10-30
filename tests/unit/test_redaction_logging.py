"""PGD-13 AC-3: the logging filter, ``install_logging_redaction`` and the third-party caps."""

from __future__ import annotations

import io
import logging
import sys
import traceback
import types
import warnings
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


# ------------------------------------------------------------------ records at every level
@pytest.mark.parametrize("level", ALL_LEVELS)
def test_app_logger_output_has_no_sentinel_at_any_level(capture: Capture, level: int) -> None:
    logging.getLogger("gmail_pdf.test").log(level, "value=%s", sentinels.CLIENT_SECRET)

    assert capture.text.count(sentinels.CLIENT_SECRET) == 0


def test_the_redacted_marker_replaces_the_secret_in_log_output(capture: Capture) -> None:
    logging.getLogger("gmail_pdf.test").info("value=%s", sentinels.CLIENT_SECRET)

    assert REDACTED in capture.text


@pytest.mark.parametrize("name", redaction.THIRD_PARTY_LOGGERS)
@pytest.mark.parametrize("level", ALL_LEVELS)
def test_third_party_logger_output_has_no_sentinel_at_any_level(
    capture: Capture, name: str, level: int
) -> None:
    logging.getLogger(name).log(level, "token %s", sentinels.ACCESS_TOKEN)

    assert capture.text.count(sentinels.ACCESS_TOKEN) == 0


# ------------------------------------------------------------------ the third-party cap
@pytest.fixture
def capped_logger(capture: Capture, request: pytest.FixtureRequest) -> logging.Logger:
    """A third-party logger set to DEBUG, capped by the installer, one record per level."""
    logger = logging.getLogger(request.param)
    logger.setLevel(logging.DEBUG)
    install_logging_redaction()
    logger.debug("debug detail")
    logger.info("info detail")
    logger.warning("warning detail")
    return logger


CAPPED = pytest.mark.parametrize("capped_logger", redaction.THIRD_PARTY_LOGGERS, indirect=True)


@CAPPED
def test_third_party_loggers_are_capped_at_warning(capped_logger: logging.Logger) -> None:
    assert capped_logger.level == logging.WARNING


@CAPPED
def test_a_capped_logger_drops_debug_records(
    capped_logger: logging.Logger, capture: Capture
) -> None:
    assert "debug detail" not in capture.text


@CAPPED
def test_a_capped_logger_drops_info_records(
    capped_logger: logging.Logger, capture: Capture
) -> None:
    assert "info detail" not in capture.text


@CAPPED
def test_a_capped_logger_still_passes_warnings(
    capped_logger: logging.Logger, capture: Capture
) -> None:
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


# ------------------------------------------------------------------ where the filter is attached
def test_filter_is_added_once_however_often_the_installer_runs() -> None:
    handler = logging.StreamHandler(io.StringIO())

    install_logging_redaction(handler)
    install_logging_redaction(handler)

    assert [type(f) for f in handler.filters] == [RedactingFilter]


def test_last_resort_handler_gets_the_filter() -> None:
    install_logging_redaction()

    filters = logging.lastResort.filters if logging.lastResort else []
    assert any(isinstance(f, RedactingFilter) for f in filters)


@pytest.fixture
def last_resort_output(monkeypatch: pytest.MonkeyPatch) -> str:
    """What Python prints through ``lastResort`` for a WARNING when no handler is configured."""
    redaction.register_secret(sentinels.CLIENT_SECRET)
    install_logging_redaction()
    monkeypatch.setattr(logging.getLogger(), "handlers", [])
    stream = io.StringIO()
    monkeypatch.setattr(sys, "stderr", stream)  # lastResort writes to the current sys.stderr
    logging.getLogger("gmail_pdf.unconfigured").warning("secret=%s", sentinels.CLIENT_SECRET)
    return stream.getvalue()


def test_last_resort_output_has_no_sentinel(last_resort_output: str) -> None:
    assert last_resort_output.count(sentinels.CLIENT_SECRET) == 0


def test_last_resort_output_still_shows_the_message(last_resort_output: str) -> None:
    assert f"secret={REDACTED}" in last_resort_output


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


@pytest.fixture
def logged_traceback(capture: Capture) -> str:
    """Log text for an exception chain whose messages carry two registered secrets."""
    try:
        try:
            raise ValueError(f"inner {sentinels.ACCESS_TOKEN}")
        except ValueError as inner:
            raise RuntimeError(f"failed with {sentinels.CLIENT_SECRET}") from inner
    except RuntimeError:
        logging.getLogger("gmail_pdf.test").exception("step failed")
    return capture.text


def test_the_traceback_of_a_logged_exception_has_no_sentinel(logged_traceback: str) -> None:
    assert sentinels.leaked(logged_traceback) == []


@pytest.mark.parametrize("name", ["RuntimeError", "ValueError"])
def test_a_logged_exception_still_shows_its_class_names(logged_traceback: str, name: str) -> None:
    assert name in logged_traceback


def test_a_logged_exception_still_shows_the_traceback_header(logged_traceback: str) -> None:
    assert "Traceback" in logged_traceback


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


def test_stack_info_text_is_redacted() -> None:
    redaction.register_secret(sentinels.CLIENT_SECRET)
    record = logging.LogRecord("n", logging.WARNING, __file__, 1, "where", None, None)
    record.stack_info = f"Stack (most recent call last):\n  frame using {sentinels.CLIENT_SECRET}"

    RedactingFilter().filter(record)

    assert record.stack_info == f"Stack (most recent call last):\n  frame using {REDACTED}"


def test_stack_info_of_a_logged_record_is_redacted(capture: Capture) -> None:
    redaction.register_secret("stack_info=True")  # text that this frame's source line holds
    logging.getLogger("gmail_pdf.test").warning("where", stack_info=True)

    assert "stack_info=True" not in capture.text


def test_an_already_formatted_exception_text_is_redacted() -> None:
    record = logging.LogRecord("n", logging.ERROR, __file__, 1, "m", None, None)
    record.exc_text = f"Traceback ... {sentinels.UNREGISTERED_GOCSPX}"

    RedactingFilter().filter(record)

    assert record.exc_text == f"Traceback ... {REDACTED}"


def test_a_message_that_cannot_be_formatted_is_replaced_not_raised() -> None:
    record = logging.LogRecord("n", logging.ERROR, __file__, 1, "%d", ("not a number",), None)

    RedactingFilter().filter(record)

    assert record.getMessage() == redaction.UNFORMATTABLE_LOG_MESSAGE


def test_the_filter_never_drops_a_record() -> None:
    record = logging.LogRecord("n", logging.DEBUG, __file__, 1, "plain", None, None)

    assert RedactingFilter().filter(record) is True


def test_the_filter_keeps_a_plain_message_unchanged() -> None:
    record = logging.LogRecord("n", logging.DEBUG, __file__, 1, "plain", None, None)

    RedactingFilter().filter(record)

    assert record.getMessage() == "plain"


# ------------------------------------------------------------------ warnings (QUA-23)
def library_warning(text: str) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("always")
        warnings.warn(text, UserWarning, stacklevel=1)


def test_a_library_warning_reaches_the_log_without_the_sentinel(capture: Capture) -> None:
    library_warning(f"token {sentinels.CLIENT_SECRET} refreshed")

    assert capture.text.count(sentinels.CLIENT_SECRET) == 0


def test_a_library_warning_is_routed_through_logging(capture: Capture) -> None:
    library_warning(f"token {sentinels.CLIENT_SECRET} refreshed")

    assert f"token {REDACTED} refreshed" in capture.text


# ------------------------------------------------------------------ a failing filter (QUA-27)
# ``logger.exception()`` must neither abort its caller nor print the original failure when
# formatting or redaction fails inside the filter.
def raise_with_a_secret(*args: object, **kwargs: object) -> None:
    raise MemoryError(sentinels.CLIENT_SECRET)


def log_an_exception_with_a_secret() -> None:
    try:
        raise RuntimeError(f"failed with {sentinels.CLIENT_SECRET}")
    except RuntimeError:
        logging.getLogger("gmail_pdf.test").exception("step failed")


@pytest.fixture
def logged_with_formatting_broken(capture: Capture, monkeypatch: pytest.MonkeyPatch) -> str:
    """Log text of ``logger.exception`` while ``traceback.format_exception`` fails."""
    monkeypatch.setattr(traceback, "format_exception", raise_with_a_secret)
    log_an_exception_with_a_secret()
    return capture.text


@pytest.fixture
def logged_with_redact_broken(capture: Capture, monkeypatch: pytest.MonkeyPatch) -> str:
    """Log text of ``logger.exception`` while ``redact`` fails."""
    monkeypatch.setattr(redaction, "redact", raise_with_a_secret)
    log_an_exception_with_a_secret()
    return capture.text


def test_a_traceback_that_cannot_be_formatted_leaves_no_sentinel(
    logged_with_formatting_broken: str,
) -> None:
    assert sentinels.leaked(logged_with_formatting_broken) == []


def test_a_traceback_that_cannot_be_formatted_is_replaced_by_the_placeholder(
    logged_with_formatting_broken: str,
) -> None:
    assert redaction.TRACEBACK_UNAVAILABLE in logged_with_formatting_broken


def test_a_traceback_that_cannot_be_formatted_keeps_the_log_message(
    logged_with_formatting_broken: str,
) -> None:
    assert "step failed" in logged_with_formatting_broken


def test_a_failing_redact_leaves_no_sentinel_in_the_log(logged_with_redact_broken: str) -> None:
    assert sentinels.leaked(logged_with_redact_broken) == []


def test_a_failing_redact_reduces_the_record_to_the_placeholder_message(
    logged_with_redact_broken: str,
) -> None:
    assert redaction.UNFORMATTABLE_LOG_MESSAGE in logged_with_redact_broken


def test_the_filter_still_returns_true_when_redaction_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(redaction, "redact", raise_with_a_secret)
    record = logging.LogRecord("n", logging.ERROR, __file__, 1, "m", None, None)

    assert RedactingFilter().filter(record) is True
