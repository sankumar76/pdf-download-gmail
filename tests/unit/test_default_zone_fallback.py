"""PGD-84 AC-1 to AC-5, AC-8 and AC-9: no ``--tz`` and no identifiable system zone means IST.

The 16 rows that pinned the old exit-2 path moved with these ACs and are in
``test_cli_invalid_input.py``, ``test_daterange.py`` and ``test_validation_zone_and_table.py``.
Here are the new rows: the fallback in both modes, the range it gives (AC-3), a given ``--tz``
never looking the system up (AC-4, AC-5), and a broken install (AC-8). Nothing reads the real
system zone: every row patches ``tzlocal.get_localzone_name``. No row asserts the AC-10 line, so
this file stands whether or not AC-10 is kept. "Today" is a clock frozen at 2026-02-15 12:00 UTC.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import available_timezones

import pytest

from gmail_pdf.app.ports import Deps
from gmail_pdf.app.runner import run
from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.cli import main as cli_main
from gmail_pdf.domain import messages, validation
from gmail_pdf.domain.daterange import DateRange
from gmail_pdf.domain.events import CancelToken
from gmail_pdf.domain.models import RunRequest
from gmail_pdf.infra import tz as tz_module
from tests.fakes.fake_gmail import FakeGmail
from tests.fakes.fake_time import FixedInstantClock
from tests.fixtures.builders import MessageBuilder, build_messages
from tests.support import system_zone
from tests.support.cli_inprocess import must_not_be_called, use_hook
from tests.support.mailboxes import MESSAGES_IN_RANGE_LINE, RANGE_ARGS, write_edge_mailbox
from tests.support.validation_inputs import FUTURE_END, raw

pytestmark = pytest.mark.req("FR-008", "FR-015")

NO_TZ_ARGS = RANGE_ARGS[:4]
ZONE_ERROR = "error: --tz: Unknown time zone. Use an IANA name such as Asia/Kolkata."
START_FORMAT = "error: --start: Enter the date as YYYY-MM-DD, for example 2026-01-31."
UNEXPECTED_FAILURE = "error: unexpected failure, see the run log"


@pytest.fixture(autouse=True)
def _no_hook_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test in real mode, whatever the developer's shell holds."""
    monkeypatch.delenv(ENV_FAKE_MAILBOX, raising=False)
    monkeypatch.delenv(ENV_TESTING, raising=False)


@pytest.fixture(autouse=True)
def _frozen_today(monkeypatch: pytest.MonkeyPatch) -> None:
    """Today is 2026-02-15 (12:00 UTC), whatever the machine's date and zone are."""
    clock = FixedInstantClock(datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc))
    monkeypatch.setattr(cli_main, "SystemClock", lambda: clock)


@pytest.fixture
def requests_seen(monkeypatch: pytest.MonkeyPatch) -> list[RunRequest]:
    """Every ``RunRequest`` the command line hands to the run."""
    seen: list[RunRequest] = []
    original = cli_main._execute

    def spy(request: RunRequest, deps: Deps) -> int:
        seen.append(request)
        return original(request, deps)

    monkeypatch.setattr(cli_main, "_execute", spy)
    return seen


@pytest.fixture
def build_deps_calls(monkeypatch: pytest.MonkeyPatch) -> list[None]:
    """One entry per call of the real ``build_deps``, which still runs."""
    calls: list[None] = []
    original = cli_main.build_deps

    def spy() -> Deps:
        calls.append(None)
        return original()

    monkeypatch.setattr(cli_main, "build_deps", spy)
    return calls


