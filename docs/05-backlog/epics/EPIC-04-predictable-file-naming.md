# EPIC-04: Predictable file naming

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-5](https://sankumar76.atlassian.net/browse/PGD-5) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0) |
| Wave | W1 (name planning and checks on the fake mailbox); the write-time containment story rides with EPIC-05 in W2 |
| Priority | Backlog rank 4 of 10 |
| PRD size | M (12 pts, PRD §7) |
| Status | Ready for story slicing (scrum-master) |

## Goal & User Value
Every file is named `YYYYMMDD_<name>.pdf`, safe on disk and collision-free, exactly as the sponsor's example table shows, so downloaded files sort by date and nothing collides (GOAL-02 predictable naming, GOAL-04 no path escape).

## Requirements Covered
- Functional: FR-022, FR-023, FR-024, FR-025, FR-026, FR-027.
- Non-functional: NFR-024 (Unicode letters kept, date formats), NFR-020 (long Windows paths, AR-06).
- Business rules / source IDs: BR-001, BR-003, BR-009, BR-010, BR-011; AC-03, AC-04, AC-06; SEC-09.

## Scope
**In:**
- Date prefix from the email's received date in the chosen time zone; `Date` header only as fallback (FR-022).
- Sanitising: folder parts removed, `<>:"/\|?*` and control characters to `_`, spaces collapsed, dots trimmed, RFC 2047/2231 decoded, Unicode kept, `.pdf` lower-case (FR-023).
- 200-character limit applied to the stem only (FR-024); `attachment.pdf` for unnamed PDFs (FR-025).
- Case-insensitive `_1`, `_2` suffixes against files on disk and names assigned earlier in the run (FR-026).
- Containment: planned and final paths resolve inside the output folder, else an `ERROR` row; `\\?\` long-path handling on Windows (FR-027, AR-06, AA-06).

**Out:** writing the file (EPIC-05); the dry-run command surface (EPIC-07).

## UX & Architecture References
- Screens / journeys: planned names in SCR-04, saved names in the CLI and CSV; UJ-02 ([ux-spec](../../03-ux/ux-spec.md) §9 rows 022-027).
- Components: `domain.naming`, `domain.name_allocator`, `infra.file_store` ([architecture](../../04-architecture/architecture.md) §4.1, §6.6, §12).
- ADRs: [ADR-004](../../04-architecture/adr/ADR-004-manifest-and-safe-writes.md) (no-clobber).
- PRD: [§4.4](../../02-product/prd.md); release plan W1.

## Stories (ordered)
Candidates only; the scrum-master creates the stories.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-04.01 | Date-prefixed name from the received date | [W1] `YYYYMMDD_` in the chosen zone, near-midnight correct in two zones; unnamed PDF becomes `attachment.pdf` (FR-022, FR-025) | Workflow step (first name end to end) | 03.02 | Candidate |
| 2 | STORY-04.02 | Sanitise file names | [W1] Table-driven rows including `../../Report:Q4.pdf` giving `20260120_Report_Q4.pdf`, RFC 2047/2231, Unicode kept (FR-023) | Business-rule variation (table rows) | 04.01 | Candidate |
| 3 | STORY-04.03 | Cap the length of a name | [W1] 300-character name shortened at the stem only (FR-024) | Data variation | 04.02 | Candidate |
| 4 | STORY-04.04 | Number name collisions | [W1] `_1`, `_2` against disk and the run, case-insensitive; first file keeps the plain name; RD §4.4 example table 6 of 6 exact (FR-026) | Business-rule variation | 04.02 | Candidate |
| 5 | STORY-04.05 | Never leave the output folder | [W1 planning check, W2 write-time check] Traversal and absolute-path names land inside or give an `ERROR` row; long paths work on Windows (FR-027, AR-06) | Happy / unhappy path | 04.04; the write-time half needs STORY-05.01 | Candidate |

## Epic Acceptance Criteria
- [ ] The RD §4.4 example table reproduces exactly (6 of 6 rows).
- [ ] `../../Report:Q4.pdf` becomes `20260120_Report_Q4.pdf`; a near-midnight message is dated correctly in two zones.
- [ ] A 300-character name keeps its date prefix, suffix and extension and is shortened at the stem only.
- [ ] `Invoice.pdf` and `invoice.PDF` receive distinct names.
- [ ] `../../x.pdf` and absolute-path names never produce a file outside the output folder.
- [ ] A deep Windows path is handled (AA-06 verified on Windows CI).

## Dependencies & Risks
- Depends on: EPIC-03 (candidates to name). Story 5's write-time half depends on EPIC-05.
- Risks: AR-06 `\\?\` long paths (Windows CI test in W1), AA-06. Dry-run names are "planned, not verified" because a dry run fetches no bytes (D-22).
