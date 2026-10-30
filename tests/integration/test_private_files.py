"""PGD-14 AC-2 and AC-3: private folder and file helpers against a real temporary directory.

POSIX mode bits are asserted only on the POSIX legs (Ubuntu, macOS). Everything that can be
observed without mode bits (temp-file handling, failure behaviour, which OS calls are made) runs
on every platform, with ``os.chmod`` recorded rather than trusted.

Note: ``paths.os`` is the real ``os`` module, so the fault injections below patch the function
for the whole process while the test runs. The windows are short and nothing else in these tests
calls the patched functions.
"""

from __future__ import annotations

import os
import stat
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

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
PREVIOUS_CONTENT = "previous-content"


def mode_of(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def fail_with_oserror(*_args: object, **_kwargs: object) -> None:
    raise OSError(28, "injected failure")


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


class OpenCall(NamedTuple):
    path: Path
    flags: int
    mode: int


@pytest.fixture
def temp_file_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> OpenCall:
    """Run one write and return the ``os.open`` call that created its temp file."""
    calls: list[OpenCall] = []
    real_open = os.open

    def spy(path: str | os.PathLike[str], flags: int, mode: int = 0o777) -> int:
        calls.append(OpenCall(Path(path), flags, mode))
        return real_open(path, flags, mode)

    monkeypatch.setattr(paths.os, "open", spy)

    paths.write_private_text(tmp_path / "token.json", "x")

    return calls[0]


class WrittenTree(NamedTuple):
    folder: Path
    folder_mode: int
    mode_after_first_write: int
    mode_after_overwrite: int
    content: str


@pytest.fixture(params=[0o022, 0o077], ids=["umask-022", "umask-077"])
def written_tree(request: pytest.FixtureRequest, tmp_path: Path) -> WrittenTree:
    """Create the secrets folder, write a token twice, all under the parametrized umask."""
    previous = os.umask(request.param)
    try:
        folder = paths.ensure_private_dir(tmp_path / "secrets")
        token = folder / "token.json"
        paths.write_private_text(token, "first")
        after_first = mode_of(token)
        paths.write_private_text(token, "second")
    finally:
        os.umask(previous)
    return WrittenTree(
        folder, mode_of(folder), after_first, mode_of(token), token.read_text("utf-8")
    )


# ---------------------------------------------------------------- AC-2 (POSIX modes)


@POSIX_ONLY
def test_ac2_directory_is_0700(written_tree: WrittenTree) -> None:
    assert written_tree.folder_mode == 0o700


@POSIX_ONLY
def test_ac2_token_is_0600_after_the_first_write(written_tree: WrittenTree) -> None:
    assert written_tree.mode_after_first_write == 0o600


@POSIX_ONLY
def test_ac2_token_is_still_0600_after_an_overwrite(written_tree: WrittenTree) -> None:
    assert written_tree.mode_after_overwrite == 0o600


@POSIX_ONLY
def test_ac2_overwrite_replaces_the_content(written_tree: WrittenTree) -> None:
    assert written_tree.content == "second"


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

    assert mode_of(token) == 0o600


@POSIX_ONLY
def test_ac2_token_is_0600_under_a_fully_permissive_umask(tmp_path: Path) -> None:
    previous = os.umask(0o000)
    try:
        paths.write_private_text(tmp_path / "token.json", "x")
    finally:
        os.umask(previous)

    assert mode_of(tmp_path / "token.json") == 0o600


# ---------------------------------------------------------------- AC-2 (calls, every platform)


def test_ac2_temp_file_is_created_in_the_target_folder(
    tmp_path: Path, temp_file_open: OpenCall
) -> None:
    assert temp_file_open.path.parent == tmp_path


def test_ac2_temp_file_is_created_with_mode_0600(temp_file_open: OpenCall) -> None:
    assert temp_file_open.mode == 0o600


def test_ac2_temp_file_is_created_exclusively_for_writing(temp_file_open: OpenCall) -> None:
    wanted = os.O_WRONLY | os.O_CREAT | os.O_EXCL

    assert temp_file_open.flags & wanted == wanted


def test_ac2_temp_file_name_differs_from_the_target(temp_file_open: OpenCall) -> None:
    assert temp_file_open.path.name != "token.json"


def test_ac2_posix_modes_are_asserted_on_the_directory_then_the_temp_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, recorded_chmod: list[tuple[Path, int]]
) -> None:
    monkeypatch.setattr(paths, "_APPLY_POSIX_MODES", True)

    folder = paths.ensure_private_dir(tmp_path / "secrets")
    paths.write_private_text(folder / "token.json", "x")

    seen = [(p if p == folder else p.parent, mode) for p, mode in recorded_chmod]
    assert seen == [(folder, 0o700), (folder, 0o600)]


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


