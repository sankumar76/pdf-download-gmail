# EPIC-08: Onboarding documentation

| Field | Value |
|-------|-------|
| Owner | product-owner |
| Jira | [PGD-9](https://sankumar76.atlassian.net/browse/PGD-9) (relates to Intake [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1)) |
| Release | R1 Core + CLI (v0.9.0); the GUI sections of the README are R2 |
| Wave | W3 (drafting can start in W2 as the CLI stabilises) |
| Priority | Backlog rank 8 of 10 |
| PRD size | S (4 pts, PRD §7) |
| Status | Ready for story slicing (scrum-master); story 3 held under C11 |

## Goal & User Value
A reader who does not know the project completes the one-time Google setup, runs a dry run and then a real run, and understands flags, exit codes, output layout and what to do when something goes wrong (GOAL-09 ease of first use, GOAL-05).

## Requirements Covered
- Functional: FR-065 (Must; GUI parts R2), FR-066 (Should).
- Non-functional: NFR-016 (data-handling note), NFR-014 (no telemetry statement).
- Business rules / source IDs: TR-001..004; RISK-003, RISK-007, RISK-009; Q-10 (assumption PA-08); UX-I-04 (env-var sentence).

## Scope
**In:**
- README: one-time Google setup (RD §2.1), CLI usage, every flag and default, exit codes (0-3 plus the three exit-1 outcomes), output layout (`logs/`, manifest, CSV BOM) (FR-065).
- Explains 7-day token expiry in Testing status and publishing to "In production"; how to revoke access; the search-recall sweep and residual gap (ADR-007, PD-06); manifest rules including re-fetching a deleted file via a new output folder and why deleting the manifest is not advised (PD-11); downloads and logs hold third-party data and are the user's to protect and delete; the sentence on sharing sign-in between CLI and GUI (FR-066).
- The setup steps are the same text constant as the in-app setup help (single source).

**Out:** installer or packaged executable (Won't; ADR-005); GUI screenshots until R2.

## UX & Architecture References
- Screens / journeys: UJ-01; SCR-03 and DLG-07 reuse the README text ([ux-spec](../../03-ux/ux-spec.md) §9 rows 065, 066; §11 note for product-owner/scrum-master).
- Components: README, `domain.messages` setup text ([architecture](../../04-architecture/architecture.md) §12 row FR-065/066).
- ADRs: [ADR-005](../../04-architecture/adr/ADR-005-packaging-distribution.md) (pip install, entry points), [ADR-007](../../04-architecture/adr/ADR-007-candidate-search-recall.md).
- PRD: [§4.11](../../02-product/prd.md); release plan W3.

## Stories (ordered)
Candidates only; the scrum-master creates the stories.

| # | Story ID | Title | Intent (one line) | Splitting pattern | Depends on | Status |
|---|----------|-------|-------------------|-------------------|------------|--------|
| 1 | STORY-08.01 | README: set up Google access and complete a first dry run | [W3] Setup steps, install, CLI flags, exit codes, output layout; an unfamiliar reader reaches a successful dry run (FR-065) | Workflow step | 01.06, 07.01, 07.05 | Candidate |
| 2 | STORY-08.02 | README: expiry, revoke, recall gap, manifest rules and data handling | [W3] Sections present and reviewed by reviewer-standards (FR-066) | Business-rule variation (topics) | 08.01, 02.09, 05.05 | Candidate |
| 3 | STORY-08.03 | README: run the GUI | [R2, W5-W6] GUI usage and screenshots; part of FR-065. Held like the EPIC-09 stories until S-02 passes and ADR-001 is Accepted (see consistency report CC-05) | Workflow step | EPIC-09 stories; C11 | Candidate (held) |

## Epic Acceptance Criteria
- [ ] A reader unfamiliar with the project follows the README to a successful dry run (also the GOAL-09 trial, with the sponsor at G7).
- [ ] The README sections for token expiry, revocation, recall gap, manifest rules and data handling are present and reviewed by reviewer-standards.
- [ ] The setup steps in the README equal the in-app text (one source).
- [ ] No secret, personal data or real mailbox content appears in the README or its examples.

## Dependencies & Risks
- Depends on: EPIC-01 (setup behaviour), EPIC-07 (flags, exit codes). The sponsor-run unaided check needs TR-006 (credentials).
- Risks: RISK-003 (token expiry surprises the sponsor), RISK-007, RISK-009; Q-04 and Q-10 are re-checked at G8 (D-34) and may change wording.
