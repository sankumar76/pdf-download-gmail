"""PGD-14 AC-2 and AC-3: private folder and file helpers against a real temporary directory.

POSIX mode bits are asserted only on the POSIX legs (Ubuntu, macOS). Everything that can be
observed without mode bits (temp-file handling, failure behaviour, which OS calls are made) runs
on every platform, with ``os.chmod`` recorded rather than trusted.
"""

from __future__ import annotations

import os
import stat
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from gmail_pdf.domain.errors import GmailPdfError, PrivateFileError
from gmail_pdf.infra import paths

pytestmark = pytest.mark.req("FR-004", "NFR-013")

POSIX_ONLY = pytest.mark.skipif(
    sys.platform == "win32",
    reason="POSIX mode bits are not meaningful on Windows; Windows relies on the profile ACL",
)

# A placeholder, not a credential: the tests only need a recognisable string to look for.
SENTINEL = "PLACEHOLDER-TOKEN-CONTENT-NOT-A-SECRET"


def mode_of(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


@pytest.fixture
def recorded_chmod(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Path, int]]:
    """Wrap ``os.chmod`` so the calls made by the helpers can be inspected on any platform."""
    calls: list[tuple[Path, int]] = []
    real_chmod = os.chmod

    def spy(path: str | os.PathLike[str], mode: int) -> None:
        calls.append((Path(path), mode))
        real_chmod(path, mode)

    monkeypatch.setattr(paths.os, "chmod", spy)
    return calls


@pytest.fixture
def recorded_opens(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Path, int, int]]:
    """Wrap ``os.open`` to capture (path, flags, mode) of every file the helpers create."""
    calls: list[tuple[Path, int, int]] = []
    real_open = os.open

    def spy(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        calls.append((Path(path), flags, mode))
        return real_open(path, flags, mode)

    monkeypatch.setattr(paths.os, "open", spy)
    return calls


def fail_with_oserror(*_args: object, **_kwargs: object) -> None:
    raise OSError(28, "injected failure")


# ---------------------------------------------------------------- AC-2 (POSIX modes)


@POSIX_ONLY
@pytest.mark.parametrize("umask", [0o022, 0o077], ids=["umask-022", "umask-077"])
def test_ac2_directory_is_0700_and_token_is_0600_including_after_overwrite(
    tmp_path: Path, umask: int
) -> None:
    previous = os.umask(umask)
    try:
        secrets_dir = paths.ensure_private_dir(tmp_path / "secrets")
        token = secrets_dir / "token.json"
        paths.write_private_text(token, "first")
        first_mode = mode_of(token)
        paths.write_private_text(token, "second")
    finally:
        os.umask(previous)

    assert (mode_of(secrets_dir), first_mode, mode_of(token), token.read_text("utf-8")) == (
        0o700,
        0o600,
        0o600,
        "second",
    )


@POSIX_ONLY
def test_ac2_wider_existing_directory_is_tightened_to_0700(tmp_path: Path) -> None:
    folder = tmp_path / "secrets"
    folder.mkdir(mode=0o755)
    folder.chmod(0o755)

    paths.ensure_private_dir(folder)

    assert mode_of(folder) == 0o700


@POSIX_ONLY
def test_ac2_wider_existing_token_file_is_replaced_by_a_0600_file(tmp_path: Path) -> None:
    token = tmp_path / "token.json"
    token.write_text("old", encoding="utf-8")
    token.chmod(0o644)

    paths.write_private_text(token, "new")

    assert (mode_of(token), token.read_text("utf-8")) == (0o600, "new")


@POSIX_ONLY
def test_ac2_token_is_0600_under_a_fully_permissive_umask(tmp_path: Path) -> None:
    previous = os.umask(0o000)
    try:
        paths.write_private_text(tmp_path / "token.json", "x")
    finally:
        os.umask(previous)

    assert mode_of(tmp_path / "token.json") == 0o600


# ---------------------------------------------------------------- AC-2 (calls, every platform)


def test_ac2_temp_file_is_created_exclusively_with_mode_0600_next_to_the_target(
    tmp_path: Path, recorded_opens: list[tuple[Path, int, int]]
) -> None:
    target = tmp_path / "token.json"

    paths.write_private_text(target, "x")

    (temp_path, flags, mode) = recorded_opens[0]
    assert (temp_path.parent, temp_path != target, mode) == (tmp_path, True, 0o600)
    assert flags & os.O_EXCL and flags & os.O_CREAT and flags & os.O_WRONLY


def test_ac2_posix_modes_are_asserted_on_the_directory_and_the_temp_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, recorded_chmod: list[tuple[Path, int]]
) -> None:
    monkeypatch.setattr(paths, "_APPLY_POSIX_MODES", True)

    folder = paths.ensure_private_dir(tmp_path / "secrets")
    paths.write_private_text(folder / "token.json", "x")

    assert [mode for _, mode in recorded_chmod] == [0o700, 0o600]
    assert recorded_chmod[0][0] == folder
    assert recorded_chmod[1][0].parent == folder


