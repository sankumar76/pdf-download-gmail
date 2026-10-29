# Technical Test Strategy — Gmail PDF Attachment Downloader

| Field | Value |
|-------|-------|
| Version | 0.2 |
| Owner | solution-architect (technical strategy); qa-engineer owns the test plan and acceptance (`docs/07-qa/test-plan.md`) |
| Date | 2026-10-29 |
| Status | In Review (G3 condition C10 closed; G4 entry) |
| Inputs | [architecture.md](architecture.md) v0.2, ADR-001..007, PRD v0.4 (commit 5dc3289; NFR-022 / PD-10, PD-18, PD-19), ux-spec v0.3 (commit 4f1536f; R-COUNT), coding-standards §6, §10 and §11 and definition-of-done as amended (commits e71302b, 834f7d2, 481a46f), D-21..D-34 (D-30 coverage, D-31 pragmas, D-32 file writes) |

## 1. Principles
- **No live Gmail in automated tests** (coding-standards §10). Every automated test runs on synthetic fixtures; the only real-mailbox activity is the sponsor's acceptance run (TR-006, PA-04).
- **No network in unit tests**: a session fixture replaces `socket.socket.connect` and `socket.create_connection` with a function that raises unless the host is loopback, so any accidental egress fails the test (also evidence for NFR-014).
- **No real secrets anywhere**: fake `credentials.json`/`token.json` are generated in `tmp_path` with sentinel values (§6). Developers and agents never open `secrets/` (SEC-08).
- **Deterministic**: fake clock, fake sleeper, seeded jitter, fixed time zones; no dependence on the machine's zone.
- Traceability: test names or markers carry FR/NFR/AC IDs (`@pytest.mark.req("FR-026", "AC-04")`), so qa-engineer can build the AC matrix from `pytest --collect-only`.

## 2. Test Pyramid and Levels

| Level | Scope | Location | Tooling | Share (target) |
|-------|-------|----------|---------|----------------|
| Unit | `domain/*` pure functions (date range, query, MIME walk, PDF rule, naming, allocator, validation, messages), `app/*` with fakes for all ports, `redaction`, `gui/view_model.py` (Qt-free) | `tests/unit/` | pytest, hypothesis **not** used (no new dependency); table-driven `pytest.mark.parametrize` | ≈ 70 % of tests |
| Integration | `infra/*` against real `tmp_path` file systems (file store, manifest, audit, paths, tz) and `infra/gmail_gateway` + `infra/retry` against `googleapiclient.http.HttpMockSequence` (scripted HTTP responses, no network); auth flow with a stub flow object | `tests/integration/` | pytest, googleapiclient's HTTP mocks | ≈ 20 % |
| End-to-end (CLI) | `python -m gmail_pdf` in a **subprocess** with a fixture mailbox injected through `GMAIL_PDF_TEST_FAKE_MAILBOX` (test-only hook in `bootstrap`, refused unless `GMAIL_PDF_TESTING=1`); asserts exit codes, stdout/stderr, files, CSV, log | `tests/e2e/cli/` | pytest + `subprocess` | ≈ 7 % |
| End-to-end (GUI) | Main window flows with `pytest-qt` (`qtbot`), offscreen platform, same fake mailbox | `tests/e2e/gui/` | pytest-qt | ≈ 3 % |
| Performance | NFR-001..003, 009, 010 benchmarks | `tests/perf/` (marker `perf`) | pytest + `time.perf_counter`, `tracemalloc`, `psutil`-free RSS via `resource`/Windows `GetProcessMemoryInfo` through `ctypes` | Nightly / on demand |
| Manual / exploratory | Real-mailbox acceptance (G7), screenshot matrix, Narrator (R3), GOAL-09 stopwatch | `docs/07-qa/` | qa-engineer, ux-expert | Per release |

The test-only fake-mailbox hook is the one production seam added for testing; it is inert unless both environment variables are set, and a unit test asserts it is refused otherwise.

## 3. Gmail API Test Doubles

