"""T-05 (QUA-37 interim control): no ``sys.exit`` or ``SystemExit`` carries a non-integer.

``SystemExit("text")`` prints the text raw and bypasses every redaction hook. Until the
structural fix of QUA-37, the package may only exit with an integer (or nothing). This is an AST
check over ``gmail_pdf/``: it flags a call whose first argument is anything but an integer
literal, a call of ``main``/``entry`` (which return ints) or a name that is a known int constant.
"""

from __future__ import annotations

import ast

import pytest

from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("FR-005", "NFR-012", "T-05")

# Calls whose result is an integer exit code by construction.
INT_CALLS = {"main", "entry"}


def _exit_calls(tree: ast.AST) -> list[ast.Call]:
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            is_sys_exit = (
                isinstance(func, ast.Attribute)
                and func.attr == "exit"
                and isinstance(func.value, ast.Name)
                and func.value.id == "sys"
            )
            if is_sys_exit or (isinstance(func, ast.Name) and func.id == "SystemExit"):
                calls.append(node)
    return calls


def non_integer_exits(source: str) -> list[int]:
    """Line numbers of exit calls whose argument is not clearly an integer."""
    bad = []
    for call in _exit_calls(ast.parse(source)):
        if not call.args:
            continue
        arg = call.args[0]
        is_int_literal = isinstance(arg, ast.Constant) and isinstance(arg.value, int)
        is_int_call = (
            isinstance(arg, ast.Call)
            and isinstance(arg.func, ast.Name)
            and arg.func.id in INT_CALLS
        )
        if not (is_int_literal or is_int_call):
            bad.append(call.lineno)
    return bad


def test_no_exit_in_the_package_carries_a_non_integer() -> None:
    offenders = {
        str(path.relative_to(REPO_ROOT)): lines
        for path in sorted((REPO_ROOT / "gmail_pdf").rglob("*.py"))
        if (lines := non_integer_exits(path.read_text(encoding="utf-8")))
    }

    assert offenders == {}


@pytest.mark.parametrize(
    "source",
    [
        "raise SystemExit('boom')",
        "import sys\nsys.exit('boom')",
        "import sys\nsys.exit(message)",
        "raise SystemExit(f'{x}')",
    ],
)
def test_the_check_flags_a_text_exit(source: str) -> None:
    assert non_integer_exits(source) != []


@pytest.mark.parametrize(
    "source",
    ["raise SystemExit(main())", "import sys\nsys.exit(0)", "raise SystemExit", "sys.exit()"],
)
def test_the_check_accepts_integer_exits(source: str) -> None:
    assert non_integer_exits(source) == []
