"""PGD-13 AC-7: ``redaction.py`` imports only the standard library and ``domain.messages``.

That is what lets ``cli.main`` load it first, before any other part of the package. The same
rule for ``domain/messages.py`` comes from the general ``domain`` rule in
``test_import_boundaries.py``; the fresh-interpreter check is in
``tests/e2e/test_redaction_subprocess.py``.
"""

from __future__ import annotations

import sys

import pytest

from tests.support.subprocess_env import REPO_ROOT
from tests.unit.test_import_boundaries import imported_modules, violations_in

pytestmark = pytest.mark.req("FR-005", "AC-7")

REDACTION = REPO_ROOT / "gmail_pdf" / "redaction.py"
MESSAGES = "gmail_pdf.domain.messages"


def test_redaction_imports_only_the_standard_library_and_domain_messages() -> None:
    modules = imported_modules("gmail_pdf.redaction", REDACTION.read_text(encoding="utf-8"))

    outside = {
        name
        for name in modules
        if name.split(".")[0] not in sys.stdlib_module_names
        and name != MESSAGES
        and not name.startswith(f"{MESSAGES}.")
    }
    assert outside == set()


def test_redaction_does_import_domain_messages() -> None:
    modules = imported_modules("gmail_pdf.redaction", REDACTION.read_text(encoding="utf-8"))

    assert MESSAGES in modules


@pytest.mark.parametrize(
    "module",
    [
        pytest.param("gmail_pdf.domain.models", id="domain"),
        pytest.param("gmail_pdf.domain.messages", id="domain-messages"),
    ],
)
def test_the_domain_layer_may_not_import_redaction(module: str) -> None:
    problems = violations_in(module, "from gmail_pdf import redaction")

    assert any("domain may import only domain" in problem for problem in problems)


def test_infra_and_cli_may_import_redaction() -> None:
    sources = {
        "gmail_pdf.infra.audit": "from gmail_pdf import redaction",
        "gmail_pdf.cli.main": "from gmail_pdf.redaction import safe_message",
    }

    assert [violations_in(module, source) for module, source in sources.items()] == [[], []]
