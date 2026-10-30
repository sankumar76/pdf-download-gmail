"""PGD-14 AC-1 and AC-5: ``git`` itself agrees with the ``.gitignore`` patterns.

Matching is checked in a scratch repository that holds a copy of the repository ``.gitignore``.
Every git call is isolated from the developer's own configuration: user-level and system config
are switched off, ``HOME``/``XDG_CONFIG_HOME``/``USERPROFILE`` point at an empty folder (so the
default user-level ignore file ``$XDG_CONFIG_HOME/git/ignore`` is not found) and
``core.excludesFile`` points at a file that does not exist. The tracked-files check
(``--exclude-per-directory``) reads only the repository's own ``.gitignore`` files, not
``.git/info/exclude`` or user-level rules.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from tests.support.subprocess_env import REPO_ROOT, SUBPROCESS_TIMEOUT_S

pytestmark = pytest.mark.req("FR-004", "NFR-013", "AC-1", "AC-5")

GIT = shutil.which("git")
requires_git = pytest.mark.skipif(GIT is None, reason="git is not installed")

# Paths that must be ignored. Names are placeholders, never real credentials.
IGNORED_PATHS = (
    "secrets/credentials.json",
    "secrets/token.json",
    "my_credentials_2.json",
    "client_secret_123.apps.googleusercontent.com.json",
    "downloads/20260115_Invoice.pdf",
    "token.json",
    "nested/dir/token.json",
    ".env",
    ".env.local",
    "report.pdf.part",
    ".manifest.json",
    ".manifest.json.bak",
    ".manifest.journal",
    "logs/run-1.log",
    "gmail_pdf/__pycache__/paths.cpython-312.pyc",
    "gmail_pdf.egg-info/PKG-INFO",
    ".coverage",
    ".coverage.win-312",
    "coverage.xml",
    ".venv/pyvenv.cfg",
    "venv/pyvenv.cfg",
    "dist/gmail_pdf-0.9.0-py3-none-any.whl",
    "build/lib/gmail_pdf/__init__.py",
    ".token.json.ab12cd34ef56ab78.tmp",
    "secrets/.token.json.ab12cd34ef56ab78.tmp",
)

# Paths that must stay trackable: guards against patterns that are too broad.
TRACKABLE_PATHS = (
    "gmail_pdf/infra/paths.py",
    "tests/unit/test_gitignore_patterns.py",
    "docs/04-architecture/adr/ADR-003-token-storage-and-secrets.md",
    "pyproject.toml",
    ".gitignore",
    ".coveragerc",
)


def isolated_env(home: Path) -> Mapping[str, str]:
    """Process environment with every user-level git setting pointed at an empty folder."""
    return dict(
        os.environ,
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        HOME=str(home),
        USERPROFILE=str(home),
        XDG_CONFIG_HOME=str(home),
    )


def git(args: Sequence[str], cwd: Path, home: Path) -> subprocess.CompletedProcess[str]:
    """Run git isolated from the developer's configuration (see the module docstring)."""
    assert GIT is not None
    no_user_excludes = f"core.excludesFile={home / 'no-such-excludes-file'}"
    return subprocess.run(
        [GIT, "-c", no_user_excludes, *args],
        cwd=cwd,
        env=isolated_env(home),
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_S,
        check=False,
    )


def tracked_files_matching_gitignore(repo: Path, home: Path) -> list[str]:
    """Tracked files that the repository's own ``.gitignore`` files would ignore."""
    result = git(["ls-files", "-c", "-i", "--exclude-per-directory=.gitignore"], repo, home)
    assert result.returncode == 0, result.stderr
    return result.stdout.split()


def new_repo(parent: Path, gitignore_text: str, home: Path) -> Path:
    repo = parent / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text(gitignore_text, encoding="utf-8")
    init = git(["init", "-q"], repo, home)
    assert init.returncode == 0, init.stderr
    return repo