@pytest.fixture
def no_kolkata_data(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """A broken install: ``available_timezones()`` has no ``Asia/Kolkata`` (AC-8)."""
    without = frozenset(available_timezones()) - {validation.FALLBACK_ZONE_NAME}
    monkeypatch.setattr(validation, "available_timezones", lambda: set(without))
    validation._known_zones.cache_clear()
    yield
    validation._known_zones.cache_clear()  # the next test reads the real set again


# ----------------------------------------------------------------------------------- AC-1
@pytest.mark.req("AC-1")
@pytest.mark.parametrize("lookup", system_zone.UNRESOLVED_FORMS)
def test_an_unidentified_system_zone_gives_the_run_of_tz_asia_kolkata(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    requests_seen: list[RunRequest],
    lookup: Callable[[], str],
) -> None:
    use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))
    explicit_code = cli_main.main(RANGE_ARGS)
    explicit = capsys.readouterr()

    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lookup)
    code = cli_main.main(NO_TZ_ARGS)
    captured = capsys.readouterr()

    assert (explicit_code, code) == (0, 0)
    assert captured.out == explicit.out == MESSAGES_IN_RANGE_LINE
    assert "error:" not in captured.err
    assert ZONE_ERROR not in captured.err
    assert requests_seen[1] == requests_seen[0]
    assert requests_seen[1].tz == "Asia/Kolkata"


# ----------------------------------------------------------------------------------- AC-2
@pytest.mark.req("AC-2")
@pytest.mark.parametrize("lookup", system_zone.UNRESOLVED_FORMS)
def test_in_real_mode_the_fallback_reaches_build_deps_and_is_never_exit_two(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    build_deps_calls: list[None],
    lookup: Callable[[], str],
) -> None:
    explicit_code = cli_main.main(RANGE_ARGS)
    capsys.readouterr()
    build_deps_calls.clear()

    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lookup)
    code = cli_main.main(NO_TZ_ARGS)

    captured = capsys.readouterr()
    assert len(build_deps_calls) == 1
    assert code == explicit_code == 3  # no Gmail sign-in is wired yet
    assert ZONE_ERROR not in captured.err


# ----------------------------------------------------------------------------------- AC-3
def _four_edge_messages() -> FakeGmail:
    """Messages one second either side of 16 January in Asia/Kolkata, given in UTC."""
    builders = [
        MessageBuilder("out-before").received("2026-01-15T18:29:59", "UTC"),
        MessageBuilder("in-first").received("2026-01-15T18:30:00", "UTC"),
        MessageBuilder("in-last").received("2026-01-16T18:29:59", "UTC"),
        MessageBuilder("out-after").received("2026-01-16T18:30:00", "UTC"),
    ]
    return FakeGmail(build_messages(builder.pdf("Edge.pdf") for builder in builders))


@pytest.mark.req("AC-3")
def test_the_fallback_range_is_the_kolkata_day_and_picks_exactly_its_messages() -> None:
    clock = FixedInstantClock(datetime(2026, 2, 15, 12, 0, tzinfo=timezone.utc))
    fallback = validation.validate(raw("2026-01-16", "2026-01-16", zone=None), clock.today)
    explicit = validation.validate(
        raw("2026-01-16", "2026-01-16", zone="Asia/Kolkata"), clock.today
    )

    assert fallback.request is not None
    assert (
        fallback.request
        == explicit.request
        == RunRequest(date(2026, 1, 16), date(2026, 1, 16), "Asia/Kolkata")
    )
    date_range = DateRange.from_days(
        fallback.request.start, fallback.request.end, tz_module.resolve_zone(fallback.request.tz)
    )
    # 2026-01-16T00:00+05:30 and 2026-01-17T00:00+05:30, worked out by hand
    assert (date_range.start_epoch_s, date_range.end_epoch_s) == (1768501800, 1768588200)
    deps = Deps(gmail=_four_edge_messages(), resolve_zone=tz_module.resolve_zone)
    summary = run(fallback.request, deps, _NullSink(), CancelToken())
    assert sorted(ref.message_id for ref in summary.messages) == ["in-first", "in-last"]


class _NullSink:
    def emit(self, event: object) -> None:
        raise AssertionError("this slice emits no event")


@pytest.mark.req("AC-3")
def test_the_future_end_check_uses_today_in_kolkata_when_the_fallback_is_in_force() -> None:
    # 2026-01-16 20:00 UTC is already 2026-01-17 01:30 in Kolkata, still the 16th in UTC.
    clock = FixedInstantClock(datetime(2026, 1, 16, 20, 0, tzinfo=timezone.utc))

    today_in_kolkata = validation.validate(raw("2026-01-10", "2026-01-17", zone=None), clock.today)
    tomorrow_in_kolkata = validation.validate(
        raw("2026-01-10", "2026-01-18", zone=None), clock.today
    )
    same_dates_in_utc = validation.validate(
        raw("2026-01-10", "2026-01-17", zone="UTC"), clock.today
    )

    assert FUTURE_END not in today_in_kolkata.warnings
    assert FUTURE_END in tomorrow_in_kolkata.warnings
    assert FUTURE_END in same_dates_in_utc.warnings  # the control: UTC reads a different "today"


