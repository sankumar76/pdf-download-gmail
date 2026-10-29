# ADR-001: Desktop GUI framework — PySide6 (Qt 6 Widgets) with a generated token stylesheet

| Field | Value |
|-------|-------|
| Status | **Proposed** — desk-check passed at G3; becomes Accepted when spike S-02 passes (before R2 wave W4). R1 does not depend on it |
| Date | 2026-10-29 |
| Deciders | solution-architect (+ Santhosh at G8) |
| Related | D-01, CLAUDE.md §9, FR-047..060, FR-062..064, NFR-004, NFR-017..021, NFR-023, RISK-001, RISK-012, ux-spec §7, §8, §11 |

## Context
D-01 makes the product a desktop GUI plus CLI on one core. CLAUDE.md §9 requires shared tokens (exactly four type roles, one spacing scale, one palette), one reusable button component with variants, resizable windows with a minimum size, and crisp rendering under OS scaling. The ux-spec (v0.1) adds: minimum window 800 × 560, per-monitor DPI awareness, a 2 px focus ring with 2 px offset, a keyboard-navigable table with one tab stop, live announcements, accessible names/roles (R3), a native folder picker, opening files and folders in the OS shell, and an IANA time-zone list. The RD allows no third-party dependencies "unless justified" (NFR-023), so whatever is chosen needs this ADR. The user's global instructions also say "leverage shadcn ui components for the ui", a React/web component library.

## Decision Drivers
- §9.2/§9.3 compliance with **no per-widget literals** (FR-054..057, GOAL-08)
- High-DPI at 100/150/200 % and per-monitor (FR-059, NFR-021)
- Keyboard operation and visible focus (FR-060, NFR-017), screen-reader path for R3 (FR-063, NFR-019)
- Responsiveness with a long-running core (NFR-004)
- One language and tool chain (Python, mypy strict, pytest) for a one-developer team
- Minimal dependency and supply-chain surface (NFR-023, TB-5); permissive or LGPL licence
- Testability in CI (headless)

## Considered Options

### Option A — Tkinter/ttk (standard library)
- Pros: zero new dependency; ships with CPython on Windows; small footprint.
- Cons: Windows DPI awareness must be set manually via `ctypes` and Tk's scaling is process-wide (no reliable per-monitor re-layout); ttk theming cannot express a full token palette without re-implementing themes (many widgets ignore style colours on the native `vista` theme, so a custom theme is required); focus-ring styling is limited; no UI Automation support worth relying on for R3 (FR-063); modern look needs substantial custom drawing.
- Cost / effort: low setup, **high** effort to reach §9 and ux-spec §7 quality; high RISK-012.

### Option B — PySide6 (Qt 6 Widgets), official Qt for Python — **chosen**
- Pros: High-DPI is always on in Qt 6 and cannot be disabled; default rounding policy `PassThrough` keeps 150 % exact (Qt docs, context7). Qt Style Sheets give full control over colours, borders, radii, padding and fonts, so a stylesheet **generated from one Python token module** realises FR-054..057. `AppButton(QPushButton)` gives one component with variants via a dynamic property (`variant="primary"`). Mature focus chain, `setTabOrder`, `QTableView` (one tab stop, arrow keys), `QFileDialog`, `QDesktopServices.openUrl`, UI Automation bridge on Windows for R3. `QThread` + queued signals fit the core's event API. `pytest-qt` (MIT) supports headless tests (`QT_QPA_PLATFORM=offscreen`). Type stubs ship with PySide6.
- Cons: Large binary dependency (tens of MB; mitigated by the `PySide6-Essentials` wheel, which omits add-on modules); LGPL-3.0 obligations if the app is ever frozen into an executable; QSS gaps: no `outline-offset`, no transitions, no `line-height` (handled in UX-I-01..03).
- Cost / effort: moderate; one dependency; best fit for §9.

