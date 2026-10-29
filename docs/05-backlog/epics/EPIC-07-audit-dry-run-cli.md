# EPIC-07: Audit trail, dry run and CLI

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-8](https://sankumar76.atlassian.net/browse/PGD-8) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0); the GUI dry-run list and summary are FR-049 and FR-052 in EPIC-09 |
| Wave | W1 (FR-044 dry run, FR-045 flag set and `--help`), W2 (FR-039..043, FR-046) |
| Priority | Backlog rank 5 of 10 |
| PRD size | L (16 pts, PRD §7) |
| Status | Ready for story slicing (scrum-master) |

## Goal & User Value
I can prove what happened in every run, preview a run safely before it writes anything, and script the tool with exit codes that never make an incomplete or failed run look like success (GOAL-10 auditability, GOAL-07 parity, GOAL-02 predictable naming).

## Requirements Covered
- Functional: FR-039, FR-040, FR-041, FR-042, FR-043, FR-044, FR-045, FR-046 (Should).
- Non-functional: NFR-005 (audit completeness), NFR-016 (data minimisation: LOG-02 fields only, no body text, query only at DEBUG), NFR-003 (CSV flush cost), NFR-012 (redaction through the log filter).
- Business rules / source IDs: LOG-01..05; UR-002, UR-003, UR-007, UR-011; CFG-01..10; AC-09; DR-006..008; GOAL-11 evidence via the benchmark.

## Scope
**In:**
- Run log `logs/run_<YYYYMMDD_HHMMSS>.log` and CSV `logs/report_<...>.csv`: exclusive create, never replaced; UTF-8 with BOM for the CSV; times in the run's time zone; closed status set; formula-injection neutralised (FR-039, 040, 041, TD-02).
- Run summary with seven fields; counts reconcile with the CSV (FR-042).
- Exit codes 0/1/2/3 and the three extra outcomes (cancel, unreadable manifest, internal failure) all exiting 1 with distinct first lines and no stack trace (FR-043, D-21).
- Dry run: planned names only, nothing written (no PDFs, manifest, logs, or folder), no attachment bytes fetched, "planned, not verified" (FR-044, D-22, PA-06).
- The CLI flag set exactly as in the RD plus standard `--help` / `-h`; `--log-level` (FR-045, FR-046, PD-16).
- Reconciliation test over the eight scripted outcomes (NFR-005, GOAL-10).

**Out:** GUI summary view and dry-run table (EPIC-09); `--skip-identical`, config file, `--version` (Won't).

## UX & Architecture References
- Screens / journeys: UJ-02, UJ-03, UJ-07; CLI flags, messages and exit-code table in UX §12; SCR-04, SCR-06 are R2 ([ux-spec](../../03-ux/ux-spec.md) §9 rows 039-046).
- Components: `infra.audit`, `app.summary`, `app.runner` (dry-run branch), `domain.models` (`Status`, `ExitCode`), `cli.args`, `cli.console`, `cli.main` ([architecture](../../04-architecture/architecture.md) §4.1, §4.2, §6.5, §7 NFR-005, §12).
- ADRs: [ADR-006](../../04-architecture/adr/ADR-006-core-execution-model.md) (dry run, events), [ADR-004](../../04-architecture/adr/ADR-004-manifest-and-safe-writes.md).
- PRD: [§4.7-4.8](../../02-product/prd.md); release plan W1 and W2.

## Stories (ordered)
Candidates only; the scrum-master creates the stories. This is the epic that produces the first user-visible increment of sprint 1.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-07.01 | CLI dry run on the fake mailbox | [W1] The exact RD flag set plus `--help`; a dry run prints the planned names (RD §4.4 example names exact), writes nothing, fetches no bytes, labels names "planned, not verified"; unknown flag exits 2 (FR-044, FR-045, AC-09) | Workflow step (first end-to-end increment) | 02.02..02.07, 03.04, 04.04, 01.01 | Candidate |
| 2 | STORY-07.02 | Write a run log | [W2] Log file with app version, parameters, one line per decision; query text only at DEBUG; log level option (FR-039, FR-046, NFR-016) | Workflow step | 01.01, 05.01 | Candidate |
| 3 | STORY-07.03 | Write the CSV report with a closed status set | [W2] LOG-02 columns, UTF-8 BOM, one row per candidate, statuses from the closed set, header-only when no candidate is examined (FR-040, FR-041) | Data variation (row types / statuses) | 07.02 | Candidate |
| 4 | STORY-07.04 | End every run with a reconciling summary | [W2] Seven fields, counts equal CSV rows (FR-042) | Workflow step | 07.03 | Candidate |
| 5 | STORY-07.05 | Exit codes that never hide a failure | [W2] One test per code 0/1/2/3 plus cancel, unreadable manifest and internal failure, each non-zero, not 2/3, with a distinct first line and no trace (FR-043, D-21) | Business-rule variation (outcome per code) | 07.04, 05.04, 06.02 | Candidate |
| 6 | STORY-07.06 | Prove the audit trail across eight outcomes | [W2] Reconciliation test over success, errors, cancelled, zero matches, failed auth, unreadable manifest, internal failure and a hard kill (NFR-005, GOAL-10) | Happy / unhappy path (outcome matrix) | 07.05 | Candidate |

## Epic Acceptance Criteria
- [ ] Dry run: the output folder tree is identical before and after (the folder is not created); planned names equal the real-run names for the same mailbox state; names are labelled "planned, not verified"; `NOT_A_PDF` cannot appear.
- [ ] Reconciliation over at least 8 scripted runs: log and CSV exist (CSV header-only where no candidate was examined), header equals the LOG-02 list, every examined candidate has exactly one row with one valid status, per-status counts equal the summary; after a hard kill at most 1 row is missing.
- [ ] First three bytes of the CSV are EF BB BF; query text is absent from the log at INFO and present at DEBUG.
- [ ] One test per exit code 0/1/2/3, plus cancel, unreadable manifest and internal failure: non-zero, not 2 or 3, distinct first line, no stack trace or secret.
- [ ] `--help` prints every flag with its default and exits 0 without a network call or credential read; an unknown flag exits 2.

## Dependencies & Risks
- Depends on: EPIC-02/03/04 for the W1 dry run; EPIC-01 story 1 (redaction) before any log line; EPIC-05/06 for several exit-code outcomes.
- Hidden sequencing (CC-06): the dry-run `already-downloaded` label and the "equals real run" check need STORY-05.02 and 05.01, so the W1 story covers the manifest-absent case and the rest closes in W2.
- Risks: TD-02 (CSV formula neutralisation changes some cell text; documented in README), RISK-010.