# ----------------------------------------------------------------------------------- AC-4
@pytest.mark.req("AC-4")
@pytest.mark.parametrize("zone", ["UTC", "Asia/Kolkata"])
@pytest.mark.parametrize("hook", [True, False], ids=["test-hook", "real-mode"])
def test_a_given_tz_never_looks_up_the_system_zone(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    requests_seen: list[RunRequest],
    zone: str,
    hook: bool,
) -> None:
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", must_not_be_called)
    if hook:
        use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main([*NO_TZ_ARGS, "--tz", zone])

    assert code == (0 if hook else 3)
    assert [request.tz for request in requests_seen] == ([zone] if hook else [])


# ----------------------------------------------------------------------------------- AC-5
@pytest.mark.req("AC-5")
@pytest.mark.parametrize("zone", ["Mars/Olympus", ""])
@pytest.mark.parametrize("hook", [True, False], ids=["test-hook", "real-mode"])
def test_a_bad_tz_is_rejected_without_a_system_lookup_and_without_the_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    zone: str,
    hook: bool,
) -> None:
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", must_not_be_called)
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)
    if hook:
        use_hook(monkeypatch, write_edge_mailbox(tmp_path / "mailbox.json"))

    code = cli_main.main([*NO_TZ_ARGS, "--tz", zone])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out, list(workdir.iterdir())) == (
        2,
        ZONE_ERROR + "\n",
        "",
        [],
    )


# ----------------------------------------------------------------------------------- AC-8
@pytest.mark.req("AC-8")
@pytest.mark.usefixtures("no_kolkata_data")
@pytest.mark.parametrize(
    "lookup",
    [
        pytest.param(system_zone.raising(LookupError("no zone key")), id="tzlocal-fails"),
        pytest.param(system_zone.reporting("Europe/London"), id="tzlocal-names-a-real-zone"),
    ],
)
def test_without_time_zone_data_and_without_tz_the_run_stops_with_the_fixed_line(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    lookup: Callable[[], str],
) -> None:
    workdir = tmp_path / "cwd"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", lookup)
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)

    code = cli_main.main(NO_TZ_ARGS)

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out, list(workdir.iterdir())) == (
        1,
        UNEXPECTED_FAILURE + "\n",
        "",
        [],
    )
    assert UNEXPECTED_FAILURE == messages.UNEXPECTED_FAILURE_LINE


@pytest.mark.req("AC-8")
@pytest.mark.usefixtures("no_kolkata_data")
def test_without_time_zone_data_a_bad_date_still_gets_its_date_line_and_exit_two(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        tz_module.tzlocal, "get_localzone_name", system_zone.raising(LookupError("no zone key"))
    )
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)

    code = cli_main.main(["--start", "x", "--end", "2026-01-31"])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, START_FORMAT + "\n", "")


@pytest.mark.req("AC-8")
@pytest.mark.usefixtures("no_kolkata_data")
def test_without_time_zone_data_a_typed_tz_keeps_the_zone_sentence(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # D-114: only the no-``--tz`` limb moves; the typed limb keeps the PGD-16 behaviour.
    monkeypatch.setattr(tz_module.tzlocal, "get_localzone_name", must_not_be_called)
    monkeypatch.setattr(cli_main, "build_deps", must_not_be_called)

    code = cli_main.main([*NO_TZ_ARGS, "--tz", "Asia/Kolkata"])

    captured = capsys.readouterr()
    assert (code, captured.err, captured.out) == (2, ZONE_ERROR + "\n", "")


# ----------------------------------------------------------------------------------- AC-9
@pytest.mark.req("AC-9")
def test_the_tz_help_line_names_the_system_zone_and_the_fallback(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli_main.main(["--help"]) == 0

    help_text = " ".join(capsys.readouterr().out.split())  # argparse wraps lines
    assert "(default: system zone, or Asia/Kolkata when it cannot be identified)." in help_text
