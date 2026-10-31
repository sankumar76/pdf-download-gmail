"""T-05 (QUA-37 interim control): no ``sys.exit`` or ``SystemExit`` carries a non-integer.

``SystemExit("text")`` prints the text raw and bypasses every redaction hook. Until the
structural fix of QUA-37 (#23), the package may only exit with an integer (or nothing). This is
an AST check over each file of ``gmail_pdf/``.

What it flags (a call whose first argument is anything but an integer literal or a call of
``main``/``entry``, which return ints; a call with keyword arguments only; a starred argument):

* ``sys.exit(...)``, also through ``import sys as s``;
* ``from sys import exit`` with or without ``as``;
* the builtins ``exit`` and ``quit``, and ``SystemExit(...)``;
* a name bound to any of these (``e = sys.exit``, ``E = SystemExit``, ``s = sys``), followed
  through chains of such assignments;
* a class that derives from ``SystemExit`` (or from such a name): flagged at its definition.

What it accepts and does not cover: ``getattr(sys, "exit")``, ``builtins.exit``, a bare
``raise`` of an instance built elsewhere, ``parser.error`` and ``parser.exit`` (argparse prints
the text itself; that path is #23), third-party code, and a local function named ``main`` or
``entry`` returning text (the call is trusted by name). T-05 stays a review step until #23
closes; this test is a tripwire, not the control.
"""

from __future__ import annotations

import ast

import pytest

from tests.support.subprocess_env import REPO_ROOT

pytestmark = pytest.mark.req("FR-005", "NFR-012", "T-05")

# Calls whose result is an integer exit code by construction.
INT_CALLS = {"main", "entry"}
EXIT_BUILTINS = frozenset({"exit", "quit", "SystemExit"})


def _is_exit_ref(node: ast.expr, sys_names: set[str], exit_names: set[str]) -> bool:
    """``node`` names ``sys.exit`` or an exit-like builtin, directly or through an alias."""
    if isinstance(node, ast.Name):
        return node.id in exit_names
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "exit"
        and isinstance(node.value, ast.Name)
        and node.value.id in sys_names
    )


def _new_names(
    node: ast.AST, sys_names: set[str], exit_names: set[str]
) -> tuple[set[str], set[str]]:
    """Names this one statement binds to the ``sys`` module and to an exit-like callable."""
    if isinstance(node, ast.Import):
        return {a.asname or a.name for a in node.names if a.name == "sys"}, set()
    if isinstance(node, ast.ImportFrom) and node.module == "sys":
        return set(), {a.asname or a.name for a in node.names if a.name == "exit"}
    if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = {t.id for t in targets if isinstance(t, ast.Name)}
        if _is_exit_ref(node.value, sys_names, exit_names):
            return set(), names
        if isinstance(node.value, ast.Name) and node.value.id in sys_names:
            return names, set()
    return set(), set()


def _exit_names(tree: ast.AST) -> tuple[set[str], set[str]]:
    """Every local name for the ``sys`` module and for an exit-like callable (to a fixed point)."""
    sys_names, exit_names = {"sys"}, set(EXIT_BUILTINS)
    grew = True
    while grew:
        grew = False
        for node in ast.walk(tree):
            new_sys, new_exit = _new_names(node, sys_names, exit_names)
            if not (new_sys <= sys_names and new_exit <= exit_names):
                sys_names |= new_sys
                exit_names |= new_exit
                grew = True
    return sys_names, exit_names


def _is_int_exit_code(arg: ast.expr) -> bool:
    if isinstance(arg, ast.UnaryOp) and isinstance(arg.op, (ast.USub, ast.UAdd)):
        arg = arg.operand
    if isinstance(arg, ast.Constant):
        return isinstance(arg.value, int)
    return isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id in INT_CALLS


def non_integer_exits(source: str) -> list[int]:
    """Line numbers of exit calls whose argument is not clearly an integer, and of subclasses."""
    tree = ast.parse(source)
    sys_names, exit_names = _exit_names(tree)
    bad = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and any(
            _is_exit_ref(base, sys_names, exit_names) for base in node.bases
        ):
            bad.add(node.lineno)
        elif isinstance(node, ast.Call) and _is_exit_ref(node.func, sys_names, exit_names):
            if node.args:
                if not _is_int_exit_code(node.args[0]):
                    bad.add(node.lineno)
            elif node.keywords:
                bad.add(node.lineno)
    return sorted(bad)


def test_no_exit_in_the_package_carries_a_non_integer() -> None:
    offenders = {
        str(path.relative_to(REPO_ROOT)): lines
        for path in sorted((REPO_ROOT / "gmail_pdf").rglob("*.py"))
        if (lines := non_integer_exits(path.read_text(encoding="utf-8")))
    }

    assert offenders == {}


FLAGGED_FORMS = {
    "raise-system-exit": "raise SystemExit('boom')",
    "sys-exit": "import sys\nsys.exit('boom')",
    "sys-exit-variable": "import sys\nsys.exit(message)",
    "f-string": "raise SystemExit(f'{x}')",
    "import-sys-as": "import sys as s\ns.exit('boom')",
    "from-sys-import-exit": "from sys import exit\nexit('boom')",
    "from-sys-import-exit-as": "from sys import exit as bye\nbye('boom')",
    "builtin-exit": "exit('boom')",
    "builtin-quit": "quit('boom')",
    "name-bound-to-sys-exit": "import sys\ne = sys.exit\ne('boom')",
    "name-bound-to-system-exit": "E = SystemExit\nraise E('boom')",
    "annotated-name-bound": "import sys\ne: object = sys.exit\ne('boom')",
    "chain-of-aliases": "import sys\na = sys.exit\nb = a\nb('boom')",
    "name-bound-to-the-module": "import sys\ns = sys\ns.exit('boom')",
    "subclass-and-raise": "class X(SystemExit):\n    pass\nraise X('boom')",
    "subclass-definition-alone": "class X(SystemExit):\n    pass",
    "subclass-of-a-subclass": "class X(SystemExit): ...\nclass Y(X): ...\nraise Y('boom')",
    "subclass-of-sys-exit-alias": "from sys import exit as e\nclass X(e): ...",
    "starred-argument": "import sys\nsys.exit(*args)",
    "keyword-only": "raise SystemExit(code='boom')",
}


@pytest.mark.parametrize("source", FLAGGED_FORMS.values(), ids=FLAGGED_FORMS.keys())
def test_the_check_flags_a_text_exit(source: str) -> None:
    assert non_integer_exits(source) != []


ACCEPTED_FORMS = {
    "main-call": "raise SystemExit(main())",
    "sys-exit-zero": "import sys\nsys.exit(0)",
    "bare-raise": "raise SystemExit",
    "sys-exit-no-argument": "import sys\nsys.exit()",
    "aliased-module-integer": "import sys as s\ns.exit(2)",
    "imported-exit-integer": "from sys import exit as bye\nbye(1)",
    "builtin-exit-integer": "exit(0)",
    "alias-integer": "import sys\ne = sys.exit\ne(3)",
    "negative-integer": "import sys\nsys.exit(-1)",
    "unrelated-class": "class X(Exception):\n    pass\nraise X('boom')",
    "unrelated-exit-method": "parser = object()\nparser.exit(0)",
}


@pytest.mark.parametrize("source", ACCEPTED_FORMS.values(), ids=ACCEPTED_FORMS.keys())
def test_the_check_accepts_integer_exits(source: str) -> None:
    assert non_integer_exits(source) == []