| Double | Level | What it simulates |
|--------|-------|-------------------|
| `tests/fakes/fake_gmail.py::FakeGmail` (implements `GmailPort`) | unit, e2e | An in-memory mailbox built from fixture builders: messages with `internalDate`, headers, nested `multipart/*` and `message/rfc822` parts, inline vs `attachmentId` bodies, pagination with configurable page size, list order shuffling (FR-014), both search queries (baseline / sweep), scripted faults per call (HTTP 429/5xx/403-rate-limit, 400/404 stale attachment id, timeouts), configurable latency (perf), and a **call recorder** (method, params) used for NFR-011 assertions |
| `HttpMockSequence` scripts | integration | Real `googleapiclient` request building, `fields`/`q` parameters, error parsing, `Retry-After` headers, so the gateway and retry code are tested against the real client library |
| `FakeTokenProvider`, `StubInstalledAppFlow` | unit, integration | Consent success/denied/timeout, `RefreshError("invalid_grant")`, wrong client file |
| `FakeClock`, `FakeSleeper` | unit | Backoff delays and cancel-aware waits without real sleeping |

**Fixture data** (`tests/fixtures/`): builders produce Gmail-shaped JSON (`MessageBuilder().received("2026-01-15T23:59:59", tz).pdf("Invoice.pdf").nested(...).forwarded(...)`). Canonical sets: the RD §4.4 example table (6 rows), boundary messages (00:00:00 start, 23:59:59 end, 00:00:00 next day, DST transitions in `America/New_York`), unnamed PDF found only by the sweep, disguised non-PDF, encrypted-PDF header, malicious names (`../../x.pdf`, absolute, UNC, RFC 2047/2231 encoded, bidi override, 300 characters, Windows reserved characters), Drive-link-only message, 25 MB attachment (generated at test time, not committed). All content is synthetic (CLAUDE.md §6.7).

## 4. GUI Testing Approach (R2)
1. **Presenter first:** `gui/view_model.py` holds all decisions (validation, enabled states, event→display mapping, wording) and is unit-tested without Qt.
2. **Widget tests with pytest-qt** (`QT_QPA_PLATFORM=offscreen`): form validation inline errors (FR-048), dry-run list equals core plan (FR-049), live counts change under a slow fake; R-COUNT holds under a 1,000-event burst (≤ 10 `Progress` signals per second reach the UI thread, ≤ 4 redraws per second, phase changes and the final values drawn at once so the last screen equals the summary) (FR-050, ux-spec v0.3 §0.1, architecture §4.3), Cancel → `Stopping...` → summary within 5 s (FR-051, NFR-004), open-folder/log/CSV calls `QDesktopServices.openUrl` (patched) with the right paths (FR-052), tab order and focus ring presence (FR-060), shortcuts Enter/Ctrl+Enter (PD-15), PlainText rendering of a `<b>`-subject (TB-4).
3. **Responsiveness (NFR-004):** a 50 ms `QTimer` heartbeat records gaps while a 1,000-message fake run emits events; max gap ≤ 200 ms. Launch time measured in a subprocess (`gmail-pdf-gui --exit-after-first-paint` test flag, inert without `GMAIL_PDF_TESTING=1`).
4. **Design-system guards (FR-054..057, GOAL-08):** static tests scan `gmail_pdf/gui/**` (excluding `theme/`) for colour literals (`#[0-9a-fA-F]{3,8}`, `rgb(`), `px`/point-size literals, `QFont(` with sizes, `setStyleSheet(` with literals, and `QPushButton(` outside `widgets/button.py`. A test asserts `tokens.py` defines exactly four type roles.
5. **Contrast (NFR-018):** a unit test computes WCAG ratios for the token pairs listed in ux-spec §7.3.
6. **Screenshot matrix (FR-058/059, NFR-021):** automated captures with `QT_SCALE_FACTOR` 1, 1.5, 2 at 800 × 560 and the clamp case (work area 960 × 520) are archived as CI artefacts for ux-expert/qa review; final evidence is the manual Windows 11 matrix at G7 (ux-spec §7.6). Pixel-diff assertions are **not** used (brittle across font versions).

## 5. Coverage Policy (NFR-022 / PD-10) and Tooling

