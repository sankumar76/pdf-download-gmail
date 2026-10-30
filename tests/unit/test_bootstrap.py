"""AC-9: the fake-mailbox hook is refused without GMAIL_PDF_TESTING=1 and works with it."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from gmail_pdf import bootstrap
from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING, Deps, build_deps
from gmail_pdf.domain.errors import (
    AdapterUnavailableError,
    FakeMailboxHookRefusedError,
    GmailPdfError,
)
from tests.fakes.fake_gmail import FakeGmail
from tests.fakes.fake_gmail_json import dump_fake_gmail_to_json_file
from tests.fixtures.canonical import rd_example_table

pytestmark = pytest.mark.req("NFR-014", "AC-9")


@pytest.fixture
def mailbox_file(tmp_path: Path) -> Path:
    path = tmp_path / "mailbox.json"
    dump_fake_gmail_to_json_file(FakeGmail([row.message for row in rd_example_table()]), path)
    return path


def test_hook_is_refused_without_the_testing_flag(mailbox_file: Path) -> None:
    with pytest.raises(FakeMailboxHookRefusedError, match=ENV_TESTING):
        build_deps({ENV_FAKE_MAILBOX: str(mailbox_file)})


@pytest.mark.parametrize("flag", ["0", "", "true", "yes", "2"])
def test_hook_is_refused_unless_the_flag_is_exactly_one(mailbox_file: Path, flag: str) -> None:
    with pytest.raises(FakeMailboxHookRefusedError):
        build_deps({ENV_FAKE_MAILBOX: str(mailbox_file), ENV_TESTING: flag})


def test_refusal_does_not_echo_the_file_path(mailbox_file: Path) -> None:
    with pytest.raises(GmailPdfError) as exc_info:
        build_deps({ENV_FAKE_MAILBOX: str(mailbox_file)})

    assert str(mailbox_file) not in str(exc_info.value)


def test_hook_returns_the_fake_mailbox_loaded_from_the_named_file(mailbox_file: Path) -> None:
    deps = build_deps({ENV_FAKE_MAILBOX: str(mailbox_file), ENV_TESTING: "1"})

    assert isinstance(deps, Deps)
    assert isinstance(deps.gmail, FakeGmail)
    assert len(deps.gmail.message_ids) == 6
    assert deps.gmail.get_message("m-0121")["id"] == "m-0121"


def test_without_any_hook_variable_no_adapter_is_wired_yet() -> None:
    with pytest.raises(AdapterUnavailableError):
        build_deps({})
    with pytest.raises(AdapterUnavailableError):
        build_deps({ENV_TESTING: "1"})


def test_empty_hook_variable_is_treated_as_unset() -> None:
    with pytest.raises(AdapterUnavailableError):
        build_deps({ENV_FAKE_MAILBOX: ""})


def test_build_deps_reads_os_environ_by_default(
    monkeypatch: pytest.MonkeyPatch, mailbox_file: Path
) -> None:
    monkeypatch.setenv(ENV_FAKE_MAILBOX, str(mailbox_file))
    monkeypatch.setenv(ENV_TESTING, "1")

    assert isinstance(build_deps().gmail, FakeGmail)


def test_missing_mailbox_file_is_reported_as_unavailable(tmp_path: Path) -> None:
    with pytest.raises(AdapterUnavailableError, match="could not be read"):
        build_deps({ENV_FAKE_MAILBOX: str(tmp_path / "absent.json"), ENV_TESTING: "1"})


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("{not json", id="invalid-json"),
        pytest.param("[]", id="not-an-object"),
        pytest.param('{"format": 99, "messages": []}', id="unsupported-format"),
    ],
)
def test_unparsable_mailbox_file_is_reported_without_echoing_the_path(
    tmp_path: Path, content: str
) -> None:
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(AdapterUnavailableError) as exc_info:
        build_deps({ENV_FAKE_MAILBOX: str(path), ENV_TESTING: "1"})

    assert str(path) not in str(exc_info.value)


def test_unusable_fake_module_is_reported_as_unavailable(
    monkeypatch: pytest.MonkeyPatch, mailbox_file: Path
) -> None:
    monkeypatch.setattr(bootstrap, "_FAKE_MODULE", "tests.fakes.does_not_exist")

    with pytest.raises(AdapterUnavailableError, match="source checkout"):
        build_deps({ENV_FAKE_MAILBOX: str(mailbox_file), ENV_TESTING: "1"})


def test_a_missing_dependency_inside_the_fake_is_not_reported_as_a_missing_checkout(
    monkeypatch: pytest.MonkeyPatch, mailbox_file: Path
) -> None:
    def broken_import(name: str) -> object:
        raise ModuleNotFoundError("No module named 'tests.fixtures.x'", name="tests.fixtures.x")

    monkeypatch.setattr(importlib, "import_module", broken_import)

    with pytest.raises(ModuleNotFoundError, match="tests.fixtures.x"):
        build_deps({ENV_FAKE_MAILBOX: str(mailbox_file), ENV_TESTING: "1"})
