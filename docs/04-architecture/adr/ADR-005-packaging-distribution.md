# ADR-005: Packaging and distribution for Windows 11 (Q-03)

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-10-29 |
| Deciders | solution-architect (+ Santhosh at G8) |
| Related | Q-03, ASSUMPTION-03, PRD §6.2 (standalone installer Won't), NFR-020, NFR-023, ADR-001, ADR-002 |

## Context
The sponsor runs Windows 11 (PA-09) and the PRD sets a standalone installer as a Won't for the MVP ("run from source or `pip install`; revisit after G3"). The RD invocation is `python gmail_pdf_downloader.py --start … --end …`. The GUI must start without a console window and without typing commands (FR-047, GOAL-09).

## Decision Drivers
FR-045 (RD invocation), FR-047 (no command typing), GOAL-09, NFR-020, simplicity, LGPL obligations for Qt.

## Considered Options
### Option A — pip-installable package with entry points (chosen)
- Pros: standard; `pyproject.toml` (PEP 621) declares `[project.scripts] gmail-pdf = "gmail_pdf.cli.main:entry"` and `[project.gui-scripts] gmail-pdf-gui = "gmail_pdf.gui.app:main"`; on Windows pip creates `gmail-pdf-gui.exe`, which starts without a console window and can be pinned to Start/desktop; Qt stays dynamically linked (LGPL satisfied).
- Cons: the user needs Python 3.10+ installed once (ASSUMPTION-03); setup steps in the README.
### Option B — Frozen executable (PyInstaller / `pyside6-deploy`)
- Pros: no Python needed; double-click install.
- Cons: Won't in PRD §6.2; code-signing and antivirus false positives; LGPL relinking obligations need review; larger CI. Deferred.
### Option C — Run from source only
- Pros: zero packaging.
- Cons: GUI start needs a terminal command; fails GOAL-09's "no command typing". Rejected as the only path (kept for developers).

## Decision
Option A. Deliverables: `pyproject.toml`, pinned `requirements.txt`/`requirements-dev.txt` (ADR-002), console and GUI entry points, `python -m gmail_pdf` and the RD shim `gmail_pdf_downloader.py`. Install for the sponsor (README): create a venv, `pip install --require-hashes -r requirements.txt`, `pip install --no-deps .`, then create a shortcut to `<venv>\Scripts\gmail-pdf-gui.exe`. Version from `gmail_pdf.__version__` (SemVer: R1 `0.9.0`, R2 `1.0.0`). Releases are git tags with built sdist/wheel attached; no PyPI publication (private tool).

## Consequences
- Positive: no extra tooling; parity of CLI and GUI from one install; rollback = install the previous wheel.
- Negative: one-time Python install for the sponsor (README covers it).
- Follow-up: revisit Option B after R2 if the sponsor asks (new ADR with LGPL review, signing).

## Verification
CI builds the wheel and installs it into a clean venv on `windows-latest`, then runs `gmail-pdf --help` and a GUI smoke start (offscreen) from the installed entry point.
