"""PGD-14 AC-4: a token path outside the user profile yields a warning, never an error."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from gmail_pdf.domain import events
from gmail_pdf.infra import paths

pytestmark = pytest.mark.req("FR-004", "NFR-015", "AC-4")

EXPECTED = events.Warning(events.WarningCode.TOKEN_OUTSIDE_PROFILE)
WINDOWS_ONLY = pytest.mark.skipif(sys.platform != "win32", reason="Windows path semantics")


@pytest.fixture
def home(tmp_path: Path) -> Path:
    profile = tmp_path / "profile"
    profile.mkdir()
    return profile


def make_symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available to this account")


def test_ac4_path_inside_the_profile_gives_no_warning(home: Path) -> None:
    assert paths.token_location_warning(home / "secrets" / "token.json", home) is None


def test_ac4_path_equal_to_the_profile_gives_no_warning(home: Path) -> None:
    assert paths.token_location_warning(home, home) is None


def test_ac4_path_with_spaces_inside_the_profile_gives_no_warning(home: Path) -> None:
    assert paths.token_location_warning(home / "My Secrets" / "token.json", home) is None


def test_ac4_path_outside_the_profile_gives_the_outside_profile_warning(
    home: Path, tmp_path: Path
) -> None:
    assert paths.token_location_warning(tmp_path / "elsewhere" / "token.json", home) == EXPECTED


def test_ac4_sibling_folder_sharing_the_profile_name_prefix_is_outside(
    home: Path, tmp_path: Path
) -> None:
    sibling = tmp_path / "profile-other" / "token.json"

    assert paths.token_location_warning(sibling, home) == EXPECTED


def test_ac4_dotdot_that_leaves_the_profile_gives_the_warning(home: Path) -> None:
    escaped = home / "secrets" / ".." / ".." / "elsewhere" / "token.json"

    assert paths.token_location_warning(escaped, home) == EXPECTED


def test_ac4_dotdot_that_stays_inside_the_profile_gives_no_warning(home: Path) -> None:
    inside = home / "a" / ".." / "secrets" / "token.json"

    assert paths.token_location_warning(inside, home) is None


def test_ac4_relative_path_is_judged_against_the_working_directory(
    home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(home)

    assert paths.token_location_warning(Path("secrets") / "token.json", home) is None


def test_ac4_symlinked_profile_folder_counts_as_the_real_location(
    home: Path, tmp_path: Path
) -> None:
    link = tmp_path / "profile-link"
    make_symlink(link, home)

    assert paths.token_location_warning(link / "secrets" / "token.json", home) is None


def test_ac4_symlink_inside_the_profile_that_points_out_is_outside(
    home: Path, tmp_path: Path
) -> None:
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    link = home / "out"
    make_symlink(link, outside)

    assert paths.token_location_warning(link / "token.json", home) == EXPECTED


@pytest.mark.parametrize(
    "error",
    [
        pytest.param(OSError("injected"), id="os-error"),
        pytest.param(RuntimeError("loop"), id="loop"),
    ],
)
def test_ac4_unresolvable_path_never_raises_and_is_still_classified(
    home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    def broken_resolve(self: Path, strict: bool = False) -> Path:
        raise error

    monkeypatch.setattr(Path, "resolve", broken_resolve)

    results = (
        paths.token_location_warning(home / "token.json", home),
        paths.token_location_warning(tmp_path / "elsewhere" / "token.json", home),
    )

    assert results == (None, EXPECTED)


@WINDOWS_ONLY
def test_ac4_case_difference_on_windows_gives_no_false_warning(home: Path) -> None:
    shouted = Path(str(home / "secrets" / "token.json").swapcase())

    assert paths.token_location_warning(shouted, home) is None


@WINDOWS_ONLY
def test_ac4_other_drive_gives_the_warning() -> None:
    result = paths.token_location_warning(Path("D:/Data/token.json"), Path("C:/Users/someone"))

    assert result == EXPECTED


@WINDOWS_ONLY
def test_ac4_drive_letter_case_does_not_matter() -> None:
    result = paths.token_location_warning(
        Path("c:/Users/someone/secrets/token.json"), Path("C:/Users/someone")
    )

    assert result is None