### Option C — pywebview + shadcn/ui (React, Tailwind, Radix) frontend
- Pros: Literally satisfies the user-level "shadcn ui" preference; shadcn's CSS-variable tokens and `Button` with `cva` variants map naturally to §9.2; WebView2 on Windows 11 handles high-DPI; Radix primitives are accessible.
- Cons: Two languages and two tool chains (Node/npm build of React + Tailwind + Radix, hundreds of npm packages in the build supply chain); on Windows pywebview depends on `pythonnet` and the .NET runtime (AA, verify); a JS↔Python bridge exposes Python functions to page script, which becomes an attack path for untrusted email text (subjects, names) rendered in HTML (TB-4); mypy/pytest coverage covers only half the UI code; packaging and CI double in size; it renders a web page in a window, which sits uneasily with CLAUDE.md §9 "not a website".
- Cost / effort: high; adds the most moving parts.

### Option D — Others considered briefly
- **wxPython**: native widgets, but native theming defeats a single token palette (colours of native controls are OS-controlled). Rejected for FR-057.
- **CustomTkinter / Flet / Dear PyGui**: smaller communities or immediate-mode rendering; Flet's desktop client is a separate Flutter binary (packaging and NFR-014 egress questions). Rejected on maturity/accessibility.

## Decision
We will build the GUI with **PySide6 Qt Widgets** (`PySide6-Essentials`, Qt ≥ 6.8 line, exact pin at W4), using:
1. **Token contract.** `gmail_pdf/gui/theme/tokens.py` is the only place sizes, weights, spacing, radii, colours and layout sizes exist, named exactly as ux-spec §7 (`type.heading|subheading|body|label`, `space.1..8`, `color.*`, `shape.*`, `layout.*`). It is pure Python (no Qt import) so tests and the contrast script read it directly.
2. **Generated stylesheet.** `theme/stylesheet.py` renders one application-wide QSS string from the tokens (string template) and builds the four `QFont` roles; screens never call `setStyleSheet` with literals.
3. **One button.** `widgets/button.py::AppButton` with `Variant` = `PRIMARY | SECONDARY | DESTRUCTIVE`, fixed height/min width from tokens, busy state, and a custom-painted focus ring (2 px, offset 2) because QSS lacks `outline-offset`.
4. **High-DPI.** Leave Qt 6 defaults (high-DPI on, `PassThrough`); layouts only (no absolute geometry); vector icons (SVG via `QIcon`).
5. **Design language.** The palette and component shapes follow the ux-spec, which is in the spirit of shadcn/ui (neutral surfaces, 6 px radius, accent primary, outline secondary, destructive). We adopt shadcn's **design language**, not its React components (AQ-02 to Santhosh, FYI at G8).