Thresholds follow coding-standards §6, the DoD and PRD v0.4 NFR-022 / PD-10, as amended by the delivery lead on 2026-10-29 (D-30). D-30 supersedes the 100 %/85 % thresholds of D-24; D-24's measurement method (combined legs, `diff-cover` against `origin/main`, GUI not exempt) is kept.

| Gate | Rule | Command | Where |
|------|------|---------|-------|
| **Changed code** | **≥ 80 %** of changed/added lines in `gmail_pdf/**` covered, measured against `origin/main` | `diff-cover coverage.xml --compare-branch=origin/main --fail-under=80` | Every PR, `coverage` job, on coverage **combined** from the Windows and Ubuntu legs |
| **Whole package** | **≥ 80 %** coverage of `gmail_pdf` (branch coverage included) | `pytest -q --cov=gmail_pdf --cov-branch --cov-report=xml --cov-fail-under=80` | Every PR on the Windows leg (target OS, full suite incl. GUI), and re-checked on the combined data with `coverage report --fail-under=80`. Developers run the same command locally |
| DoD | ≥ 80 % changed code and ≥ 80 % whole package | Same two gates | — |

- **Tool:** `diff-cover` (Apache-2.0, dev-only; ADR-002 dev list). It reads Cobertura `coverage.xml` from `pytest-cov` and the git diff; CI checks out with full history (`fetch-depth: 0`).
- **Cross-OS branches:** coverage data from the Windows and Ubuntu legs is combined (`coverage combine` of uploaded `.coverage.*` files) before `diff-cover`, so `if os.name == "nt"` branches are covered by the leg that runs them. The macOS leg (core + CLI only) reports coverage but has no threshold, because it does not run the GUI suite.
- **GUI code is not exempt.** Thanks to the Qt-free view model and offscreen pytest-qt, GUI glue is executable in CI; it counts toward both gates.
- **`# pragma: no cover`: no exceptions defined.** D-31 supersedes D-25 in full (its exception list, the CI pragma listing and the Major-finding rule all lapse). This strategy defines no coverage exclusions by pragma; a pragma in a diff is an ordinary review point under coding-standards §6.
- The 80 % gates are floors, not targets: security-relevant code (`redaction.py`, `infra/file_store.py`, `infra/manifest.py`, `domain/naming.py`, `domain/name_allocator.py`) is still tested on every branch by the tests in §6 and §8; reviewer-quality checks this at G6.
- Excluded from measurement: `tests/`, `spikes/`, repo-root `gmail_pdf_downloader.py` shim (one line, exercised by an e2e test anyway).

## 6. Security Tests

| Test | Requirement | Method |
|------|-------------|--------|
| Sentinel-secret matrix | FR-005, NFR-012, AC-07 | Fake credentials/token contain unique sentinels (`SENTINEL-CLIENT-SECRET-…`, `SENTINEL-REFRESH-…`, `ya29.SENTINEL…`). Force every error path (missing/invalid credentials, consent denied/timeout, refresh failure, HTTP 401/403/429/500 with sentinel echoed in the response body, decode/write failures, internal exception, KeyboardInterrupt) for CLI (subprocess) and GUI (pytest-qt: dialogs, details pane, copied diagnostics via clipboard). Assert 0 sentinel occurrences in stdout, stderr, log, CSV, manifest, GUI texts, clipboard, and `DEBUG`-level logs |
| Scope and method allow-list | FR-001, NFR-011, AC-01 | Stub flow records requested scopes == `{gmail.readonly}`; `FakeGmail` and `HttpMockSequence` recorders assert only `messages.list`, `messages.get`, `messages.attachments.get`; AST test: no `.modify(`, `.trash(`, `.delete(`, `.send(`, `.insert(`, `.batchModify(`, `getProfile` in `gmail_pdf/` |
| Path traversal / containment | FR-023, FR-027, AC-06 | Malicious-name table; before/after file-system diff of the parent of the output folder |
| No overwrite | FR-028, GOAL-04, coding-standards §10, D-32 | Pre-existing files hashed before and after every e2e run. Pre-created files with the exact run-log and CSV names (same-second start) → the run uses `_1`, the existing files are byte-identical afterwards. A file appearing at the final PDF name between allocation and move → `_n` suffix, no overwrite. AST/grep test: `os.replace` appears only in `infra/manifest.py` and `infra/auth.py` (plus the ADR-004 POSIX FAT fallback in `infra/file_store.py`, accepted debt AR-04) |
| Token file protection | FR-004, NFR-013 | POSIX: mode `0600`/`0700` asserted (Ubuntu/macOS legs); Windows: default path under `Path.home()`; warning on outside path |
| `.gitignore` coverage | SEC-05, NFR-013 | Test asserts each required pattern is present and `git check-ignore` matches sample paths |
| Egress | NFR-014 | Socket guard (unit); host recorder on a custom `httplib2.Http` in integration tests asserts only Google hosts |
| Body-text minimisation | NFR-016 | Fixture body contains a sentinel sentence; asserted absent from log/CSV/manifest |
| Injection | TB-4 | CSV formula neutralisation; control characters in log lines; PlainText in GUI |
| Static / supply chain | coding-standards §11 | `ruff` (incl. `S` rules), `bandit -r gmail_pdf`, `pip-audit -r requirements.txt`, gitleaks on the PR diff, dependency allow-list test (ADR-002) |

