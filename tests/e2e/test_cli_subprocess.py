"""AC-1 (end to end): the three entry points run as real processes under the socket guard."""

from __future__ import annotations

import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest

from tests.support.subprocess_env import (
    REPO_ROOT,
    SUBPROCESS_TIMEOUT_S,
    guarded_env,
    run_guarded,
)

pytestmark = pytest.mark.req("NFR-020", "AC-1")

SHIM = REPO_ROOT / "gmail_pdf_downloader.py"

BROKEN_PARSER = (
    "import sys\n"
    "from gmail_pdf.cli import main as m\n"
    "class Parser:\n"
    "    def parse_args(self, argv=None):\n"
    "        raise RuntimeError('boom')\n"
    "m.build_parser = lambda: Parser()\n"
    "sys.exit(m.main([]))\n"
)


def run_with_a_closed_stream(args: list[str], stream: str, tmp_path: Path) -> tuple[int, str]:
    """Run a child, close one output reader at once, and return its status and other output."""
    process = subprocess.Popen(
        args,
        cwd=tmp_path,
        env=guarded_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    closed, other = (
        (process.stdout, process.stderr) if stream == "stdout" else (process.stderr, process.stdout)
    )
    assert closed is not None and other is not None
    closed.close()
    process.wait(timeout=SUBPROCESS_TIMEOUT_S)
    output = other.read().decode("utf-8", "replace")
    other.close()
    return process.returncode, output


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


@pytest.mark.req("PGD-68")
def test_help_exits_zero_when_the_stdout_reader_is_gone(tmp_path: Path) -> None:
    # Python exits 120 when it cannot flush a standard stream at shutdown: an unused output
    # stream must not turn a successful --help into a failure (PGD-68).
    code, stderr = run_with_a_closed_stream(
        [sys.executable, "-m", "gmail_pdf", "--help"], "stdout", tmp_path
    )

    assert (code, stderr) == (0, "")


@pytest.mark.req("PGD-68")
def test_a_reported_failure_exits_one_when_the_stderr_reader_is_gone(tmp_path: Path) -> None:
    # The fixed failure line cannot be delivered, but the status is still the one D-21 chose.
    code, stdout = run_with_a_closed_stream(
        [sys.executable, "-c", BROKEN_PARSER], "stderr", tmp_path
    )

    assert (code, stdout) == (1, "")