## Capability checklist (ux-spec §11) — desk-check at G3, proof in S-02
| # | Capability | PySide6 means | Desk-check | S-02 proof needed |
|---|------------|---------------|------------|-------------------|
| 1 | Full token-driven theming, no per-widget literals | Generated QSS + `QFont` roles; test greps `gui/` for literals outside `theme/` | Pass | Yes — style every widget used (line edit, date edit, combo, check box, table, progress bar, scroll bars, tool tips, dialogs) |
| 2 | One button component, three variants | `AppButton` + dynamic property selector in QSS | Pass | Yes |
| 3 | Per-monitor DPI awareness and re-layout | Qt 6 high-DPI always on (docs); per-monitor awareness on Windows is Qt 6 default (verify) | Pass (docs) | Yes — move window between 100 % and 200 % monitors |
| 4 | Visible, customisable focus ring (2 px, offset 2) | QSS `:focus` border for fields; painted ring in `AppButton` and table delegate | Partial (offset needs painting) | Yes |
| 5 | Tab-order control | `QWidget.setTabOrder` | Pass | Walkthrough |
| 6 | Minimum window 800 × 560, clamped to a smaller work area with scrolling (PD-12, UA-01) | `setMinimumSize(min(token, availableGeometry))` at start-up and on `screenChanged`; content in `QScrollArea` | Pass | Yes at 1920 × 1080 / 200 % (work area ≈ 960 × 520 logical): window clamped, columns scroll, nothing clipped |
| 6a | Shortcuts Enter = Dry run, Ctrl+Enter = Run (PD-15) | `QShortcut` / field key handling; bare Enter on a button activates only that button | Pass | Walkthrough |
| 7 | Keyboard table, one tab stop | `QTableView` + plain-text model | Pass | Yes |
| 8 | Live announcements (polite/assertive) | `QAccessibleAnnouncementEvent` (Qt ≥ 6.8 — verify) or status-bar `QAccessible` value change | Unverified | Yes (Narrator) |
| 9 | Accessible names and roles (R3) | `setAccessibleName/Description`; UIA bridge | Pass (docs) | Narrator smoke in S-02, full test R3 |
| 10 | Reduced-motion signal | Not needed: QSS has no transitions (UX-I-01) | Pass (n/a) | — |
| 11 | Native folder picker | `QFileDialog.getExistingDirectory` | Pass | — |
| 12 | Open files/folders in OS shell | `QDesktopServices.openUrl(QUrl.fromLocalFile(…))` | Pass | — |
| 13 | IANA time-zone list | `zoneinfo.available_timezones()` with `tzdata` (ADR-002), not Qt's `QTimeZone` | Pass | — |
| 14 | Responsive during runs | Core on `QThread`; queued signals; ≤ 10 Hz coalescing | Pass | Heartbeat test (NFR-004) |
| 15 | Rich-text injection safety | `Qt.TextFormat.PlainText` on every label/model showing email text | Pass | Test with `<b>` subject |
| 16 | Tabular figures, Segoe UI Variable | `QFont` OpenType features (Qt ≥ 6.7 — verify) | Unverified | Yes (UX-I-06, optional) |
| 17 | Scrim behind dialogs | Overlay widget | Partial | Yes (UX-I-03, optional) |

## Spike S-02 plan (RISK-012) — run before W4, timebox 2 days, code in `spikes/s02-qt-theme/`, never merged
1. Install `PySide6-Essentials` (pinned) in a clean venv on Windows 11; record wheel size and import time.
2. Implement `tokens.py` (ux-spec §7 values) + `stylesheet.py` + `AppButton` (3 variants, 6 states) + a form with every field type, a `QTableView` with 1,000 rows, a progress bar, a modal dialog with scrim.
3. Checks (each pass/fail with screenshot): FR-054 (four fonts only, code search), FR-055 (no spacing literal), FR-056 (only `AppButton`), FR-057 (no colour literal), FR-058 (resize 800 × 560 → 3840 × 2160, no clipping), FR-059 (100/150/200 % + monitor move), FR-060 (tab through every control, ring visible), NFR-004 (launch to first paint ≤ 3 s on the reference machine; stall ≤ 200 ms with a 1,000-event burst), NFR-018 (contrast script reads `tokens.py`), checklist items 8, 16, 17.
4. Exit: all Must items (1–7, 11–15) pass → ADR Accepted. Any Must fails → try the remedy listed in the checklist; if still failing, re-open this ADR with Option A (Tk) as fallback and raise a scope note to PM.

## Consequences
- Positive: §9 compliance is structural (one token file, one stylesheet generator, one button class), enforceable by tests; GUI and CLI share the core with no GUI-specific logic in it; R3 accessibility is reachable without a framework change.
- Negative / trade-offs accepted: one large runtime dependency (justified by NFR-023 ADR rule); LGPL obligations if a frozen executable is ever produced (ADR-005); three QSS gaps handled by custom painting or token reinterpretation (UX-I-01..03); the literal shadcn/ui component library is not used (AQ-02).
- Follow-up actions: S-02 (developer, before W4); confirm AQ-02 with Santhosh at G8 (orchestrator FYI); ux-expert acknowledges UX-I-01..06.

## Verification
S-02 report attached to this ADR (status → Accepted). Ongoing: GUI token-literal test and `AppButton`-only test in CI; screenshot matrix at G7 (ux-spec §7.6); NFR-004 instrumented test.