## 7. Performance Tests (NFR-001..004, 009, 010)

| NFR | Test | Set-up | Pass |
|-----|------|--------|------|
| NFR-001 | `test_first_run_throughput` | `FakeGmail` with 1,000 matched messages × one 1 MB PDF, **300 ms sleep per call** (real sleep, so the test runs ≈ 10 min; marker `perf`, nightly); sweep ratio parameter 0 / 0.5 / 1.0 (ADR-007 S-01) | Wall clock ≤ 15 min at ratio 0; report the others |
| NFR-002 | `test_rerun_and_dry_run_scan` | Same mailbox after a completed run; and a dry run on a fresh folder | ≤ 8 min each (re-run expected ≪ 1 min because complete messages skip `messages.get`) |
| NFR-003 | `test_overhead_per_message` | Zero-latency fake, 1,000 messages, per-message timer around core work | p95 ≤ 50 ms (Windows runner + reference machine) |
| NFR-004 | GUI heartbeat + launch time | §4 item 3; 10 cold launches on the reference machine (manual record) | Stall ≤ 200 ms; launch ≤ 3 s p95; Cancel ≤ 5 s with 500 ms fake latency |
| NFR-009 | `test_memory_bounds` | 25 MB attachment; 500- vs 10,000-message fixtures; `tracemalloc` peak + process RSS | ≤ 300 MB peak; growth per architecture AR-03 wording (reported against both the PRD clause and the proposed per-message bound until PM decides) |
| NFR-010 | `test_manifest_scale` | Journal append micro-benchmark with 10,000 and 50,000 existing entries; load time | Append p95 ≤ 50 ms; 50,000 entries load and compact correctly |

**Reference machine (AA):** the sponsor's Windows 11 laptop for the recorded numbers; CI runners give trend data only (shared hardware). The W1 benchmark story produces the first baseline; a miss on NFR-001/002 triggers FR-038 (release plan).

## 8. Reliability and Audit Tests
- **Interrupt safety (NFR-007):** a subprocess harness runs the CLI on a 50-attachment fixture and kills it with `os._exit` at 100 injected points (env-selected: after temp write, after `pending`, after move, after `commit`, after CSV row, during compaction), then re-runs to completion. Assert per iteration: no partial file under a final name, ≤ 1 `.part` leftover, final set equals the expected names, 0 duplicates, 0 missing, manifest parses.
- **Graceful cancel:** Ctrl+C (CLI: `CTRL_BREAK_EVENT`/`SIGINT` to a process group) and GUI Cancel at random points: exit 1, `Run cancelled` first line, manifest valid, summary present.
- **Failure isolation (NFR-008):** one fault each at message fetch, attachment fetch, decode, disk write (read-only file or full-disk fake) → other files saved, `ERROR` rows, exit 1.
- **GOAL-10 reconciliation (NFR-005):** six scripted runs (success, some errors, cancelled, zero matches, auth failure, hard kill) through CLI and GUI; checker asserts log + CSV exist, header equals LOG-02 exactly, one row per candidate, statuses ∈ LOG-03, per-status counts equal the summary; hard-kill case ≤ 1 row missing.
- **Exit codes (FR-043, PD-13):** one test per code 0/1/2/3 plus cancel, unreadable manifest, injected internal failure (all exit 1 with distinct first lines, no traceback); `--help` exits 0 with no network and no credential read (PD-16).
- **Parity (FR-064, GOAL-07):** same fixture through CLI and GUI; CSVs equal after removing timestamp-bearing values; manifests equal ignoring `recorded_at`.
- **Determinism (FR-014):** fake list order shuffled across runs; names identical.

