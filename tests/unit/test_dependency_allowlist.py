"""AC-5: runtime dependencies in pyproject.toml must be on the ADR-002 allow-list."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:  # Python 3.10: tomli is a dev dependency (pyproject.toml, extra "dev")
    import tomli as tomllib

from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("NFR-023", "AC-5")

# ADR-002 "Runtime allow-list (exhaustive)", normalised names.
ALLOW_LIST = frozenset(
    {
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
        "tzdata",
        "tzlocal",
        "pyside6-essentials",
    }
)
# What must be present now. PySide6-Essentials joins with the GUI stories once ADR-001 is
# Accepted (condition C11); until then adding it is a violation of this story's scope.
CURRENT_RUNTIME = frozenset(ALLOW_LIST - {"pyside6-essentials"})

_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def normalise(name: str) -> str:
    """PEP 503 name normalisation."""
    return re.sub(r"[-_.]+", "-", name).lower()


def runtime_dependencies(pyproject_text: str) -> set[str]:
    """Normalised names of ``[project].dependencies``."""
    data = tomllib.loads(pyproject_text)
    names: set[str] = set()
    for requirement in data["project"].get("dependencies", []):
        match = _NAME.match(requirement)
        assert match, f"cannot parse requirement {requirement!r}"
        names.add(normalise(match.group(1)))
    return names


def violations(pyproject_text: str) -> set[str]:
    """Declared runtime dependencies that are not on the allow-list."""
    return runtime_dependencies(pyproject_text) - ALLOW_LIST


PYPROJECT = REPO_ROOT / "pyproject.toml"


def test_declared_runtime_dependencies_are_exactly_the_adr_002_set_present_now() -> None:
    declared = runtime_dependencies(PYPROJECT.read_text(encoding="utf-8"))

    assert declared == CURRENT_RUNTIME


def test_no_declared_runtime_dependency_is_off_the_allow_list() -> None:
    assert violations(PYPROJECT.read_text(encoding="utf-8")) == set()


def test_pyside6_is_not_added_while_adr_001_is_proposed() -> None:
    declared = runtime_dependencies(PYPROJECT.read_text(encoding="utf-8"))

    assert not {name for name in declared if name.startswith("pyside6")}


def test_adding_requests_to_a_temporary_copy_fails_the_check(tmp_path: Path) -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    patched = text.replace('    "tzdata",\n', '    "tzdata",\n    "requests>=2",\n', 1)
    assert patched != text, "fixture drifted: could not inject a dependency"
    copy = tmp_path / "pyproject.toml"
    copy.write_text(patched, encoding="utf-8")

    assert violations(copy.read_text(encoding="utf-8")) == {"requests"}


@pytest.mark.parametrize(
    "requirement",
    ["requests", "Requests>=2", "PySide6", "PyYAML", "python-dotenv", "tzlocal-extra"],
)
def test_other_packages_are_rejected_including_look_alike_names(requirement: str) -> None:
    text = f'[project]\nname = "x"\ndependencies = ["tzdata", "{requirement}"]\n'

    assert violations(text) == {normalise(requirement.split(">")[0])}


def test_name_normalisation_accepts_equivalent_spellings() -> None:
    text = '[project]\nname = "x"\ndependencies = ["Google_Auth", "google.api.python.client>=2"]\n'

    assert violations(text) == set()


def test_requirements_files_pin_every_declared_dependency_with_hashes() -> None:
    declared = runtime_dependencies(PYPROJECT.read_text(encoding="utf-8"))
    for filename in ("requirements.txt", "requirements-dev.txt"):
        text = (REPO_ROOT / filename).read_text(encoding="utf-8")
        pinned = {normalise(m) for m in re.findall(r"^([A-Za-z0-9._-]+)==", text, re.MULTILINE)}

        assert declared <= pinned, filename
        assert "--hash=sha256:" in text, filename
        # every pin is followed by at least one hash (no unhashed pin under --require-hashes)
        for block in re.split(r"\n(?=[A-Za-z0-9._-]+==)", text):
            if re.match(r"[A-Za-z0-9._-]+==", block):
                assert "--hash=sha256:" in block, block.splitlines()[0]
