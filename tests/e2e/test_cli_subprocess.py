"""AC-1 (end to end): the three entry points run as real processes under the socket guard."""

from __future__ import annotations

import sys
import sysconfig
from pathlib import Path

import pytest

from tests.support.subprocess_env import REPO_ROOT, run_guarded

pytestmark = pytest.mark.req("NFR-020", "AC-1")

SHIM = REPO_ROOT / "gmail_pdf_downloader.py"


@pytest.mark.parametrize(
    "args",
    [
        pytest.param([sys.executable, "-m", "gmail_pdf", "--help"], id="python-m"),
        pytest.param([sys.executable, str(SHIM), "--help"], id="shim"),
    ],
)
def test_subprocess_entry_points_print_usage_and_exit_zero(args: list[str], tmp_path: Path) -> None:
    result = run_guarded(args, tmp_path)

    assert (result.returncode, result.stdout.startswith("usage: gmail-pdf")) == (0, True), (
        result.stderr
    )


def test_installed_console_script_prints_usage_and_exits_zero(tmp_path: Path) -> None:
    # A venv puts scripts beside python.exe; a system install (CI runner) uses sysconfig's dir.
    scripts_dirs = [Path(sysconfig.get_path("scripts")), Path(sys.executable).parent]
    candidates = [d / name for d in scripts_dirs for name in ("gmail-pdf.exe", "gmail-pdf")]
    script = next((path for path in candidates if path.exists()), None)
    assert script is not None, "gmail-pdf console script missing: run `pip install --no-deps -e .`"

    result = run_guarded([str(script), "--help"], tmp_path)

    assert (result.returncode, result.stdout.startswith("usage: gmail-pdf")) == (0, True), (
        result.stderr
    )
