# ADR-004: Manifest (snapshot + journal), no-clobber writes and de-duplication

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-10-29 |
| Deciders | solution-architect |
| Related | FR-026..035, FR-037, NFR-003, NFR-007, NFR-010, BR-003/005/006/007, PD-02 (D-05), RISK-008, coding-standards §10 |

## Context
RD FR-16/17 require temp-file + atomic rename, never overwrite, and a manifest `downloads/.manifest.json` keyed by `messageId` + `partId`. PD-02 makes the manifest authoritative, stops on an unreadable one, warns on a missing one and adds recovery in R3. NFR-007 requires 0 duplicates and 0 lost attachments after 100 hard kills; NFR-010 requires ≤ 50 ms p95 per update with 10,000 entries and capacity ≥ 50,000. No database is allowed.

Two technical facts shape the design: (1) `os.replace` **overwrites** an existing target on every OS, so it cannot implement "never overwrite"; (2) rewriting a multi-MB JSON file after every attachment costs tens of ms plus `fsync` and grows with the manifest.

## Decision Drivers
NFR-007, NFR-010, NFR-003, FR-028, FR-032, RISK-008, no new dependency.

## Considered Options
### Option A — Rewrite `.manifest.json` atomically after each attachment
- Pros: simplest format.
- Cons: O(n) per update (fails NFR-010 at scale); a crash between file move and manifest write still leaves an unrecorded file → `_1` duplicate on re-run.
### Option B — SQLite file
- Pros: transactional.
- Cons: violates CONSTRAINT-04 "no database" in spirit; opaque to the user. Rejected.
### Option C — Snapshot + append-only journal with two-phase records (chosen)
- Pros: O(1) durable append per attachment; crash-consistent; keeps the RD file name for the snapshot; human-readable JSON.
- Cons: two files; load must replay and validate.

## Decision
**Files:** `.manifest.json` (snapshot), `.manifest.journal` (JSON Lines), `.manifest.json.bak` (last good snapshot).

**Write protocol per PDF** (single-threaded):
1. Allocate the name (case-insensitive, ADR context in architecture §6.6).
2. Write bytes to `<out>/.gmail_pdf-<uuid4>.part`, hashing incrementally; `flush` + `os.fsync`.
3. Append `{"op":"pending","key":…,"saved_file":…,"sha256":…}` to the journal; `fsync`.
4. **No-clobber move** temp → final: Windows `os.rename` (raises `FileExistsError` if the target exists — atomic, no race); POSIX `os.link(temp, final)` (fails if the target exists) then `os.unlink(temp)`; if hard links are unsupported (FAT/exFAT: `EPERM`/`ENOTSUP`/`EXDEV`), fall back to an existence check + `os.replace` (narrow race, AR-04). `FileExistsError` → next suffix, retry.
5. Append `{"op":"commit","key":…, …full entry…}`; `fsync`. After the last candidate of a message: `{"op":"message_done","message_id":…,"detector_version":…,"internal_date_ms":…}`.
6. Write the CSV row (flush).

**Load:** read snapshot (if present) → replay journal. A torn **last** journal line is ignored (crash during append). Any other parse/schema error, or `schema_version` newer than supported → **unreadable** (FR-032: stop, exit 1, nothing modified). A `pending` without `commit`: if the final file exists **and** its SHA-256 matches, promote to committed; otherwise drop (its temp file, if any, is a leftover). Leftover `.gmail_pdf-*.part` files are ignored and counted in a `TEMP_LEFTOVERS` warning (never deleted automatically — FR-028).

**Compaction:** at run end or graceful cancel: copy current snapshot to `.bak`, write the new snapshot via temp + `os.replace` (the app owns this file), then truncate the journal. Never in a dry run.

**What is recorded (UA-06):** `SAVED`, `SAVED_RENAMED`, `NOT_A_PDF` entries; `ERROR` is never recorded, so errors are retried next run. Entries store LOG-02 fields so skipped items produce full CSV rows without re-fetching.

**De-duplication:** key `messageId:partId` only (never `attachmentId`, never content hash by default — BR-007/FR-031). Messages with `message_done` and the current `detector_version` are skipped before `messages.get` (NFR-002). Optional SHA-256 index for FR-035 (backlog) is built in memory at load.

**FR-033 warnings:** (a) no manifest and `^\d{8}_.+\.pdf$` files present; (b) entries whose `saved_file` is not in the directory listing.

**FR-034 (R3) recovery:** with no manifest, read `logs/report_*.csv` (newest first); for rows `SAVED`/`SAVED_RENAMED` whose `saved_file` exists and whose SHA-256 matches, claim the file for that key (each file claimed once); write a fresh snapshot; unmatched files are left alone.

## Consequences
- Positive: meets NFR-007/010 without a database; crash windows are closed by the pending/commit pair; manifest is inspectable.
- Negative: two extra `fsync`s per PDF (budgeted in NFR-003); the POSIX FAT fallback has a race (single-user tool; documented); `.bak` is one generation only.
- **Standards note:** coding-standards §10 says "temp file + atomic `os.replace`; never overwrite". For user-visible files these conflict; this ADR's no-clobber move is the rule, `os.replace` is limited to app-owned files (snapshot, token). Raised to reviewer-standards/master.

## Verification
100-iteration kill-point loop (NFR-007) with `os._exit` injected after each step 2–6; manifest micro-benchmark at 10,000/50,000 entries (NFR-010); corrupt-snapshot, corrupt-middle-journal and torn-last-line fixtures (FR-032); FAT fallback unit-tested with a fake `os.link` raising `EPERM`.
