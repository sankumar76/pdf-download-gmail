"""AC-6: layering rules of architecture sections 4.1 and 10.2, enforced with an AST walk.

Rules (``module`` is the dotted name, e.g. ``gmail_pdf.infra.auth``):

* ``domain`` imports only ``domain`` from this package and nothing outside the standard library.
* ``app`` imports only ``domain`` (and itself) from this package.
* Only ``infra/gmail_gateway.py`` and ``infra/auth.py`` import Google libraries.
* Only ``gui/**`` imports PySide6.
* ``cli`` never imports ``googleapiclient`` or ``google.*``.
"""

from __future__ import annotations

import ast
import sys
from collections.abc import Mapping
from pathlib import Path

import pytest

from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("NFR-022", "AC-6")

PACKAGE = "gmail_pdf"
GOOGLE_ROOTS = frozenset(
    {"google", "googleapiclient", "google_auth_oauthlib", "google_auth_httplib2"}
)
GOOGLE_ALLOWED_MODULES = frozenset({"gmail_pdf.infra.gmail_gateway", "gmail_pdf.infra.auth"})
QT_ROOTS = frozenset({"PySide6", "shiboken6"})
LAYERS = frozenset({"domain", "app", "infra", "cli", "gui"})


def imported_modules(module: str, source: str, *, is_package: bool = False) -> set[str]:
    """Absolute dotted names imported by ``source`` (relative imports are resolved)."""
    tree = ast.parse(source)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_from(module, node, is_package)
            found.add(base)
            found.update(f"{base}.{alias.name}" for alias in node.names if alias.name != "*")
    return found


def _resolve_from(module: str, node: ast.ImportFrom, is_package: bool) -> str:
    if node.level == 0:
        return node.module or ""
    parts = module.split(".")
    anchor = parts if is_package else parts[:-1]
    anchor = anchor[: len(anchor) - (node.level - 1)]
    return ".".join([*anchor, *([node.module] if node.module else [])])


def layer_of(module: str) -> str:
    """``domain``, ``app``, ``infra``, ``cli``, ``gui`` or ``root`` for package-level modules."""
    parts = module.split(".")
    return parts[1] if len(parts) > 1 and parts[1] in LAYERS else "root"


def violations_in(module: str, source: str, *, is_package: bool = False) -> list[str]:
    """Rule violations of one module."""
    layer = layer_of(module)
    problems: list[str] = []
    for name in sorted(imported_modules(module, source, is_package=is_package)):
        root = name.split(".")[0]
        own = name == PACKAGE or name.startswith(f"{PACKAGE}.")
        target = layer_of(name) if own else ""
        if layer == "domain":
            if own and target != "domain":
                problems.append(f"{module}: domain may import only domain, not {name}")
            if not own and root not in sys.stdlib_module_names:
                problems.append(f"{module}: domain may not import third-party {name}")
        if layer == "app" and own and target not in ("domain", "app"):
            problems.append(f"{module}: app may import only domain, not {name}")
        if root in GOOGLE_ROOTS and module not in GOOGLE_ALLOWED_MODULES:
            problems.append(f"{module}: only the gateway and auth import Google libraries ({name})")
        if root in QT_ROOTS and layer != "gui":
            problems.append(f"{module}: only gui/** imports PySide6 ({name})")
        if layer == "cli" and root in GOOGLE_ROOTS:
            problems.append(f"{module}: cli never imports Google libraries ({name})")
    return problems


def check_tree(sources: Mapping[str, str]) -> list[str]:
    """Violations across ``{module: source}``; ``__init__`` modules are packages."""
    problems: list[str] = []
    for module, source in sources.items():
        problems.extend(violations_in(module, source))
    return problems


def package_sources() -> dict[str, str]:
    """``{module: source}`` for every module in the real package."""
    sources: dict[str, str] = {}
    for path in sorted((REPO_ROOT / PACKAGE).rglob("*.py")):
        relative = path.relative_to(REPO_ROOT).with_suffix("")
        parts = relative.parts[:-1] if relative.name == "__init__" else relative.parts
        sources[".".join(parts)] = path.read_text(encoding="utf-8")
    return sources