def test_ac2_no_permission_calls_are_made_where_the_profile_acl_applies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, recorded_chmod: list[tuple[Path, int]]
) -> None:
    monkeypatch.setattr(paths, "_APPLY_POSIX_MODES", False)

    folder = paths.ensure_private_dir(tmp_path / "secrets")
    paths.write_private_text(folder / "token.json", "x")

    assert recorded_chmod == []


def test_ac2_missing_parents_are_created(tmp_path: Path) -> None:
    folder = paths.ensure_private_dir(tmp_path / "a" / "b" / "secrets")

    assert folder.is_dir()


def test_ac2_ensure_private_dir_is_idempotent(tmp_path: Path) -> None:
    first = paths.ensure_private_dir(tmp_path / "secrets")
    second = paths.ensure_private_dir(tmp_path / "secrets")

    assert first == second == tmp_path / "secrets"


def test_ac2_text_is_written_as_utf8_without_newline_translation(tmp_path: Path) -> None:
    target = tmp_path / "token.json"

    paths.write_private_text(target, "line1\nline2\né")

    assert target.read_bytes() == b"line1\nline2\n\xc3\xa9"


def test_ac2_ensure_private_dir_over_a_file_raises_a_domain_error(tmp_path: Path) -> None:
    blocker = tmp_path / "secrets"
    blocker.write_text("not a folder", encoding="utf-8")

    with pytest.raises(PrivateFileError):
        paths.ensure_private_dir(blocker)


def test_ac2_ensure_private_dir_chmod_failure_is_translated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(paths, "_APPLY_POSIX_MODES", True)
    monkeypatch.setattr(paths.os, "chmod", fail_with_oserror)

    with pytest.raises(PrivateFileError):
        paths.ensure_private_dir(tmp_path / "secrets")


# ---------------------------------------------------------------- AC-3 (failure behaviour)


@pytest.mark.parametrize(
    "failing_call",
    [
        pytest.param("fsync", id="mid-write-fsync"),
        pytest.param("replace", id="final-replace"),
        pytest.param("chmod", id="mode-assertion"),
    ],
)
def test_ac3_failure_keeps_old_content_leaves_no_temp_and_hides_the_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failing_call: str
) -> None:
    monkeypatch.setattr(paths, "_APPLY_POSIX_MODES", True)
    target = tmp_path / "token.json"
    target.write_text("previous-content", encoding="utf-8")
    monkeypatch.setattr(paths.os, failing_call, fail_with_oserror)

    with pytest.raises(PrivateFileError) as caught:
        paths.write_private_text(target, SENTINEL)

    assert target.read_text("utf-8") == "previous-content"
    assert [entry.name for entry in tmp_path.iterdir()] == ["token.json"]
    assert SENTINEL not in str(caught.value)
    assert isinstance(caught.value, GmailPdfError)


def test_ac3_failure_to_create_the_temp_file_is_a_domain_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(paths.os, "open", fail_with_oserror)

    with pytest.raises(PrivateFileError):
        paths.write_private_text(tmp_path / "token.json", SENTINEL)

    assert list(tmp_path.iterdir()) == []


def test_ac3_missing_parent_folder_is_a_domain_error_not_a_silent_create(tmp_path: Path) -> None:
    with pytest.raises(PrivateFileError):
        paths.write_private_text(tmp_path / "absent" / "token.json", SENTINEL)

    assert not (tmp_path / "absent").exists()


def test_ac3_unencodable_text_is_a_domain_error_that_does_not_echo_the_text(
    tmp_path: Path,
) -> None:
    with pytest.raises(PrivateFileError) as caught:
        paths.write_private_text(tmp_path / "token.json", SENTINEL + "\ud800")

    assert SENTINEL not in str(caught.value)
    assert caught.value.__cause__ is None
    assert list(tmp_path.iterdir()) == []


def test_ac3_failure_to_remove_the_temp_file_is_logged_and_the_original_error_is_raised(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(paths.os, "replace", fail_with_oserror)
    monkeypatch.setattr(Path, "unlink", fail_with_oserror)

    with pytest.raises(PrivateFileError), caplog.at_level("WARNING", logger=paths.logger.name):
        paths.write_private_text(tmp_path / "token.json", SENTINEL)

    assert SENTINEL not in caplog.text
    assert "temporary file" in caplog.text


@pytest.mark.parametrize(
    "operation",
    [
        pytest.param(lambda folder: paths.ensure_private_dir(folder / "x"), id="ensure-dir"),
        pytest.param(lambda folder: paths.write_private_text(folder / "t", SENTINEL), id="write"),
    ],
)
def test_ac3_helpers_raise_only_application_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: Callable[[Path], object]
) -> None:
    monkeypatch.setattr(paths.os, "open", fail_with_oserror)
    monkeypatch.setattr(Path, "mkdir", fail_with_oserror)

    with pytest.raises(GmailPdfError):
        operation(tmp_path)
