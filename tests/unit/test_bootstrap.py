"""AC-9: the fake-mailbox hook is refused without GMAIL_PDF_TESTING=1 and works with it."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from gmail_pdf import bootstrap
from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING, Deps, build_deps
from gmail_pdf.domain.errors import (
    AdapterUnavailableError,
    FakeMailboxHookRefusedError,
    GmailPdfError,
)
from tests.fakes.fake_gmail import FakeGmail, dump_fake_gmail_to_json_file
from tests.fixtures.canonical import rd_example_table
from tests.support.subprocess_env import REPO_ROOT, guarded_env

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


def test_missing_mailbox_file_raises_an_os_error(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        build_deps({ENV_FAKE_MAILBOX: str(tmp_path / "absent.json"), ENV_TESTING: "1"})


def test_unusable_fake_module_is_reported_as_unavailable(
    monkeypatch: pytest.MonkeyPatch, mailbox_file: Path
) -> None:
    monkeypatch.setattr(bootstrap, "_FAKE_MODULE", "tests.fakes.does_not_exist")

    with pytest.raises(AdapterUnavailableError, match="source checkout"):
        build_deps({ENV_FAKE_MAILBOX: str(mailbox_file), ENV_TESTING: "1"})


def test_hook_works_across_a_process_boundary(tmp_path: Path, mailbox_file: Path) -> None:
    """The e2e pattern later stories use: a child process builds Deps from the environment."""
    code = (
        "from gmail_pdf.bootstrap import build_deps\nprint(len(build_deps().gmail.message_ids))\n"
    )
    env = guarded_env({ENV_FAKE_MAILBOX: str(mailbox_file), ENV_TESTING: "1"})

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.stdout.strip() == "6", result.stderr
    assert json.loads(mailbox_file.read_text(encoding="utf-8"))["format"] == 1
