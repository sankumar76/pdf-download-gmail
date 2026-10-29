# ADR-006: Core execution model — plan-then-fetch, events, cancellation, retry, dry run (PQ-01)

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-10-29 |
| Deciders | solution-architect |
| Related | D-01, FR-014, FR-036..038, FR-044, FR-050..053, FR-064, NFR-001..004, NFR-006, NFR-009, PQ-01, Q-11, ux-spec UQ-02/UQ-06/UA-03 |

## Context
Names must be deterministic (FR-014: order by `internalDate`, then messageId, then part order), but `messages.list` returns ids in no guaranteed order, so all candidates must be known and dated before the first name is assigned. Both front ends need the same behaviour (FR-064), live progress and cancellation (FR-050/051, NFR-004). The RD prefers bounded memory (NFR-05) and allows ≤ 4 workers only if needed (FR-038). PQ-01 asks whether a dry run fetches bytes.

## Decision Drivers
FR-014 determinism, NFR-001/002 call budget, NFR-009 memory, NFR-004 responsiveness, testability, simplicity.

## Considered Options
### Option A — Three calls per message (`get(minimal)` to sort, then `get(full)` + attachment)
- Pros: tiny retained state.
- Cons: ≈ 15 min per 1,000 messages at 300 ms/call — no margin on NFR-001.
### Option B — Batch HTTP requests for metadata
- Pros: fewer round trips.
- Cons: sub-request error handling, 429s inside batches, harder mocks; complexity before evidence. Kept as a later optimisation.
### Option C — Plan-then-fetch with compact plans (chosen)
- Phase 1 list ids (both queries, ADR-007); Phase 2 one `messages.get(format=full)` per not-yet-complete message, keep a compact `MessagePlan` (ids, date, From, Subject, candidate parts, `attachmentId`s), drop the payload, sort; Phase 3 fetch bytes and save in order.
- Pros: 2 calls per new message (≈ 10 min per 1,000); deterministic; dry run = phases 1–2.
- Cons: retained metadata grows linearly (≈ 1 KB/message) — see AR-03.

## Decision
- Option C, **sequential** in R1. The fetch step sits behind a `fetch_bytes(plan)` seam so FR-038 can add ≤ 4 workers for phase 2/3 fetching later while naming and saving stay on one thread.
- **API:** synchronous `run(request, deps, sink, cancel) -> RunSummary`; events per architecture §6.8 (incl. `TotalKnown`, `ItemStarted`, `error_reason` — UQ-02); `CancelToken` checked before every API call, between candidates and in backoff sleeps (`cancel.wait(delay)`). GUI runs it on a `QThread`; CLI on the main thread with SIGINT → `cancel.set()`.
- **Retry:** own helper (6 attempts, full jitter 1→64 s, `Retry-After` honoured, cancel-aware); the library's `num_retries` stays 0 because it ignores `Retry-After` (verified in `googleapiclient/http.py` via context7).
- **PQ-01 answer — dry run does not fetch attachment bytes.** It runs phases 1–2, reads the manifest and folder listing read-only, and reports `would-save`, `would-save-renamed`, `already-downloaded`. It cannot detect `NOT_A_PDF`; if a real run later rejects a part, later suffixes in the same date/name group can differ — the dry-run output says names are planned, not verified (ux-spec UA-03 notice). Rationale: NFR-002 (≤ 8 min) and "writes nothing" are met with one call per message.
- **Sign-in wait (UQ-06):** `run_local_server(port=0, timeout_seconds=300)`; GUI Cancel abandons the wait immediately (result discarded); CLI timeout → exit 3.
- **Memory (Q-11 remainder):** one message payload and one attachment in memory at a time; `attachments.get` returns base64url JSON, so bytes cannot be streamed from the network; decode then write in 1 MiB chunks with incremental SHA-256. ASSUMPTION-16 confirmed.

## Consequences
- Positive: one code path for CLI, GUI, dry run and real run; deterministic names; NFR-001 margin ≈ 5 min per 1,000 messages for sweep extras and overhead.
- Negative: O(n) metadata in memory (AR-03 asks PM to reword NFR-009's growth clause); a dry run's names are "unverified" for `NOT_A_PDF` cases.
- Follow-up: W1 benchmark story measures NFR-001..003 and NFR-009; if NFR-001 misses, FR-038 is promoted (release plan) before Option B is considered.

## Verification
Determinism test (same fixture, shuffled list order, identical names); dry-run "tree unchanged" test; parity test (dry-run names = real-run names on a fixture with no `NOT_A_PDF`); cancel-latency test (≤ 5 s with 500 ms mock); retry schedule test with a fake clock; benchmarks in test-strategy §7.
