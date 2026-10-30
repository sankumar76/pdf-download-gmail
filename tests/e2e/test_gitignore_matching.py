"""PGD-14 AC-1 and AC-5: ``git`` itself agrees with the ``.gitignore`` patterns.

Matching is checked in a scratch repository that holds a copy of the repository ``.gitignore``,
so the result does not depend on the developer's global ignore rules or on the working tree.
The tracked-files check runs against the real repository.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Sequence
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
)

# Paths that must stay trackable: guards against patterns that are too broad.
TRACKABLE_PATHS = (
    "gmail_pdf/infra/paths.py",
    "tests/unit/test_gitignore_patterns.py",
    "docs/04-architecture/adr/ADR-003-token-storage-and-secrets.md",
    "pyproject.toml",
    ".gitignore",
)


def git(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run git with the user and system configuration switched off."""
    assert GIT is not None
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(
        [GIT, *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_S,
        check=False,
    )


@pytest.fixture(scope="module")
def scratch_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    repo = tmp_path_factory.mktemp("gitignore-repo")
    shutil.copyfile(REPO_ROOT / ".gitignore", repo / ".gitignore")
    init = git(["init", "-q"], repo)
    assert init.returncode == 0, init.stderr
    return repo


@requires_git
@pytest.mark.parametrize("sample", IGNORED_PATHS, ids=lambda sample: sample)
def test_ac1_git_ignores_secret_and_artefact_paths(scratch_repo: Path, sample: str) -> None:
    result = git(["check-ignore", "-q", "--no-index", sample], scratch_repo)

    assert result.returncode == 0, f"{sample} is not ignored"


@requires_git
@pytest.mark.parametrize("sample", TRACKABLE_PATHS, ids=lambda sample: sample)
def test_ac1_git_does_not_ignore_ordinary_project_files(scratch_repo: Path, sample: str) -> None:
    result = git(["check-ignore", "-q", "--no-index", sample], scratch_repo)

    assert result.returncode == 1, f"{sample} is wrongly ignored"


@requires_git
def test_ac5_no_tracked_file_matches_an_ignored_pattern() -> None:
    inside = git(["rev-parse", "--is-inside-work-tree"], REPO_ROOT)
    if inside.returncode != 0:
        pytest.skip("not a git work tree (for example an unpacked source archive)")

    # -c: tracked files, -i: that match the ignore rules.
    result = git(["ls-files", "-c", "-i", "--exclude-standard"], REPO_ROOT)

    assert (result.returncode, result.stdout.split()) == (0, [])
