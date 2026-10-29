# ADR-007: Candidate search and recall sweep (Q-07, FR-017, RISK-007)

| Field | Value |
|-------|-------|
| Status | Accepted — sweep ON by default; cost gate confirmed by measurement S-01 (W1 synthetic, W3 real mailbox) |
| Date | 2026-10-29 |
| Deciders | solution-architect (+ product-manager for the residual under PD-06) |
| Related | FR-009, FR-012, FR-017, FR-019, FR-025, NFR-001, NFR-002, PD-06 (D-09), RISK-007, Q-07, ASSUMPTION-15 |

## Context
RD FR-02 searches `has:attachment filename:pdf`. A PDF part with no file name, or a name the Gmail index does not match, may never be returned (RISK-007), so FR-025's `attachment.pdf` would never apply. Gmail's exact matching rules for `filename:` (does it match by MIME type when there is no name?) are not documented precisely enough to rely on, and the real mailbox cannot be queried before TR-006. FR-017 (Should) asks for a method whose cost fits NFR-001/002, otherwise the residual gap is accepted (PD-06).

## Decision Drivers
GOAL-01 recall, NFR-001 (≤ 15 min/1,000), NFR-002 (≤ 8 min re-run), FR-045 (no new flags), simplicity.

## Considered Options
### Option A — Baseline only (RD FR-02)
- Pros: cheapest. Cons: silent recall gap (RISK-007).
### Option B — Broad search only: `has:attachment` + local filter
- Pros: one query, maximal recall within "has attachment".
- Cons: every attachment message (images, office files) costs a `messages.get`, with no way to tell how many in advance; no visibility of what the sweep added.
### Option C — Baseline + complementary sweep `has:attachment -filename:pdf` (chosen)
- Pros: the baseline set is unchanged (RD-faithful); the sweep's extra messages are counted separately (`TotalKnown.sweep_extra`) so cost and benefit are measurable per run; sweep-only messages with 0 PDFs are recorded as `message_done` and never re-fetched on re-runs (NFR-002 unaffected after the first run).
- Cons: one more `list` pass; first-run cost grows with the number of non-PDF attachment messages.

## Decision
Option C, **enabled by default** (internal constant `RECALL_SWEEP = True`, not a CLI flag — FR-045). Both queries use the same ±1 s epoch bounds and the user's `--query`. Ids are de-duplicated; the union is planned and sorted together, so naming is unaffected by which query found a message. PDF detection is the local FR-019 rule plus FR-021's header check.

**Cost gate.** Budget: 1,000 baseline messages × 2 calls × 0.3 s ≈ 600 s; NFR-001 allows 900 s, so the sweep may add up to ≈ 800 extra `messages.get` calls per 1,000 baseline messages after overhead. Measurement S-01:
1. W1 (synthetic): benchmark with sweep ratios 0, 0.5, 1.0 → confirm the linear model.
2. W3 (real mailbox, sponsor run, dry run on the one-week acceptance range): record `baseline`, `sweep_extra`, and how many sweep messages contained a PDF.
If `sweep_extra / baseline > 0.8` on the real sample, or the sweep finds 0 PDFs, the architect raises a scope note to PM: either switch the constant off (gap accepted per PD-06, README states it) or promote FR-038 workers. The run summary always shows "messages scanned", which includes sweep messages.

## Consequences
- Positive: FR-017 delivered in R1 without new flags; residual risk is measurable on every run; PD-06's fallback stays available by flipping one constant.
- Negative: first-run time increases on mailboxes with many non-PDF attachments; dry runs also pay the sweep cost.
- Follow-up: GitHub issue (architecture) tracks S-01; README (FR-066) documents the sweep and the remaining gap (PDFs inside messages Gmail does not mark `has:attachment` — not addressable without scanning every message).

## Verification
Unit tests for both query strings; fixture with an unnamed `application/pdf` part found only by the sweep and saved as `YYYYMMDD_attachment.pdf`; benchmark at sweep ratios 0/0.5/1.0; S-01 numbers recorded in this ADR at W3.
