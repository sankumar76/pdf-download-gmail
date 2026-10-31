"""PGD-15 AC-5 and AC-6 end to end: the real command line in a child process.

Every child runs under the socket guard and in an empty working directory, so "no network call"
and "no file or folder is created" are checked, not assumed. The hook is the one of
test-strategy section 2: ``GMAIL_PDF_TESTING=1`` plus ``GMAIL_PDF_TEST_FAKE_MAILBOX``.

AC-6 keeps exit 3 (real mode) and exit 1 (hook refused, fake file unusable) in separate tests,
so the two cannot be swapped unnoticed. Names, content and the file path carry sentinels that
must appear on no surface.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from gmail_pdf.bootstrap import ENV_FAKE_MAILBOX, ENV_TESTING
from gmail_pdf.domain import messages
from tests.support import sentinels
from tests.support.mailboxes import MESSAGES_IN_RANGE_LINE, RANGE_ARGS, write_edge_mailbox
from tests.support.subprocess_env import SUPPORT_DIR, run_guarded

pytestmark = pytest.mark.req("FR-008", "FR-012")

# A sentinel in the file name and one in the file content: neither may be printed.
PATH_SENTINEL = sentinels.CLIENT_SECRET
CONTENT_SENTINEL = sentinels.REFRESH_TOKEN


class Workspace:
    """An empty working directory for the child, and a separate directory for fixture files."""

    def __init__(self, tmp_path: Path) -> None:
        self.cwd = tmp_path / "cwd"
        self.fixtures = tmp_path / "fixtures"
        self.cwd.mkdir()
        self.fixtures.mkdir()

    def mailbox_path(self) -> Path:
        return self.fixtures / f"mailbox-{PATH_SENTINEL}.json"

    def run(
        self, extra_env: dict[str, str] | None = None, args: list[str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-m", "gmail_pdf", *(RANGE_ARGS if args is None else args)]
        return run_guarded(command, self.cwd, extra_env)

    def created_files(self) -> list[str]:
        return sorted(str(p) for p in self.cwd.rglob("*"))


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    return Workspace(tmp_path)


def hook_env(path: Path, *, testing: str | None = "1") -> dict[str, str]:
    env = {ENV_FAKE_MAILBOX: str(path)}
    if testing is not None:
        env[ENV_TESTING] = testing
    return env


def assert_only_this_line_on_stderr(
    result: subprocess.CompletedProcess[str], line: str, workspace: Workspace
) -> None:
    """The shared "In every case" clause of AC-6."""
    assert result.stderr == line + "\n"
    assert result.stdout == ""
    assert "Traceback" not in result.stderr
    assert "Messages in range" not in result.stdout
    for surface in (result.stdout, result.stderr):
        assert sentinels.leaked(surface) == []
        assert PATH_SENTINEL not in surface
        assert CONTENT_SENTINEL not in surface
        assert str(workspace.fixtures) not in surface
    assert workspace.created_files() == []


# ----------------------------------------------------------------------------------- AC-5
@pytest.mark.req("AC-5")
def test_a_range_on_the_fake_mailbox_prints_the_interim_count_and_exits_zero(
    workspace: Workspace,
) -> None:
    path = write_edge_mailbox(workspace.mailbox_path())

    result = workspace.run(hook_env(path))

    assert (result.returncode, result.stdout) == (0, MESSAGES_IN_RANGE_LINE), result.stderr
    assert "error:" not in result.stderr
    assert result.stderr == ""
    assert workspace.created_files() == []


@pytest.mark.req("AC-5")
def test_a_range_without_matches_prints_a_zero_count(workspace: Workspace) -> None:
    path = write_edge_mailbox(workspace.mailbox_path())

    result = workspace.run(
        hook_env(path), ["--start", "2020-05-05", "--end", "2020-05-06", "--tz", "UTC"]
    )

    assert (result.returncode, result.stdout, result.stderr) == (
        0,
        "Messages in range: 0\n",
        "",
    )


# ----------------------------------------------------------------------------------- AC-6 (i)
@pytest.mark.req("AC-6")
def test_real_mode_exits_three_with_the_interim_sign_in_line(workspace: Workspace) -> None:
    result = workspace.run()

    assert result.returncode == 3
    assert_only_this_line_on_stderr(result, messages.SIGN_IN_UNAVAILABLE_LINE, workspace)
    assert messages.SIGN_IN_UNAVAILABLE_LINE == (
        "error: Gmail sign-in is not available in this build yet."
    )


@pytest.mark.req("AC-6")
def test_the_testing_flag_alone_is_still_real_mode_and_exits_three(workspace: Workspace) -> None:
    result = workspace.run({ENV_TESTING: "1"})

    assert result.returncode == 3
    assert_only_this_line_on_stderr(result, messages.SIGN_IN_UNAVAILABLE_LINE, workspace)


# ---------------------------------------------------------------------------------- AC-6 (ii)
REFUSED_LINE = (
    "error: GMAIL_PDF_TEST_FAKE_MAILBOX is a test-only setting and needs GMAIL_PDF_TESTING=1."
)


@pytest.mark.req("AC-6")
@pytest.mark.parametrize("testing", [None, "0", "", "true", "yes", "2"])
def test_a_refused_hook_exits_one_with_the_fixed_line(
    workspace: Workspace, testing: str | None
) -> None:
    path = write_edge_mailbox(workspace.mailbox_path())

    result = workspace.run(hook_env(path, testing=testing))

    assert result.returncode == 1
    assert_only_this_line_on_stderr(result, REFUSED_LINE, workspace)
    assert messages.FAKE_MAILBOX_HOOK_REFUSED_LINE == REFUSED_LINE


# --------------------------------------------------------------------------------- AC-6 (iii)
UNREADABLE_LINE = (
    "error: The fake mailbox file could not be read; check GMAIL_PDF_TEST_FAKE_MAILBOX."
)
NOT_IMPORTABLE_LINE = (
    "error: The fake mailbox is only available from a source checkout (tests/ not importable)."
)


def _missing(workspace: Workspace) -> Path:
    return workspace.mailbox_path()


def _directory(workspace: Workspace) -> Path:
    path = workspace.mailbox_path()
    path.mkdir()
    return path


def _content(data: bytes) -> Callable[[Workspace], Path]:
    def make(workspace: Workspace) -> Path:
        path = workspace.mailbox_path()
        path.write_bytes(data)
        return path

    return make


def _unreadable(workspace: Workspace) -> Path:
    path = write_edge_mailbox(workspace.mailbox_path())
    path.chmod(0)
    return path


SECRET_JSON = f'{{"format": 99, "note": "{CONTENT_SENTINEL}"}}'.encode()
NO_ID_JSON = (
    b'{"format": 1, "messages": [{"resource": {"note": "'
    + CONTENT_SENTINEL.encode()
    + b'"}, "attachments": {}}]}'
)
UNUSABLE_FILES = [
    pytest.param(_missing, id="missing"),
    pytest.param(_directory, id="directory"),
    pytest.param(_content(b'{"format": 1, "messages": ['), id="bad-json"),
    pytest.param(_content(SECRET_JSON), id="wrong-format-version"),
    pytest.param(_content(NO_ID_JSON), id="message-without-id"),
    pytest.param(_content(b'{"format": 1, "messages": [\xff\xfe]}'), id="invalid-utf-8"),
    pytest.param(_content(b"\xef\xbb\xbf" + SECRET_JSON), id="utf-8-bom"),
    pytest.param(_content(b"[" * 200_000), id="deeply-nested"),
    pytest.param(
        _unreadable,
        id="unreadable",
        marks=pytest.mark.skipif(
            os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0),
            reason="needs POSIX permission bits and a non-root user",
        ),
    ),
]


@pytest.mark.req("AC-6")
@pytest.mark.parametrize("make_file", UNUSABLE_FILES)
def test_an_unusable_fake_mailbox_file_exits_one_and_never_falls_through_to_real_mode(
    workspace: Workspace, make_file: Callable[[Workspace], Path]
) -> None:
    path = make_file(workspace)

    result = workspace.run(hook_env(path))

    assert result.returncode == 1
    assert_only_this_line_on_stderr(result, UNREADABLE_LINE, workspace)
    assert messages.SIGN_IN_UNAVAILABLE_LINE not in result.stderr
    assert messages.FAKE_MAILBOX_UNREADABLE_LINE == UNREADABLE_LINE


@pytest.mark.req("AC-6")
def test_without_a_tests_package_the_line_says_source_checkout_and_exits_one(
    workspace: Workspace,
) -> None:
    path = write_edge_mailbox(workspace.mailbox_path())
    # An installed wheel has no ``tests`` package: leave only the socket guard on the path
    # (the child still finds ``gmail_pdf`` through the editable install).
    env = {**hook_env(path), "PYTHONPATH": str(SUPPORT_DIR)}

    result = workspace.run(env)

    assert result.returncode == 1
    assert_only_this_line_on_stderr(result, NOT_IMPORTABLE_LINE, workspace)
    assert messages.FAKE_MAILBOX_NOT_IMPORTABLE_LINE == NOT_IMPORTABLE_LINE


@pytest.mark.req("AC-6")
def test_exit_three_is_used_only_for_real_mode_and_exit_one_only_for_hook_failures(
    workspace: Workspace,
) -> None:
    good = write_edge_mailbox(workspace.mailbox_path())
    bad = workspace.fixtures / "absent.json"

    codes = {
        "real-mode": workspace.run().returncode,
        "hook-refused": workspace.run(hook_env(good, testing=None)).returncode,
        "file-unusable": workspace.run(hook_env(bad)).returncode,
        "success": workspace.run(hook_env(good)).returncode,
    }

    assert codes == {"real-mode": 3, "hook-refused": 1, "file-unusable": 1, "success": 0}