## 9. Environments and CI Pipeline

| Environment | Purpose | Data |
|-------------|---------|------|
| Developer machine | TDD, fast suite (`pytest -q -m "not perf"`) | Synthetic only |
| GitHub Actions | PR gates and nightly perf | Synthetic only; **no secrets configured** |
| Sponsor machine | W3 real-mailbox acceptance, GOAL-09 trials, NFR-001 real timing | Real mailbox (owner-run; agents never see contents) |

**Pipeline stages (per PR; workflow created in the first W1 story):**
1. `lint` — `ruff check .` and `ruff format --check .`
2. `types` — `mypy gmail_pdf --strict`
3. `test` — matrix: `windows-latest` × Python 3.10/3.11/3.12 (full suite incl. GUI offscreen from R2); `ubuntu-latest` × 3.12 (full suite; GUI offscreen); `macos-latest` × 3.12 (core + CLI). Coverage XML per leg.
4. `coverage` — combine Windows + Ubuntu data, `coverage report --fail-under=80` (whole package), `diff-cover --fail-under=80` (changed code).
5. `security` — `pip-audit`, `bandit -r gmail_pdf`, gitleaks, dependency allow-list test.
6. `package` — build wheel, install in a clean venv on Windows, run `gmail-pdf --help` and an offscreen GUI start (ADR-005).
7. Nightly: `perf` marker suite on `windows-latest`; artefacts: timings, memory, screenshot matrix.

The CLAUDE.md §1 build command installs runtime pins only; CI and developers install `requirements-dev.txt` (raised to the delivery lead, architecture §16).

## 10. Test Data Management
- Fixtures are code (builders) plus small JSON payloads under `tests/fixtures/`; large binaries are generated at test time.
- No real names, addresses or subjects: use `example.com` / `example.org` and lorem-style subjects.
- Every fixture mailbox is reproducible from a seed; perf fixtures are generated, never committed.

## 11. Responsibilities
| Activity | Owner |
|----------|-------|
| Unit/integration/e2e tests per story, coverage gates green | developer |
| Test plan, AC matrix (AC-01..09 × CLI/GUI), exploratory, sentinel matrix review, reconciliation evidence, G7 reports | qa-engineer |
| Screenshot matrix and FR-062 checklist review | ux-expert + qa-engineer |
| Fake mailbox and fixture builders (first W1 story) | developer (design here) |
| Real-mailbox acceptance and GOAL-09 trials | Santhosh with qa-engineer |
| Strategy changes | solution-architect (this document) |

## 12. Change Log
| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1 | 2026-10-29 | solution-architect | First version for G3 (commit 75b7e47) |
| 0.2 | 2026-10-29 | solution-architect | Closes G3 **C10** (test-strategy part). §5: gates are ≥ 80 % changed code (`diff-cover --fail-under=80`) and ≥ 80 % whole package (`--cov-fail-under=80`), per the amended coding-standards §6/DoD, PRD v0.4 NFR-022 and D-30; the 100 %/85 % gates of D-24 are superseded. The `# pragma: no cover` exception list is removed (D-31 supersedes D-25). Whole-package threshold applied to the Windows leg and the combined data, not to the macOS leg. §4: R-COUNT test (≤ 10 Hz to the UI thread, ≤ 4 redraws per second). §6: no-overwrite test covers exclusive create of the run log and CSV and the `os.replace` allow-list (coding-standards §10, D-32). §9: pragma report removed. Inputs cite ux-spec v0.3 (4f1536f) and PRD v0.4 (5dc3289) |