def test_the_real_package_obeys_the_layering_rules() -> None:
    sources = package_sources()

    assert "gmail_pdf.app.ports" in sources  # the walk really found the package
    assert check_tree(sources) == []


@pytest.mark.parametrize(
    ("module", "source", "fragment"),
    [
        ("gmail_pdf.domain.x", "from gmail_pdf.app import ports", "domain may import only domain"),
        ("gmail_pdf.domain.x", "import gmail_pdf.infra.auth", "domain may import only domain"),
        ("gmail_pdf.domain.x", "from ..infra import auth", "domain may import only domain"),
        ("gmail_pdf.domain.x", "import requests", "third-party"),
        ("gmail_pdf.app.x", "from gmail_pdf.infra import auth", "app may import only domain"),
        ("gmail_pdf.app.x", "import gmail_pdf.cli.main", "app may import only domain"),
        ("gmail_pdf.app.x", "from googleapiclient.discovery import build", "Google libraries"),
        ("gmail_pdf.infra.file_store", "from google.oauth2 import credentials", "Google libraries"),
        ("gmail_pdf.infra.retry", "import googleapiclient.errors", "Google libraries"),
        ("gmail_pdf.cli.main", "import googleapiclient", "Google libraries"),
        ("gmail_pdf.cli.main", "from google.auth import transport", "cli never imports"),
        ("gmail_pdf.bootstrap", "import google_auth_oauthlib.flow", "Google libraries"),
        ("gmail_pdf.app.x", "from PySide6 import QtWidgets", "PySide6"),
        ("gmail_pdf.infra.x", "import PySide6.QtCore", "PySide6"),
        ("gmail_pdf.cli.x", "import shiboken6", "PySide6"),
    ],
)
def test_synthetic_violations_are_detected(module: str, source: str, fragment: str) -> None:
    problems = violations_in(module, source)

    assert any(fragment in problem for problem in problems), problems


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("gmail_pdf.domain.x", "import os\nfrom gmail_pdf.domain import errors\nfrom . import y"),
        ("gmail_pdf.domain.x", "import zoneinfo, dataclasses, typing"),
        (
            "gmail_pdf.app.runner",
            "from gmail_pdf.domain.errors import GmailPdfError\nfrom .ports import GmailPort",
        ),
        ("gmail_pdf.infra.gmail_gateway", "from googleapiclient.discovery import build"),
        ("gmail_pdf.infra.auth", "from google_auth_oauthlib.flow import InstalledAppFlow"),
        ("gmail_pdf.gui.app", "from PySide6.QtWidgets import QApplication"),
        (
            "gmail_pdf.cli.main",
            "from gmail_pdf.bootstrap import build_deps\nfrom gmail_pdf.app import runner",
        ),
        ("gmail_pdf.bootstrap", "from gmail_pdf.infra import auth"),
    ],
)
def test_permitted_imports_are_not_flagged(module: str, source: str) -> None:
    assert violations_in(module, source) == []


def test_relative_imports_resolve_against_the_importing_module() -> None:
    source = "from .. import infra\nfrom ...gmail_pdf.app import x"

    modules = imported_modules("gmail_pdf.domain.x", source)

    assert "gmail_pdf.infra" in modules


def test_package_init_relative_import_resolves_inside_the_package() -> None:
    modules = imported_modules("gmail_pdf.domain", "from . import errors", is_package=True)

    assert "gmail_pdf.domain.errors" in modules


def test_a_synthetic_violation_in_a_tree_fails_the_check() -> None:
    sources = {"gmail_pdf.domain.models": "from gmail_pdf.infra import auth"}

    assert check_tree(sources) != []


def test_layer_of_package_level_modules() -> None:
    assert layer_of("gmail_pdf.bootstrap") == "root"
    assert layer_of("gmail_pdf.cli.main") == "cli"


def test_package_walk_reads_utf8_sources() -> None:
    assert all(isinstance(source, str) for source in package_sources().values())
    assert Path(REPO_ROOT / PACKAGE / "__init__.py").exists()
