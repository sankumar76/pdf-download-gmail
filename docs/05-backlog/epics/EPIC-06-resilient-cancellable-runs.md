# EPIC-06: Resilient, cancellable runs

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-7](https://sankumar76.atlassian.net/browse/PGD-7) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0); the GUI Cancel control is FR-051 in EPIC-09 (R2) |
| Wave | W2 |
| Priority | Backlog rank 7 of 10 |
| PRD size | S (5 pts, PRD §7) |
| Status | Ready for story slicing (scrum-master) |

## Goal & User Value
One failing message or attachment never stops a long run, and a deliberate stop never harms the files already saved or the audit trail (GOAL-06 resilience and resumability, GOAL-10).

## Requirements Covered
- Functional: FR-036, FR-037 (CLI part). Not included: FR-038 parallel fetching (backlog; promoted to Must in R1 only if the first benchmark misses NFR-001/002).
- Non-functional: NFR-007 (interrupt safety), NFR-008 (failure isolation), NFR-004 (Cancel takes effect within 5 s; the GUI half is in EPIC-09), NFR-006 (cancel-aware backoff sleeps).
- Business rules / source IDs: NFR-02, NFR-03 (RD); UR-006; EC-07.

## Scope
**In:**
- Per-message and per-attachment failure isolation: an `ERROR` row, the rest continues, summary, exit 1 (FR-036).
- CLI stop with Ctrl+C: current file finished or discarded, manifest saved, log and CSV closed, summary with "Run cancelled", saved files kept, re-run continues, exit 1; second Ctrl+C prints `Already stopping, please wait.` once (FR-037, PD-13, UX-I-05).

**Out:** GUI Cancel button, `Stopping...` state and DLG-06 (EPIC-09); parallel fetching (FR-038).

## UX & Architecture References
- Screens / journeys: UJ-06; CLI Cancel in UX §12; SCR-05 and DLG-06 are R2 ([ux-spec](../../03-ux/ux-spec.md) §9 rows 036, 037).
- Components: `app.runner`, `app.downloader`, `domain.events` (`CancelToken`), `infra.retry`, `cli.main` ([architecture](../../04-architecture/architecture.md) §4.1, §4.2, §6.4, §6.9, §12).
- ADRs: [ADR-006](../../04-architecture/adr/ADR-006-core-execution-model.md).
- PRD: [§4.6](../../02-product/prd.md); release plan W2.

## Stories (ordered)
Candidates only; the scrum-master creates the stories.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-06.01 | Keep going when one item fails | [W2] Faults at message fetch, attachment fetch, decode and write give `ERROR` rows, other attachments are saved, exit 1 (FR-036, NFR-008) | Happy / unhappy path | 05.01, 07.03 (CSV rows) | Candidate |
| 2 | STORY-06.02 | Stop a CLI run safely with Ctrl+C | [W2] No temp file remains, manifest valid, "Run cancelled" summary, exit 1, re-run continues (FR-037, NFR-004, NFR-007) | Workflow step (stop and resume) | 06.01, 05.03, 07.04 (summary) | Candidate |

## Epic Acceptance Criteria
- [ ] Faults injected at message fetch, attachment fetch, decode and disk write: 100 % of other attachments are saved and the exit code is 1.
- [ ] Stop mid-run: no temp file remains, the manifest parses, the summary says the run was cancelled, that saved files are kept and that running the same range again continues.
- [ ] A cancelled run exits 1 with the first line `Run cancelled` (never 0, 2 or 3).
- [ ] Cancel takes effect within 5 s with the mock latency at 500 ms or less.
- [ ] After a stop, re-running the range gives 0 duplicates and 0 lost.

## Dependencies & Risks
- Depends on: EPIC-05 (manifest and journal), EPIC-07 (CSV rows, summary, exit codes).
- Risks: RISK-010 (Must share). Smallest epic by points but it carries two of the nine acceptance behaviours; keep its test evidence (fault-injection loop) in the QA plan.