@pytest.fixture(scope="module")
def quiet_home(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("git-home")


@pytest.fixture(scope="module")
def scratch_repo(tmp_path_factory: pytest.TempPathFactory, quiet_home: Path) -> Path:
    text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    return new_repo(tmp_path_factory.mktemp("gitignore-repo"), text, quiet_home)


# ---------------------------------------------------------------- AC-1


@requires_git
@pytest.mark.parametrize("sample", IGNORED_PATHS, ids=lambda sample: sample)
def test_ac1_git_ignores_secret_and_artefact_paths(
    scratch_repo: Path, quiet_home: Path, sample: str
) -> None:
    result = git(["check-ignore", "-q", "--no-index", sample], scratch_repo, quiet_home)

    assert result.returncode == 0, f"{sample} is not ignored"


@requires_git
@pytest.mark.parametrize("sample", TRACKABLE_PATHS, ids=lambda sample: sample)
def test_ac1_git_does_not_ignore_ordinary_project_files(
    scratch_repo: Path, quiet_home: Path, sample: str
) -> None:
    result = git(["check-ignore", "-q", "--no-index", sample], scratch_repo, quiet_home)

    assert result.returncode == 1, f"{sample} is wrongly ignored"


# ---------------------------------------------------------------- isolation from user config


@pytest.fixture
def user_level_ignore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Mapping[str, str]]:
    """A fake user profile whose default git ignore file lists ``token.json``."""
    profile = tmp_path / "profile"
    (profile / "git").mkdir(parents=True)
    (profile / "git" / "ignore").write_text("token.json\n", encoding="utf-8")
    for name in ("HOME", "USERPROFILE", "XDG_CONFIG_HOME"):
        monkeypatch.setenv(name, str(profile))
    return profile, dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


@requires_git
def test_isolation_probe_user_level_ignore_file_is_effective_without_isolation(
    tmp_path: Path, quiet_home: Path, user_level_ignore: tuple[Path, Mapping[str, str]]
) -> None:
    """Control: proves the probe would catch a leak, by showing git does read that file."""
    assert GIT is not None
    repo = new_repo(tmp_path, "# no token pattern here\n", quiet_home)

    unisolated = subprocess.run(
        [GIT, "check-ignore", "-q", "--no-index", "token.json"],
        cwd=repo,
        env=user_level_ignore[1],
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_S,
        check=False,
    )

    assert unisolated.returncode == 0


@requires_git
def test_isolation_user_level_ignore_file_does_not_affect_the_result(
    tmp_path: Path, quiet_home: Path, user_level_ignore: tuple[Path, Mapping[str, str]]
) -> None:
    repo = new_repo(tmp_path, "# no token pattern here\n", quiet_home)

    result = git(["check-ignore", "-q", "--no-index", "token.json"], repo, quiet_home)

    assert result.returncode == 1


# ---------------------------------------------------------------- AC-5


@requires_git
def test_ac5_no_tracked_file_matches_an_ignored_pattern(quiet_home: Path) -> None:
    inside = git(["rev-parse", "--is-inside-work-tree"], REPO_ROOT, quiet_home)
    if inside.returncode != 0:
        pytest.skip("not a git work tree (for example an unpacked source archive)")

    assert tracked_files_matching_gitignore(REPO_ROOT, quiet_home) == []


@requires_git
def test_ac5_checker_reports_a_tracked_file_that_the_gitignore_matches(
    tmp_path: Path, quiet_home: Path
) -> None:
    repo = new_repo(tmp_path, "token.json\n", quiet_home)
    (repo / "token.json").write_text("{}", encoding="utf-8")
    added = git(["add", "-f", "token.json"], repo, quiet_home)
    assert added.returncode == 0, added.stderr

    assert tracked_files_matching_gitignore(repo, quiet_home) == ["token.json"]


@requires_git
def test_ac5_checker_ignores_a_per_clone_exclude_file(tmp_path: Path, quiet_home: Path) -> None:
    repo = new_repo(tmp_path, "# nothing ignored\n", quiet_home)
    (repo / ".git" / "info" / "exclude").write_text("notes.txt\n", encoding="utf-8")
    (repo / "notes.txt").write_text("x", encoding="utf-8")
    added = git(["add", "-f", "notes.txt"], repo, quiet_home)
    assert added.returncode == 0, added.stderr

    assert tracked_files_matching_gitignore(repo, quiet_home) == []
