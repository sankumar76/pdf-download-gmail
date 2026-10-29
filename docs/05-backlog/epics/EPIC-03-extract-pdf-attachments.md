# EPIC-03: Extract PDF attachments

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-4](https://sankumar76.atlassian.net/browse/PGD-4) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0) |
| Wave | W1 |
| Priority | Backlog rank 3 of 10 |
| PRD size | M (12 pts, PRD §7) |
| Status | Ready for story slicing (scrum-master) |

## Goal & User Value
Every PDF in a message is found and read, including PDFs inside nested multipart parts and inside forwarded emails, and a message with several PDFs yields all of them. A disguised file is never saved as a PDF (GOAL-01 complete retrieval, GOAL-04 no loss).

## Requirements Covered
- Functional: FR-018, FR-019, FR-020, FR-021.
- Non-functional: NFR-008 (a decode fault does not stop the run; fault-injection point shared with EPIC-06), NFR-009 (one message and one attachment in memory at a time), NFR-016 (body text is never decoded except PDF candidates).
- Business rules / source IDs: BR-008; EC-01, EC-03, EC-04; BRQ-001.

## Scope
**In:**
- Recursive MIME walk, including `multipart/*` and `message/rfc822`, parts in document order (FR-018, `domain.mime`).
- PDF rule: `application/pdf`, or a `.pdf` name (any case) with `application/octet-stream`; Drive links are not attachments (FR-019).
- Bytes from an inline body or a separate attachment, URL-safe base64; one re-fetch of the message if an `attachmentId` is stale (FR-020, AR-05, AA-02).
- `%PDF-` header check; `NOT_A_PDF` for a disguised file; encrypted or corrupt PDFs that pass the header are kept unchanged (FR-021).

**Out:** naming (EPIC-04); saving to disk (EPIC-05); the recall sweep that finds unnamed PDFs (EPIC-02, FR-017).

## UX & Architecture References
- Screens / journeys: no UI of their own; `Not a PDF` label in SCR-06 and the CLI summary when produced ([ux-spec](../../03-ux/ux-spec.md) §9 row 018-021).
- Components: `domain.mime`, `app.downloader`, `infra.gmail_gateway` ([architecture](../../04-architecture/architecture.md) §4.1, §6.2, §12); risk AR-05 (§14).
- ADRs: [ADR-006](../../04-architecture/adr/ADR-006-core-execution-model.md) (dry run fetches no bytes, so `NOT_A_PDF` cannot appear in a dry run).
- PRD: [§4.3](../../02-product/prd.md); release plan W1.

## Stories (ordered)
Candidates only; the scrum-master creates the stories.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-03.01 | Recognise a PDF part | [W1] Type/name matrix decides PDF or not; a Drive-link-only message gives no row (FR-019) | Business-rule variation | 02.02 | Candidate |
| 2 | STORY-03.02 | Find all PDFs in a message, however nested | [W1] Multi-PDF, nested multipart and forwarded `message/rfc822` fixtures all yield every PDF in document order (FR-018) | Data variation (MIME shape) | 03.01 | Candidate |
| 3 | STORY-03.03 | Get the bytes of a PDF | [W1] Inline and separate-attachment bytes decode (URL-safe base64); a stale attachment id is re-fetched once (FR-020) | Data variation | 03.02 | Candidate |
| 4 | STORY-03.04 | Refuse a file that is not a PDF | [W1] Bytes without `%PDF-` are reported `NOT_A_PDF` and not saved; an encrypted PDF is kept as-is (FR-021) | Happy / unhappy path | 03.03 | Candidate |

## Epic Acceptance Criteria
- [ ] Nested and multi-PDF fixtures: every PDF is found, in document order.
- [ ] The type/name matrix test is exact (including `.PDF` with `application/octet-stream`); a Drive-link-only message yields no row.
- [ ] Both bytes representations decode; the stale-attachment re-fetch is covered.
- [ ] A disguised file is not saved and is reported `NOT_A_PDF`; an encrypted PDF passes through unchanged.
- [ ] A decode fault is isolated to its attachment (feeds the NFR-008 fault-injection test in EPIC-06).

## Dependencies & Risks
- Depends on: EPIC-02 (range selection, fake mailbox with MIME fixture builders).
- Risks: AR-05 stale `attachmentId`; memory for 25 MB attachments (NFR-009, measured by STORY-02.08). Fixtures use synthetic data only (CLAUDE.md §6.7).
