# EPIC-09: Desktop GUI workflow

> **GATE (G3 condition C11).** EPIC-09 is detailed but **no story in it may be marked Ready (DoR) until spike S-02 (GitHub [#3](https://github.com/sankumar76/PDF-Download-Gmail/issues/3)) has passed and [ADR-001](../../04-architecture/adr/ADR-001-gui-framework.md) is Accepted.** The product-owner and scrum-master apply this at every G4. ADR-001 is Proposed today. The latest allowed time to settle it is wave W4 of the first sprint that contains an EPIC-09/10 story. If S-02 fails, ADR-001 is re-opened with the fallback and the product-manager is told; this epic's candidate stories are then re-validated.

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-10](https://sankumar76.atlassian.net/browse/PGD-10) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R2 Desktop GUI (v1.0.0) |
| Wave | W5 (after EPIC-10 tokens in W4) |
| Priority | Backlog rank 10 of 10 |
| PRD size | XL (25 pts, PRD §7) |
| Status | Draft. Detailed but held by C11 |

## Goal & User Value
I do the whole job in one desktop window with no command typing: set the dates, time zone, output folder, optional search text and Spam/Trash choice; sign in; preview with a dry run; run; watch progress; cancel safely; and open the folder, run log and CSV (GOAL-07 GUI/CLI parity, GOAL-09 ease of first use, GOAL-06).

## Requirements Covered
- Functional: FR-047, FR-048, FR-049, FR-050, FR-051, FR-052, FR-053, FR-064. The GUI surfaces of R1 requirements also belong here (release plan W5): FR-005 (redaction on every text surface), FR-006 (setup help), FR-010 and FR-013 (the two fields), FR-015 (inline validation, with FR-048), FR-033 (warnings), FR-037 (stop behaviour via FR-051), FR-042 (summary via FR-052). FR-061 (Advanced area) is R3 and out of scope.
- Non-functional: NFR-004 (launch at most 3 s, stall at most 200 ms, Cancel at most 5 s), NFR-005 (GUI outcomes reconcile), NFR-012 (secrets on GUI text), NFR-020 (Windows 11 primary).
- Business rules / source IDs: GUI-01..11; UR-001..007; PD-01 (seven fields), PD-13, PD-14; R-COUNT.

## Scope
**In:**
- One window with the seven Download settings and inline validation using the shared domain rules (FR-047, FR-048).
- Set up Google access (SCR-03, DLG-07), sign-in wait and re-consent (DLG-01, DLG-02), including the wrong-client-file message.
- Dry-run results list and folder warnings (SCR-04, FR-049, FR-033).
- Run in progress: live counts, bar, current item at the R-COUNT rate (core up to 10 Hz, window redraw at most 4 times a second); responsive window (SCR-05, FR-050, FR-053).
- Cancel with `Stopping...`, DLG-06 (FR-051); run summary with open folder, run log, CSV (SCR-06, FR-052).
- Identical results to the CLI for identical inputs: names, statuses, manifest, log, CSV (FR-064).

**Out:** tokens, window sizing, scaling, keyboard, FR-062 checklist (EPIC-10); Advanced area, sign-out, screen reader (R3); sort or filter in the dry-run table, dark theme, remembering the last folder (Won't, PD-14); any third-party design kit (D-29).

## UX & Architecture References
- Screens / journeys: SCR-01..06, DLG-01..08, UJ-01..06; wireframes in `docs/03-ux/wireframes/` ([ux-spec](../../03-ux/ux-spec.md) §5, §6, §9).
- Components: `gui.main_window`, `gui.view_model`, `gui.worker`, `gui.widgets.*`, `gui.dialogs.*`, `bootstrap`, `app.runner` events ([architecture](../../04-architecture/architecture.md) §4.3, §6.8, §6.9, §12).
- ADRs: [ADR-001](../../04-architecture/adr/ADR-001-gui-framework.md) (Proposed), [ADR-006](../../04-architecture/adr/ADR-006-core-execution-model.md), [ADR-003](../../04-architecture/adr/ADR-003-token-storage-and-secrets.md) (GUI default paths).
- PRD: [§4.9](../../02-product/prd.md); release plan W5; test strategy §4 (GUI testing).

## Stories (ordered)
Candidates only; the scrum-master creates the stories **after** C11 clears. None is Ready. Each also needs the R1 core to expose progress events and cancellation.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-09.01 | Fill in the Download settings and see errors beside the field | [W5] Seven fields, FR-010/013 fields, inline validation equal to the CLI rules, Run blocked when invalid (FR-047, FR-048) | Workflow step (first screen slice) | C11; EPIC-10 tokens and button (W4) | Held by C11 |
| 2 | STORY-09.02 | Preview with a dry run in the window | [W5] Planned-names list in fixed order, "not verified" notice, folder warnings, output folder unchanged, list equals CLI dry run (FR-049, FR-033, FR-044) | Workflow step | 09.01 | Held by C11 |
| 3 | STORY-09.03 | Set up Google access and sign in from the window | [W5] SCR-03 steps and path, wrong-client-file message, sign-in wait and re-consent dialogs, no secret in any text (FR-006, FR-001, FR-003, FR-005 GUI surfaces) | Happy / unhappy path | 09.01; EPIC-01 | Held by C11 |
| 4 | STORY-09.04 | Run and watch live progress | [W5] Counts change during a slow-mock run, window stays responsive, R-COUNT rate, launch at most 3 s (FR-050, FR-053, NFR-004) | Workflow step | 09.02, 09.03 | Held by C11 |
| 5 | STORY-09.05 | Cancel a run from the window | [W5] Cancel mid-run leaves no temp file and a valid manifest; "Run cancelled" wording equal to the CLI (FR-051, FR-037) | Happy / unhappy path | 09.04 | Held by C11 |
| 6 | STORY-09.06 | See the summary and open the results | [W5] Seven fields, errors table, open folder / run log / CSV each go to the right place (FR-052, FR-042) | Workflow step | 09.04 | Held by C11 |
| 7 | STORY-09.07 | Prove GUI and CLI give the same results | [W5] Same fixture through both: CSVs equal, timestamps excluded (FR-064, GOAL-07); AC-01..09 checked on the GUI | Business-rule variation (front end) | 09.06 | Held by C11 |

## Epic Acceptance Criteria
- [ ] A walkthrough from launch to saved files needs no terminal.
- [ ] Start after end blocks Run with an inline message next to the field.
- [ ] The dry-run list equals the CLI dry-run output and the output folder is unchanged.
- [ ] Counts change during a slow-mock run; the window stays responsive (stall at most 200 ms); Cancel takes effect within 5 s with no temp file and a valid manifest.
- [ ] Each of the open-folder, open-run-log and open-CSV links opens the right location.
- [ ] The same fixture through the GUI and the CLI gives equal CSVs (timestamps excluded); 0 differences (GOAL-07).
- [ ] The sentinel-secret matrix finds 0 occurrences on every GUI text surface, including the details pane and copied diagnostics.
- [ ] S-02 passed and ADR-001 Accepted before the first story became Ready (C11 evidence attached).

## Dependencies & Risks
- Depends on: R1 released (core callable with progress and cancellation); ADR-001 Accepted (C11); EPIC-10 tokens and button first (W4), so no screen hard-codes a value.
- Risks: RISK-001 (GUI scope growth; EPIC-09 is the largest epic, watch estimate growth sprint over sprint), RISK-012 (framework cannot meet §9; controlled by C11), RISK-010. The sponsor's GOAL-09 trial needs TR-006.
