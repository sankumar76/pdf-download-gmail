# EPIC-10: GUI design system and adaptability

> **GATE (G3 condition C11).** EPIC-10 is detailed but **no story in it may be marked Ready (DoR) until spike S-02 (GitHub [#3](https://github.com/sankumar76/PDF-Download-Gmail/issues/3)) has passed and [ADR-001](../../04-architecture/adr/ADR-001-gui-framework.md) is Accepted.** ADR-001 is Proposed today. The token, button and scaling stories are exactly what S-02 tests, so S-02 must report before STORY-10.01 is Ready (latest: wave W4). The product-owner and scrum-master apply this at every G4.

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-11](https://sankumar76.atlassian.net/browse/PGD-11) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R2 Desktop GUI (v1.0.0) |
| Wave | W4 (FR-054..059, tokens first) and W6 (FR-060, FR-062 and the quality bar) |
| Priority | Backlog rank 9 of 10 (before EPIC-09, so that no screen can hard-code values) |
| PRD size | L (17 pts, PRD §7) |
| Status | Draft. Detailed but held by C11 |

## Goal & User Value
Every screen looks designed by the same hand and follows CLAUDE.md §9: four text roles, one spacing scale, one button component, one palette; the window resizes cleanly from small laptops to large monitors and stays crisp under Windows display scaling; everything works from the keyboard (GOAL-08).

## Requirements Covered
- Functional: FR-054, FR-055, FR-056, FR-057, FR-058, FR-059, FR-060, FR-062. Not included: FR-063 screen reader (R3).
- Non-functional: NFR-017 (keyboard and focus), NFR-018 (contrast), NFR-021 (display matrix), NFR-004 (launch time, shared with EPIC-09), NFR-020 (Windows 11). NFR-019 is R3.
- Business rules / source IDs: GUI-12..19; CLAUDE.md §9.1-9.3; PD-04, PD-12, PD-14, PD-15; UX-I-01..06.

## Scope
**In:**
- `gui/theme/tokens.py` as the only source of values: exactly four typography roles (size and weight), one spacing scale, one light palette, radii, focus ring, minimum window size, `layout.stat.min`, `motion.fast = 0` (FR-054, 055, 057); stylesheet generated from tokens.
- `AppButton`, the only button, with primary, secondary and destructive variants (FR-056).
- Guard tests: no literal colour, size or spacing outside the token file; no `QPushButton(` outside `widgets/button.py`.
- Minimum window 800 x 560 logical px; clamp to a smaller work area and scroll (1920 x 1080 at 200 % gives about 960 x 520) (FR-058, PD-12).
- Crisp rendering and correct layout at 100, 150 and 200 % scaling and when moving between monitors (FR-059, NFR-021).
- Keyboard-only operation, logical tab order, visible focus; Enter in a field starts a Dry run and Ctrl+Enter starts a Run, never a bare Enter (FR-060, PD-15, NFR-017).
- Contrast script over the palette (NFR-018); screenshot matrix; the signed FR-062 checklist.

**Out:** screen reader (FR-063, R3); dark theme; the Advanced area (FR-061, R3); any third-party design kit or component library (D-29).

## UX & Architecture References
- Screens / journeys: all screens; UX §7 (tokens), §7.4 (AppButton), §7.6 (layout, high-DPI), §8 (accessibility), §10 (FR-062 checklist) ([ux-spec](../../03-ux/ux-spec.md)).
- Components: `gui.theme.tokens`, `gui.theme.stylesheet`, `gui.widgets.button`, `gui.main_window`, `gui.app` ([architecture](../../04-architecture/architecture.md) §4.3, §7 NFR-017..021, §10.2 GUI rule, §17).
- ADRs: [ADR-001](../../04-architecture/adr/ADR-001-gui-framework.md) (token contract, capability checklist, spike S-02 plan).
- PRD: [§4.10](../../02-product/prd.md); release plan W4 and W6; test strategy §4 (guard tests).

## Stories (ordered)
Candidates only; the scrum-master creates the stories **after** C11 clears. None is Ready.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-10.01 | A themed empty window from one token file | [W4] Window shows the four text roles, spacing scale, palette and one `AppButton` with its three variants; guard tests fail on any literal (FR-054..057, NFR-018 contrast script) | Workflow step (thin vertical shell, not "build the theme layer") | C11 (S-02, ADR-001) | Held by C11 |
| 2 | STORY-10.02 | Resize safely down to 800 x 560 and below | [W4] Minimum size, clamp to a smaller work area, scroll instead of clipping, re-layout across monitors (FR-058, PD-12) | Data variation (screen sizes) | 10.01 | Held by C11 |
| 3 | STORY-10.03 | Stay crisp at 100, 150 and 200 % scaling | [W4] Screenshot matrix on Windows at three scalings (FR-059, NFR-021) | Data variation (scale) | 10.02 | Held by C11 |
| 4 | STORY-10.04 | Operate everything from the keyboard | [W6] Tab order, focus ring, Enter / Ctrl+Enter, shortcuts listed on screen, a bare Enter never starts a Run (FR-060, NFR-017, PD-15) | Workflow step | EPIC-09 stories 09.01..09.06 | Held by C11 |
| 5 | STORY-10.05 | Sign off the design quality bar | [W6] Screenshot matrix 800 x 560 to 3840 x 2160, contrast results, FR-062 checklist signed by ux-expert (FR-062, NFR-021) | Business-rule variation (checklist items) | 10.04, EPIC-09 complete | Held by C11 |

## Epic Acceptance Criteria
- [ ] Code search finds 0 text sizes or weights outside the four roles, 0 literal spacing values and 0 literal colours outside the token file; exactly 1 button implementation.
- [ ] Screenshots at 800 x 560, at 1920 x 1080 with 200 % scaling (window clamped, nothing clipped) and at 3840 x 2160 show 0 clipped or overlapping controls (NFR-021).
- [ ] Screenshots at 100, 150 and 200 % scaling on Windows are crisp and correctly sized.
- [ ] 100 % of controls are reachable by keyboard with a visible focus indicator; Enter in a field starts a dry run (nothing written), Ctrl+Enter starts a run, bare Enter on a focused button activates that button only.
- [ ] Contrast: text and background pairs at least 4.5:1, focus indicator and borders at least 3:1.
- [ ] The FR-062 checklist is signed by ux-expert at G6/G7 with no further polish work required.
- [ ] S-02 passed and ADR-001 Accepted before the first story became Ready (C11 evidence attached).

## Dependencies & Risks
- Depends on: ADR-001 Accepted (C11); R1 released; ux-spec §7 tokens. Story 4 and 5 need the EPIC-09 screens to exist.
- Risks: RISK-012 (framework cannot satisfy a §9 check; S-02 unverified items: focus-ring offset, live announcements, per-monitor re-layout), RISK-001, RISK-010. The tokens-first order protects GOAL-08 (no screen can hard-code a value).
