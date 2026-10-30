# Test Report — PGD-14 (STORY-01.02): Keep secret files out of git and protected on disk

| Field | Value |
|-------|-------|
| Tester | qa-engineer |
| Build / commit | `6bd795b` on `feat/PGD-14-secret-files` (PR #17; base `main` at `1ce8473`; 4 commits, 9 files, +1,133 lines) |
| Environment | Local: Windows 11, CPython 3.12.10 (hash-pinned dev install; main-checkout code confirmed by import path). POSIX: `python:3.12-slim` container (CPython 3.12.16), non-root uid 1000, `--network none`, repository mounted read-only. CI: GitHub Actions run 41005608058. Synthetic data only; no real network call; git always isolated from user and system configuration |
| Date | 2026-10-30 |
| Gate | G7 QA Acceptance, attempt 1 |
| **Recommendation** | **ACCEPT** (5 of 5 ACs verified; QUA-15, QUA-16 and QUA-21 re-verified fixed; 0 open Sev-1, Sev-2 or Sev-3; 2 open Sev-4 defects, not blocking) |

## Summary

All five acceptance criteria pass on the final head. I re-ran the full suite on Windows (398 passed, 11 skipped, repeatable, and each of the 15 test files alone), ran the 11 POSIX-only tests plus the rest of the integration and unit tests on Linux as a non-root user (88 passed, 3 Windows-only skips), and confirmed CI is 10 of 10 green on `6bd795b`. I then probed the `.gitignore` in temp repositories (CRLF and LF, case-sensitive and case-insensitive), the two file helpers on both operating systems (umasks, wider pre-existing permissions, read-only and locked targets, symlinks, planted temp files, a kill between write and replace, concurrency), and `token_location_warning` with more than 30 path shapes across both operating systems, including NUL, invalid characters, UNC and drive variants. The three G6 re-checks hold. Exploratory work found two Sev-4 gaps (DEF-003, DEF-004); neither fails an AC.

## AC Verification Matrix

Test IDs are `file::test` under `tests/`. The `req` marker (`FR-004`, `NFR-013`, `NFR-015`, `AC-n`) is on every test; the story-key form of the marker is still open question OQ-4 of the test plan.

| AC | Test ID(s) | Technique | Result | Evidence |
|----|-----------|-----------|--------|----------|
| AC-1 | `unit/test_gitignore_patterns.py` (27 tests: every required pattern present, pre-existing lines kept and in order, no duplicates, artefact patterns); `e2e/test_gitignore_matching.py` (47 tests: `git check-ignore` in a scratch repo over 25 ignored and 6 trackable paths) | Equivalence classes (listed samples, near-misses), boundary (pattern at depth), mutation | ✅ Pass | The 11 patterns of the AC are present and the 5 original lines are intact (diff against `origin/main`: additions only). My own probe in four temp repos (LF and CRLF, `core.ignorecase` true and false): 34 sample paths ignored, 14 ordinary paths not (including `.gitignore`, `.coveragerc`, `secretsX/`, `download/`, `tokens.json`). The working-tree `.gitignore` here is CRLF (autocrlf) and still matches. **Mutation:** removing any one of 13 required patterns fails the shipped tests (13 of 13). Gaps in the negative guard: DEF-004 |
| AC-2 | `integration/test_private_files.py` AC-2 group (32 tests, 11 POSIX-only skipped on Windows with a reason): modes under umask 022 and 077, overwrite, wider pre-existing folder and file, `os.open` flags and mode `0o600` with `O_EXCL` asserted on every platform, chmod recorded or absent per platform | State and mode checks; decision table over umask × pre-existing state | ✅ Pass | **Linux, non-root:** the whole POSIX group passes (88 passed, 3 skipped). My probe: after `ensure_private_dir` and two `write_private_text` calls the folder is `0700` and the file `0600` under umask 022, 077, 000 and 002 (parents keep the default mode, as documented); a pre-existing `0777` folder and `0666` file end `0700` and `0600`; an existing `0400` file is replaced with `0600`; a symlink at the target is replaced by a regular file and the pointee (`0644`) is untouched. Windows: no chmod is called (flag-gated); protection is the profile ACL. **Not run:** macOS (CI `test (macos-312)` is green; the skip counts of the CI legs are not visible to me through the API, so I rely on the Linux container for the POSIX evidence) |
| AC-3 | `integration/test_private_files.py::test_ac3_*`: injected `OSError` at open, fsync, chmod and replace leaves the old content, no temp file, and no content in the error; unencodable text; temp-removal failure is logged | Fault injection; negative paths | ✅ Pass | Probe (Windows and Linux): errors for a missing parent, a directory as target, a read-only attribute / `0500` folder, a target held open by another handle (Windows `PermissionError`), an over-long name and an invalid character are all `PrivateFileError` with the fixed message; previous content intact and no `.tmp` left in every case; the sentinel secret never appears in `str` or `repr` of the error; a lone surrogate gives the fixed encoding message with no chained text. A planted symlink at the temp name (forced collision) fails safe and the victim file is unchanged (`O_EXCL`). A process killed between temp write and replace (`os._exit` in a child) leaves the old token intact and one stale `.token.json.<hex>.tmp` (mode `0600`), which the new `.*.tmp` pattern ignores. Gap: DEF-003 (NUL or nameless path raises a raw `ValueError`) |
| AC-4 | `unit/test_token_location_warning.py` (21 tests; 3 Windows-only ran here, skipped on Linux): inside, outside, `..`, symlinks, spaces, relative, unresolvable path never raises, NUL in path and in home | Equivalence classes; boundary (sibling prefix); error guessing | ✅ Pass | Windows probe, 25 shapes: inside, inside in upper case, lower case and with forward slashes give no warning; other drive, `C:\ProgramData`, sibling prefix (`...\sanku2`), `..` escape give the warning; **NUL in path, NUL in home, a relative home, a device name** give the warning and **never raise**. Linux: symlink out of home warns, symlink loop warns, very long path does not raise. It never blocks. Advisory false positives (fail safe, noted below): `\\?\C:\Users\...`, `\\localhost\C$\...` and relative `home`. **8.3 short names could not be tested** (this volume has no distinct short name) |
| AC-5 | `e2e/test_gitignore_matching.py::test_ac5_*` (`git ls-files -c -i --exclude-per-directory=.gitignore` must be empty on the repository; checker proven in a scratch repo); CI `security` (gitleaks, bandit) | Negative test (a force-added secret must be reported), evidence review | ✅ Pass | The tracked-files check passes on the real tree. In a temp repo a force-added `secrets/token.json` is reported by the checker; a tracked file ignored only by `.git/info/exclude` or a global excludes file is **not** reported (QUA-16 behaviour). No code or test reads a real `secrets/` folder: the only `Path.home()` is in a docstring and every test uses `tmp_path`. gitleaks is not installed here: CI `security` is green on `6bd795b`. |

## Re-checks of G6 findings

| Finding | Result | Evidence |
|---------|--------|----------|
| **QUA-15** (Major, D-45): `token_location_warning` must never raise | ✅ Fixed | NUL in path, NUL in home, relative home, invalid characters, symlink loop, 300-character and 5,000-character names, device name: all return a warning or `None`, none raises (Windows and Linux) |
| **QUA-16**: git tests leaked user-level ignore and `.git/info/exclude` | ✅ Fixed | Checker run against a temp repo with an `info/exclude` and a global excludes file: no false findings; the real `.gitignore` still reports the tracked secret. Removing `token.json` from the patterns still fails the tests, so a user-level rule cannot mask it |
| **QUA-21**: inherited `GIT_INDEX_FILE` and other repository variables | ✅ Fixed | Whole e2e file run with `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR`, `GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES` and others pointing at a **decoy** repository: the decoy's index hash, status and tree are unchanged, and the real repository's index hash is unchanged before and after. Each variable alone also leaves the suite green except one control test (see Observations 8) |
| Also verified | ✅ | STD-22 patterns present and tested; `.coveragerc` stays trackable (QUA-19); `events.Warning` docstring and `write_private_text` "app-owned state only" docstring present; C22 acknowledgement is on the PR (comment 6515049452) |

## Automated Test Results

| Suite | Command | Total | Passed | Failed | Skipped | Duration |
|-------|---------|-------|--------|--------|---------|----------|
| New acceptance tests (QA) | none added: the developer's tests map to the ACs and survived mutation of the patterns; no production code touched | 0 | 0 | 0 | 0 | n/a |
| Full regression, Windows 3.12 | `pytest -q --cov=gmail_pdf --cov-branch` | 409 | 398 | 0 | 11 | 40.6 s cold, 4.9 to 8.6 s warm |
| Repeat runs | the full suite three more times (`--no-cov`) | 3 × 409 | 3 × 398 | 0 | 3 × 11 | 4.9 to 8.6 s |
| Per-file isolation | each of the 15 test files alone (17+11+12+104+9+27+28+27+31+27+21+32+3+47+2 passed) | 409 | 398 | 0 | 11 | under 3 s each |
| POSIX subset, Linux non-root | `pytest tests/integration tests/unit/test_token_location_warning.py tests/unit/test_gitignore_patterns.py` in `python:3.12-slim`, no network | 91 | 88 | 0 | 3 (Windows-only path tests) | 5.6 s |
| Lint, types, static | `ruff check .`, `ruff format --check .`, `mypy gmail_pdf --strict`, `bandit -r gmail_pdf` | n/a | clean (44 files; 12 source files; bandit no issues) | 0 | n/a | n/a |
| Coverage | as the full regression | 155 statements, 16 branches | 99.42 % (gate 80 %) | n/a | n/a | only `__main__.py` branch `5->exit` partial |
| Changed-code coverage | `diff-cover cov.xml --compare-branch=origin/main --fail-under=80` | 74 lines | 100 % (gate 80 %) | 0 | n/a | n/a |
| CI on the final head | PR #17 check runs, run 41005608058 | 10 jobs | 10 success (`lint`, `types`, `test` × 5 legs, `coverage`, `security`, `package`) | 0 | 0 | n/a |

All 11 Windows skips are the POSIX-mode tests, each with an explicit reason; the 3 Windows-only tests ran here and are skipped on Linux for their stated reason. Pre-existing failures: none.

## Non-Functional Checks

| Check | NFR | Method | Result |
|-------|-----|--------|--------|
| Security: file protection | NFR-013, FR-004 | POSIX modes under four umasks, wider pre-existing state, symlink and planted-temp attacks, read-only targets (Linux, non-root); Windows path rule | ✅ Owner-only from creation (`0600` set at `os.open`, so the token is never readable by others even briefly); atomic replace; fixed error messages |
| Security: secrets in git | NFR-013, SEC-05 | `git check-ignore` in temp repos; force-add detection; gitleaks (CI) | ✅ Patterns and checker work. Variants outside the AC list are not covered (Observation 1) |
| Security: error leakage | NFR-015, FR-005 | Sentinel secret through every failure path | ✅ No content or path in any `PrivateFileError`; `from None` on the encoding failure. The chained `OSError` still carries the path (R-02 of the test plan, expected) |
| Reliability | NFR-007 (partial) | Kill between temp write and replace; concurrency | Old token survives a kill. Four threads writing one target on Windows: 30 of 160 writes failed with `PermissionError` wrapped as `PrivateFileError`; final content valid, no temp left (Observation 4) |
| Performance | none for this story | 20 MB write on Windows (functional check, not timed) | Succeeds; PERF-07 (token write ≈ 42 ms, reviewer's figure) is a STORY-01.04 AC via #20 |
| Platforms | NFR-020 | Windows full, Linux subset, CI legs | Windows and Linux evidence is mine; macOS and Python 3.10, 3.11 are CI-only (green) |
| Accessibility | n/a | n/a | No UI |
| Dependencies | NFR-023 | `pyproject.toml` and requirements untouched (diff) | ✅ No change |
| Test-plan checks | Plan sections 11, 13, 15 | `import_module` / `__import__` in `gmail_pdf/`: only the gated hook in `bootstrap.py` (R-01 stands); `os.replace` only in `infra/paths.py` (token, per C22) | ✅ |

## Exploratory Testing

**Charter (EC-5 and EC-1 of the test plan):** get a secret file into git or leave it readable; break the safe-write helpers. **Time-box:** one 90-minute session. **Areas:** `.gitignore` matching (LF and CRLF, case rules, near-miss names, force-add), `ensure_private_dir`, `write_private_text`, `token_location_warning`, the git e2e isolation, and mutation of the pattern tests.

**Observations (none is an AC failure)**
1. **Variants outside the AC list are not ignored.** `token.json.bak`, `token.json.old`, `credentials.json.bak`, `service-account.json`, `key.pem` and `id_rsa` are not matched, and on a case-sensitive file system (`core.ignorecase=false`, the Linux default) `Token.json`, `Credentials.JSON`, `Secrets/` and `Downloads/` are not either. SEC-05 and the AC name exactly the patterns delivered, and gitleaks in CI is the second control. Suggest the delivery lead decides whether to add `*.json.bak`-style and `*.pem` patterns; not raised as a defect.
2. **A stale temp file survives a kill and holds the new content** (`.token.json.<hex>.tmp`, `0600`, in the `0700` folder, ignored by git). Nothing removes it later. Same protection as the token itself; suggest STORY-01.04 sweeps stale `.token.json.*.tmp` when it writes.
3. **Advisory false positives, fail safe:** `\\?\C:\Users\...`, a UNC admin-share form of the profile and a relative `home` produce `TOKEN_OUTSIDE_PROFILE`. A literal `~` is not expanded (the callers of STORY-01.03 must `expanduser`), and a relative token path is judged against the working directory.
4. **Concurrent writers on Windows** can fail with `PermissionError` (`os.replace` over a file another thread just replaced). Surfaced as `PrivateFileError`, content stays valid. Fine for the single-flow CLI; STORY-01.04 and the GUI must not write the token from two threads.
5. `ensure_private_dir` follows a symlink and tightens the pointee's mode to `0700`. Only tightening, only for the owner.
6. No `fsync` of the parent folder after `os.replace` (architect: optional, losing the rename means signing in again).
7. `_discard` logs "Could not remove temporary file" even when the temp file never existed (invalid or over-long name on Windows, where `unlink(missing_ok=True)` raises). Harmless noise; the log carries the path only.
8. The control test `test_isolation_probe_user_level_ignore_file_is_effective_without_isolation` fails if the ambient environment sets `GIT_CONFIG_PARAMETERS=core.excludesfile=...` (what `git -c` sets for hooks); the isolated tests are unaffected. Git lists seven other local variables the helper does not strip (`GIT_PREFIX`, `GIT_GRAFT_FILE`, `GIT_SHALLOW_FILE`, `GIT_NO_REPLACE_OBJECTS`, `GIT_REPLACE_REF_BASE`, `GIT_IMPLICIT_WORK_TREE`, legacy `GIT_CONFIG`); I set the first and found no effect on isolation or on the decoy repository.

## Defects

| ID | Title | Severity | Status | Linked AC | Jira | GitHub |
|----|-------|----------|--------|-----------|------|--------|
| DEF-003 | `ensure_private_dir` and `write_private_text` raise a raw `ValueError` for a NUL or nameless path | Sev-4 Minor (P3), type Product | New | AC-2, AC-3 (contract; no AC fails) | [PGD-65](https://sankumar76.atlassian.net/browse/PGD-65) | [#25](https://github.com/sankumar76/pdf-download-gmail/issues/25) |
| DEF-004 | `.gitignore` tests do not catch over-broad patterns (`*.json`, `*.pdf`, `*.yml`, `token*`, `*.tmp`) or a `!secrets/` re-include | Sev-4 Minor (P3), type Test | New | AC-1 (negative guard; no AC fails) | [PGD-66](https://sankumar76.atlassian.net/browse/PGD-66) | [#26](https://github.com/sankumar76/pdf-download-gmail/issues/26) |

Open by severity: Sev-1 0, Sev-2 0, Sev-3 0, Sev-4 2 (plus DEF-001 and DEF-002 from PGD-12, still open and routed by master). Each new defect is linked to PGD-14 ("Relates") and cross-linked to its GitHub issue. Suggested homes: DEF-003 in the next story that edits `infra/paths.py` (STORY-01.03 or 01.04); DEF-004 in the next story that edits the `.gitignore` tests.

## Residual Risks / Notes

1. **macOS and Python 3.10 / 3.11 are CI-only.** The macOS leg is green on `6bd795b`; I could not see its skip counts. The POSIX evidence is my Linux container run, which includes the `0700`/`0600` assertions.
2. **8.3 short names** of the profile folder were not testable here (no distinct short name on this volume).
3. **gitleaks was not run locally** (not installed); CI `security` is green on the final head. A full-history run is on the G8 list of the test plan.
4. **Document follow-ups are not QA's:** ADR-003 decision 1, architecture §8.2, §7 and §4.1/§10.2 and the `os.replace` allow-list are amended in #20; `Warning` rename and stable `WarningCode` values in #21 (before STORY-01.03 is Ready).
5. **R-01 to R-11 of the test plan stand;** this story adds Observations 1 to 8 above as input for STORY-01.03 and STORY-01.04.

## Sign-off

QA recommends **ACCEPT** for G7. After master's G7 decision is relayed, qa-engineer moves PGD-14 to Done (GO) or back to In Progress (NO-GO). Merging PR #17 is a human action under `MERGE_POLICY = docs-auto, code-human`; the merge precondition is all 10 CI jobs green on the head that will be merged. This report adds one docs file after `6bd795b`, so that head changes to the report commit and its CI run must be green before merging.
