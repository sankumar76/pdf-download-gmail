# EPIC-05: Safe saving and re-run safety

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-6](https://sankumar76.atlassian.net/browse/PGD-6) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0) |
| Wave | W2 |
| Priority | Backlog rank 6 of 10 |
| PRD size | M (14 pts, PRD §7) |
| Status | Ready for story slicing (scrum-master) |

## Goal & User Value
No existing file is ever overwritten or deleted, and a re-run of the same range adds nothing new. A stopped run can be continued without duplicates or lost attachments (GOAL-03 safe re-runs, GOAL-04 no loss, GOAL-06 resumability).

## Requirements Covered
- Functional: FR-028, FR-029, FR-030, FR-031, FR-032 (Should), FR-033 (Should). Not included: FR-034 (R3 manifest recovery) and FR-035 (backlog skip-identical).
- Non-functional: NFR-007 (interrupt safety, 100 kill points), NFR-010 (manifest of at least 50,000 entries, update at most 50 ms at p95), NFR-003 (journal cost), NFR-013 (permissions on state files).
- Business rules / source IDs: BR-005, BR-006, BR-007; EC-02; AC-05; DR-005 (manifest is Confidential).

## Scope
**In:**
- Temp file, `fsync` and no-clobber move for PDFs; leftover `.part` files ignored and counted (FR-028, ADR-004).
- Manifest (snapshot + journal, last-good backup) keyed by messageId + partId; re-run skips and reports `SKIPPED_ALREADY_DOWNLOADED`; a hand-deleted file is not re-downloaded (FR-029, PD-02).
- Resume after any stop or kill with 0 duplicates and 0 lost (FR-030).
- Different files with the same name are both kept; byte-identical PDFs from different emails are both kept (FR-031).
- Unreadable manifest: the run saves no PDF, leaves the manifest and its backup untouched, names the file, exits 1, and still leaves a run log and a header-only CSV (FR-032, PD-18).
- Missing manifest in a non-empty folder, or manifest entries whose files are missing: warn before and in the summary, stating the `_1` consequence and the new-output-folder advice (FR-033, PD-11).
- The write-time containment check from EPIC-04 story 5.

**Out:** rebuilding a lost manifest from CSV reports (FR-034, R3); skip-identical (FR-035, backlog); GUI notices (EPIC-09).

## UX & Architecture References
- Screens / journeys: UJ-04; DLG-03 (history unreadable), DLG-04, MW-1/MW-2 notices (R2 surfaces); CLI wording in UX §12 ([ux-spec](../../03-ux/ux-spec.md) §9 rows 028-033).
- Components: `infra.file_store`, `infra.manifest`, `app.downloader`, `app.runner`, `domain.messages` ([architecture](../../04-architecture/architecture.md) §4.1, §5, §6.3, §6.7, §10.2 write-path rule, §12).
- ADRs: [ADR-004](../../04-architecture/adr/ADR-004-manifest-and-safe-writes.md); risks AR-04 (POSIX FAT fallback, GitHub #4), RISK-008.
- PRD: [§4.5](../../02-product/prd.md); release plan W2.

## Stories (ordered)
Candidates only; the scrum-master creates the stories.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-05.01 | Save one PDF without ever overwriting | [W2] Temp file, `fsync`, no-clobber move; existing files byte-identical after the run; two same-named different files both kept; identical PDFs from two emails both kept (FR-028, FR-031, FR-027 write-time) | Workflow step (first save end to end) | 04.05, 03.04 | Candidate |
| 2 | STORY-05.02 | Remember what was saved and skip it on re-run | [W2] Manifest + journal; second run 0 new files and 100 % `SKIPPED_ALREADY_DOWNLOADED`; deleted file still skipped (FR-029, AC-05). Also enables the dry-run `already-downloaded` label | Workflow step | 05.01 | Candidate |
| 3 | STORY-05.03 | Continue where a stopped run left off | [W2] Kill at injected points then re-run: 0 duplicates, 0 lost; 100-iteration loop (FR-030, NFR-007) | Happy / unhappy path (interrupt) | 05.02 | Candidate |
| 4 | STORY-05.04 | Stop safely when the download history cannot be read | [W2] No PDF written, manifest and backup untouched, message names the file, exit 1, run log and header-only CSV present; a dry run on the same fixture writes nothing (FR-032, PD-18) | Happy / unhappy path | 05.02; run log and CSV stories STORY-07.02, 07.03 | Candidate |
| 5 | STORY-05.05 | Warn about a missing history or missing files | [W2] Both warning cases with counts; the missing-history text states the `_1` consequence and the new-folder route (FR-033, PD-11) | Business-rule variation (two cases) | 05.02 | Candidate |

## Epic Acceptance Criteria
- [ ] Second run on the same range: 0 new files and 100 % of earlier attachments reported `SKIPPED_ALREADY_DOWNLOADED` (AC-05).
- [ ] Fault-injection loop of 100 stop/kill points: 0 partial files under final names; manifest parses after a graceful stop; after a hard kill at most 1 leftover temp file, ignored on the next run; re-run gives 0 duplicates and 0 lost (NFR-007).
- [ ] An existing file is byte-identical after any run; two different same-named files and two identical PDFs from different emails are all kept.
- [ ] Corrupt-manifest fixture (non-dry run): no PDF written, manifest and backup byte-identical, message shown, exit 1, run log present, CSV holds exactly the header row; a dry run writes nothing.
- [ ] Both FR-033 warnings appear in the CLI with counts; the missing-manifest wording includes the `_1` consequence and the new-folder alternative.
- [ ] Manifest update at most 50 ms at p95 with 10,000 entries (NFR-010).

## Dependencies & Risks
- Depends on: EPIC-04 (names), EPIC-03; story 4 also needs the run log and CSV writers of EPIC-07 (hidden dependency recorded as CC-06 in the consistency report).
- Risks: RISK-008 manifest loss causes duplicates (FR-032/033 in R1, FR-034 pull-forward trigger in the release plan), AR-04/TD (POSIX no-clobber fallback; Windows is unaffected), RISK-010 Must share.