def test_ac2_ensure_private_dir_returns_the_folder(tmp_path: Path) -> None:
    assert paths.ensure_private_dir(tmp_path / "secrets") == tmp_path / "secrets"


def test_ac2_ensure_private_dir_accepts_an_existing_folder(tmp_path: Path) -> None:
    paths.ensure_private_dir(tmp_path / "secrets")

    assert paths.ensure_private_dir(tmp_path / "secrets").is_dir()


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


class FailedWrite(NamedTuple):
    folder: Path
    error: PrivateFileError


@pytest.fixture(
    params=[
        pytest.param("fsync", id="mid-write-fsync"),
        pytest.param("replace", id="final-replace"),
        pytest.param("chmod", id="mode-assertion"),
    ]
)
def failed_write(
    request: pytest.FixtureRequest, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> FailedWrite:
    """Overwrite an existing token while the parametrized OS call fails."""
    monkeypatch.setattr(paths, "_APPLY_POSIX_MODES", True)
    (tmp_path / "token.json").write_text(PREVIOUS_CONTENT, encoding="utf-8")
    monkeypatch.setattr(paths.os, request.param, fail_with_oserror)

    with pytest.raises(PrivateFileError) as caught:
        paths.write_private_text(tmp_path / "token.json", SENTINEL)

    return FailedWrite(tmp_path, caught.value)


def test_ac3_failure_keeps_the_previous_content(failed_write: FailedWrite) -> None:
    assert (failed_write.folder / "token.json").read_text("utf-8") == PREVIOUS_CONTENT


def test_ac3_failure_leaves_no_temp_file(failed_write: FailedWrite) -> None:
    assert [entry.name for entry in failed_write.folder.iterdir()] == ["token.json"]


def test_ac3_failure_does_not_echo_the_content(failed_write: FailedWrite) -> None:
    assert SENTINEL not in str(failed_write.error)


def test_ac3_failure_to_create_the_temp_file_is_a_domain_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(paths.os, "open", fail_with_oserror)

    with pytest.raises(PrivateFileError):
        paths.write_private_text(tmp_path / "token.json", SENTINEL)


def test_ac3_failure_to_create_the_temp_file_leaves_the_folder_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(paths.os, "open", fail_with_oserror)

    with pytest.raises(PrivateFileError):
        paths.write_private_text(tmp_path / "token.json", SENTINEL)

    assert list(tmp_path.iterdir()) == []


def test_ac3_missing_parent_folder_is_a_domain_error(tmp_path: Path) -> None:
    with pytest.raises(PrivateFileError):
        paths.write_private_text(tmp_path / "absent" / "token.json", SENTINEL)


def test_ac3_missing_parent_folder_is_not_created_silently(tmp_path: Path) -> None:
    with pytest.raises(PrivateFileError):
        paths.write_private_text(tmp_path / "absent" / "token.json", SENTINEL)

    assert not (tmp_path / "absent").exists()


class Unencodable(NamedTuple):
    folder: Path
    error: PrivateFileError


@pytest.fixture
def unencodable(tmp_path: Path) -> Unencodable:
    with pytest.raises(PrivateFileError) as caught:
        paths.write_private_text(tmp_path / "token.json", SENTINEL + "\ud800")
    return Unencodable(tmp_path, caught.value)


def test_ac3_unencodable_text_does_not_echo_the_text(unencodable: Unencodable) -> None:
    assert SENTINEL not in str(unencodable.error)


def test_ac3_unencodable_text_does_not_chain_the_encoding_error(unencodable: Unencodable) -> None:
    assert unencodable.error.__cause__ is None


def test_ac3_unencodable_text_creates_no_file(unencodable: Unencodable) -> None:
    assert list(unencodable.folder.iterdir()) == []


@pytest.fixture
def cleanup_failure_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> str:
    """Log text of a write whose replace fails while removing the temp file fails too."""
    monkeypatch.setattr(paths.os, "replace", fail_with_oserror)
    monkeypatch.setattr(Path, "unlink", fail_with_oserror)

    with pytest.raises(PrivateFileError), caplog.at_level("WARNING", logger=paths.logger.name):
        paths.write_private_text(tmp_path / "token.json", SENTINEL)

    return caplog.text


def test_ac3_failure_to_remove_the_temp_file_is_logged(
    cleanup_failure_log: str,
) -> None:
    assert "temporary file" in cleanup_failure_log


def test_ac3_log_of_a_failed_cleanup_does_not_contain_the_content(
    cleanup_failure_log: str,
) -> None:
    assert SENTINEL not in cleanup_failure_log


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
