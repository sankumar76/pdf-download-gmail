# Product Backlog — Gmail PDF Attachment Downloader

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Date | 2026-10-29 |
| Version | 0.1 (G4 Backlog Ready, epic level) |
| Jira | Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1); epics PGD-2..PGD-11 |
| Inputs | [prd.md](../02-product/prd.md) v0.4, [release-plan.md](../02-product/release-plan.md) v0.2, [consistency-report.md](consistency-report.md), decisions D-33 (R1 core + CLI first, Windows 11, as soon as possible) and C11 |
| Stories | None created yet. The scrum-master creates the sprint-1 stories next; the candidate stories in each epic file are the starting list |

## 1. Ordered epic backlog

Order is by dependency first, then value and risk reduction (PRD §8 scores), then learning. Epics span waves, so the "first work" column says what is needed first.

| Rank | Epic | Jira | Release | Waves | Pts | Status | First work needed |
|------|------|------|---------|-------|-----|--------|-------------------|
| 1 | [EPIC-02](epics/EPIC-02-find-messages.md) Find messages in a date range | [PGD-3](https://sankumar76.atlassian.net/browse/PGD-3) | R1 | W1, W2 | 19 | Ready for stories | STORY-02.01 enabler (skeleton, CI, fake mailbox), then the date-range slice |
| 2 | [EPIC-01](epics/EPIC-01-secure-gmail-access.md) Secure read-only Gmail access | [PGD-2](https://sankumar76.atlassian.net/browse/PGD-2) | R1 (GUI surfaces R2) | W1, W2, W3 | 17 | Ready for stories | STORY-01.01 redaction path, STORY-01.02 secret files |
| 3 | [EPIC-03](epics/EPIC-03-extract-pdf-attachments.md) Extract PDF attachments | [PGD-4](https://sankumar76.atlassian.net/browse/PGD-4) | R1 | W1 | 12 | Ready for stories | PDF rule, nested and forwarded MIME |
| 4 | [EPIC-04](epics/EPIC-04-predictable-file-naming.md) Predictable file naming | [PGD-5](https://sankumar76.atlassian.net/browse/PGD-5) | R1 | W1 (W2 write-time check) | 12 | Ready for stories | Date prefix, sanitising, collisions |
| 5 | [EPIC-07](epics/EPIC-07-audit-dry-run-cli.md) Audit trail, dry run and CLI | [PGD-8](https://sankumar76.atlassian.net/browse/PGD-8) | R1 | W1 (FR-044, 045), W2 (FR-039..043, 046) | 16 | Ready for stories | STORY-07.01 CLI dry run |
| 6 | [EPIC-05](epics/EPIC-05-safe-saving-rerun-safety.md) Safe saving and re-run safety | [PGD-6](https://sankumar76.atlassian.net/browse/PGD-6) | R1 | W2 | 14 | Ready for stories | Safe save, manifest |
| 7 | [EPIC-06](epics/EPIC-06-resilient-cancellable-runs.md) Resilient, cancellable runs | [PGD-7](https://sankumar76.atlassian.net/browse/PGD-7) | R1 (GUI Cancel R2) | W2 | 5 | Ready for stories | Failure isolation, Ctrl+C |
| 8 | [EPIC-08](epics/EPIC-08-onboarding-documentation.md) Onboarding documentation | [PGD-9](https://sankumar76.atlassian.net/browse/PGD-9) | R1 (GUI part R2) | W3 | 4 | Ready for stories (story 3 held) | README after the CLI stabilises |
| 9 | [EPIC-10](epics/EPIC-10-gui-design-system.md) GUI design system and adaptability | [PGD-11](https://sankumar76.atlassian.net/browse/PGD-11) | R2 | W4, W6 | 17 | **Draft, held by C11** | Tokens and button, after S-02 and ADR-001 Accepted |
| 10 | [EPIC-09](epics/EPIC-09-desktop-gui-workflow.md) Desktop GUI workflow | [PGD-10](https://sankumar76.atlassian.net/browse/PGD-10) | R2 | W5 | 25 | **Draft, held by C11** | Settings window, after EPIC-10 tokens |

R1 = ranks 1-8 (99 pts, v0.9.0, ships alone). R2 = ranks 9-10 (42 pts, v1.0.0). MVP = 141 pts. R3 and backlog items (FR-007, 034, 061, 063 | FR-035, 038) are not ranked here; see the release plan §4 for their triggers.

## 2. Why this order (top-10 explanation)

1. **EPIC-02 first.** Everything else needs a package, CI and a fake mailbox, and the date range plus ordering is the base of every name and every re-run. It carries the two enablers (CC-01) and the benchmark harness that decides the recall-sweep and FR-038 questions early (RISK-007, RISK-011, RISK-014). Learning value is highest here.
2. **EPIC-01 second.** Only its first stories (redaction FR-005, secret files FR-004) are needed in W1: the redaction path must exist before any log or CSV line is written (RISK-005, impact 5). The sign-in stories follow in W2 and the live consent in W3, because live access needs the sponsor's credentials (TR-006) and everything else can be proved on a mock.
3. **EPIC-03.** Extraction turns the selected messages into PDF candidates; without it there is nothing to name. Pure logic, no credentials, fully testable on fixtures.
4. **EPIC-04.** Naming is the sponsor's contract (AC-03, AC-04, AC-06) and the W1 exit check (RD §4.4 example names exact). Placed after extraction because it names what extraction finds.
5. **EPIC-07.** The CLI dry run (FR-044, FR-045) is the first user-visible increment and closes W1: it shows the sponsor the planned names with no credentials and no writes. The audit stories (log, CSV, summary, exit codes) follow in W2 and must precede some EPIC-05 and EPIC-06 stories (CC-06).
6. **EPIC-05.** Safe saving and the manifest give re-run safety (AC-05) and resume. High value and risk reduction (RISK-008), but it needs names (EPIC-04) and the audit writers (EPIC-07).
7. **EPIC-06.** Smallest epic and best value per point (PRD §8 score 14.0) but it depends on the manifest/journal and the summary; it fits after EPIC-05 in W2.
8. **EPIC-08.** The README is meaningful once the CLI is stable and live sign-in works (W3). Its score is high, but it has to describe finished behaviour.
9. **EPIC-10 before EPIC-09.** Tokens first so no screen can hard-code a value (GOAL-08, release plan W4). Both are R2, so they follow R1; both are held until C11 clears.
10. **EPIC-09 last.** The largest epic (25 pts) and the lowest score per point (2.8); it needs the R1 core (progress events, cancellation), ADR-001 Accepted and the EPIC-10 foundation.

## 3. Wave plan and recommended story order for R1

Waves are dependency order, not sprint boundaries (no velocity exists, D-33). The scrum-master sets sprint scope and plans below capacity. Candidate story IDs are in the epic files.

| Wave | Stories in recommended order | Exit check |
|------|------------------------------|------------|
| **W1 Dry-run skeleton on a mocked mailbox** (sprint 1 target) | 02.01 enabler → 01.01 redaction → 01.02 secret files → 02.02 date range → 02.03 invalid input → 02.04 paging → 02.05 order → 02.06 empty range → 02.07 query and Spam/Trash → 03.01 → 03.02 → 03.03 → 03.04 → 04.01 → 04.02 → 04.03 → 04.04 → 04.05 (planning check) → 07.01 CLI dry run → 02.08 benchmark harness | A dry run on the fixture mailbox prints the RD §4.4 names exactly; boundary, nested-MIME and malicious-name tests pass; benchmark harness exists |
| **W2 Safe save, audit, resilience** | 07.02 log → 07.03 CSV → 07.04 summary → 05.01 safe save (+ 04.05 write-time) → 05.02 manifest → 05.03 resume → 06.01 failure isolation → 05.04 unreadable manifest → 05.05 warnings → 06.02 Ctrl+C → 07.05 exit codes → 07.06 reconciliation → 01.03 paths → 01.04 sign-in (mock) → 01.05 recovery → 01.06 missing credentials → 02.09 recall sweep (after CC-02 bound and 02.08 numbers) | Two-run test saves 0 new files; NFR-007/008 loops green; GOAL-10 reconciliation green; scope list asserted |
| **W3 Live access and onboarding** | 01.07 live sign-in (needs TR-006) → 08.01 README setup and first dry run → 08.02 README expiry, recall, manifest, data | Real-mailbox acceptance (at least 10 sponsor-named PDFs, PA-04); README followed unaided; real timing recorded for NFR-001 and GOAL-11 |

Sprint-1 advice to the scrum-master (not an estimate): the full W1 set is probably more than one sprint for a team with no measured velocity. A coherent first cut is 02.01, 01.01, 01.02, 02.02, 02.03, 02.06 and 03.01-03.02, which demonstrates the date-range and extraction path on the fake mailbox; 04.x and 07.01 then complete the dry-run increment.

R2 waves (held by C11): W4 EPIC-10 stories 10.01-10.03 → W5 EPIC-09 stories 09.01-09.07 (+ 08.03) → W6 EPIC-10 stories 10.04-10.05.

## 4. Gates, dependencies and conditions that affect the order

| Item | Effect | Owner |
|------|--------|-------|
| **C11** | No EPIC-09 or EPIC-10 story (and STORY-08.03) may be Ready until spike S-02 (GitHub [#3](https://github.com/sankumar76/PDF-Download-Gmail/issues/3)) passes and ADR-001 is Accepted; applied at every G4, no later than W4 | solution-architect; product-owner and scrum-master apply |
| TR-006 and the named-PDF sample (PA-04) | Block W3 live consent, real-mailbox acceptance and the GOAL-09/GOAL-11 trials; not W1 or W2 | Santhosh |
| CC-02 sweep bound | STORY-02.09 not Ready until ADR-007's gate is restated against NFR-002 (or the AC in the story carries the 0.6 bound) | solution-architect |
| CC-01 enabler sizing | STORY-02.01 and 02.08 sized before sprint 1 is committed | scrum-master |
| W1 benchmark result | May promote FR-038 (parallel fetch) to Must in R1, which would add a story to EPIC-06 | product-manager, solution-architect |
| FR-034 pull-forward trigger | A manifest-loss incident or the sponsor saying re-fetching deleted files is routine moves FR-034 into R1/R2 | product-manager |
| G8 re-checks | Q-04, Q-10 and the PRD §14.3 confirmations; no story depends on them | Santhosh |

## 5. Product-owner ordering decisions (D-PO)

| ID | Decision | Reason | Effect |
|----|----------|--------|--------|
| D-PO-1 | FR-010 and FR-013 (CLI) are scheduled in W1 | The FR-045 flag table test needs the complete flag set in the first CLI | Release plan W2 line unchanged; see CC-09 |
| D-PO-2 | CLI half of FR-006 and the local client-file check are scheduled in W2, not W3 | They need no live access; exit 3 and `check_client_file()` are mock-testable (ADR-003 §4) | Only live consent stays in W3 |
| D-PO-3 | FR-004 (`.gitignore`, secret scan) is scheduled in W1 | Keeps any credential-like fixture out of git from the first commit (NFR-015) | STORY-01.02 |
| D-PO-4 | Engineering foundation is hosted in EPIC-02 as two explicit enabler stories | CC-01 | STORY-02.01, 02.08 |
| D-PO-5 | FR-061 sits in EPIC-09 | CC-04 | PM to confirm |

## 6. Traceability notes
- Every candidate story names at least one FR (or, for the two enablers, the NFRs they serve and a written justification); every FR in the PRD is in exactly one epic (consistency report §2.1).
- No horizontal "build the layer" stories. The two exceptions are the named enablers 02.01 and 02.08 (reason in EPIC-02). EPIC-10's first story is a thin themed window, not "the theme layer".
- Story acceptance criteria will cite PRD fit criteria and the sponsor's AC-01..09 tests; each AC gets an ID (AC-1...) for QA (product-owner, at DoR validation).
- DoR validation of the sprint-1 stories is the next product-owner task, after the scrum-master drafts them.
