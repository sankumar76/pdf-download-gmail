"""PGD-14 AC-1 (pattern presence): the repository ``.gitignore`` lists every secret pattern.

The matching behaviour of the patterns, checked with ``git check-ignore``, runs a subprocess
and therefore lives in ``tests/e2e/test_gitignore_matching.py``.
"""

from __future__ import annotations

import pytest

from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("FR-004", "NFR-013", "AC-1")

GITIGNORE = REPO_ROOT / ".gitignore"

REQUIRED_SECRET_PATTERNS = (
    "secrets/",
    "*credentials*.json",
    "client_secret*.json",
    "token.json",
    ".env",
    ".env.*",
    "downloads/",
    "*.part",
    ".manifest.json*",
    ".manifest.journal",
    "logs/",
)

# Python build and test artefacts (deferred from the PGD-12 standards review to this story).
REQUIRED_ARTEFACT_PATTERNS = (
    "__pycache__/",
    "*.egg-info/",
    ".coverage",
    ".coverage.*",
    "coverage.xml",
    ".venv/",
    "venv/",
    "dist/",
    "build/",
    ".*.tmp",
)

# The lines that existed before PGD-14; the story requires that none is removed.
PRE_EXISTING_LINES = (
    ".claude/runs/",
    ".claude/settings.local.json",
    ".claude/agent-memory-local/",
    ".env",
    ".env.*",
)


def active_lines() -> list[str]:
    text = GITIGNORE.read_text(encoding="utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


@pytest.mark.parametrize("pattern", REQUIRED_SECRET_PATTERNS, ids=lambda pattern: pattern)
def test_ac1_gitignore_contains_each_required_secret_pattern(pattern: str) -> None:
    assert pattern in active_lines()


@pytest.mark.parametrize("pattern", REQUIRED_ARTEFACT_PATTERNS, ids=lambda pattern: pattern)
def test_ac1_gitignore_contains_each_python_artefact_pattern(pattern: str) -> None:
    assert pattern in active_lines()


@pytest.mark.parametrize("line", PRE_EXISTING_LINES, ids=lambda line: line)
def test_ac1_pre_existing_gitignore_lines_remain(line: str) -> None:
    assert line in active_lines()


def test_ac1_no_pattern_is_listed_twice() -> None:
    lines = [line for line in active_lines() if not line.startswith("#")]

    assert len(lines) == len(set(lines))
