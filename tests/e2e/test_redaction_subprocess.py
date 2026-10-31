"""PGD-13 AC-5, AC-7, AC-8 in real child interpreters (no mocks of the interpreter's own exit).

The in-process versions are in ``tests/unit/test_redaction_hooks.py`` and
``tests/unit/test_cli_main_hooks.py``. A real SIGINT / CTRL_BREAK against a running download
belongs to the cancel story (STORY-06.02, test-strategy section 8); here Ctrl+C is the
``KeyboardInterrupt`` the interpreter would raise.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from gmail_pdf.domain import messages
from tests.support import sentinels
from tests.support.subprocess_env import REPO_ROOT, run_guarded

pytestmark = pytest.mark.req("FR-005", "NFR-012")

FAILURE = messages.UNEXPECTED_FAILURE_LINE + "\n"
CANCELLED = messages.RUN_CANCELLED_LINE + "\n"

PREAMBLE = (
    "from gmail_pdf import redaction\n"
    f"redaction.register_secret({sentinels.CLIENT_SECRET!r})\n"
    "redaction.install_excepthooks()\n"
)
RAISE_WITH_SECRET = (
    f"raise RuntimeError({sentinels.CLIENT_SECRET!r} + ' ' + {sentinels.ACCESS_TOKEN!r})\n"
)
MAIN_WITH_BROKEN_PARSER = (
    "import sys\n"
    "from gmail_pdf.cli import main as m\n"
    "class P:\n"
    "    def parse_args(self, argv=None):\n"
    "        raise {error}\n"
    "m.build_parser = lambda: P()\n"
    "sys.exit(m.main([]))\n"
)


def run_code(code: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    return run_guarded([sys.executable, "-c", code], tmp_path)


@pytest.mark.req("AC-5")
def test_an_uncaught_main_thread_exception_prints_one_line_and_exits_one(tmp_path: Path) -> None:
    result = run_code(PREAMBLE + RAISE_WITH_SECRET, tmp_path)

    assert (result.returncode, result.stderr, result.stdout) == (1, FAILURE, "")


@pytest.mark.req("AC-5")
def test_an_uncaught_worker_thread_exception_prints_one_line(tmp_path: Path) -> None:
    code = (
        PREAMBLE
        + "import threading\n"
        + f"def work():\n    {RAISE_WITH_SECRET}"
        + "t = threading.Thread(target=work)\nt.start()\nt.join()\n"
    )

    result = run_code(code, tmp_path)

    assert (result.returncode, result.stderr, result.stdout) == (0, FAILURE, "")


@pytest.mark.req("AC-5")
def test_main_turns_an_unexpected_failure_into_one_line_and_exit_one(tmp_path: Path) -> None:
    code = MAIN_WITH_BROKEN_PARSER.format(error=f"RuntimeError({sentinels.CLIENT_SECRET!r})")

    result = run_code(code, tmp_path)

    assert (result.returncode, result.stderr, result.stdout) == (1, FAILURE, "")


@pytest.mark.req("AC-8")
def test_main_turns_ctrl_c_into_run_cancelled_and_exit_one(tmp_path: Path) -> None:
    code = MAIN_WITH_BROKEN_PARSER.format(error=f"KeyboardInterrupt({sentinels.CLIENT_SECRET!r})")

    result = run_code(code, tmp_path)

    assert (result.returncode, result.stderr, result.stdout) == (1, CANCELLED, "")


@pytest.mark.req("AC-7")
def test_redaction_loads_alone_in_a_fresh_interpreter() -> None:
    code = (
        "import sys\n"
        "import gmail_pdf.redaction\n"
        "print(sorted(m for m in sys.modules if m.startswith('gmail_pdf')))\n"
    )

    result = run_guarded([sys.executable, "-c", code], REPO_ROOT)

    loaded = [
        "gmail_pdf",
        "gmail_pdf.domain",
        "gmail_pdf.domain.messages",
        "gmail_pdf.redaction",
    ]
    assert (result.returncode, result.stdout.strip()) == (0, str(loaded)), result.stderr
