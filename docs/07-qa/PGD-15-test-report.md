# Test Report — PGD-15 (STORY-02.02): Select the messages for an inclusive date range

| Field | Value |
|-------|-------|
| Tester | qa-engineer |
| Build / commit | `7883f9c` (`7883f9c6cac45892518c685f5f3faeccfbfd632d`) on `feat/PGD-15-date-range-selection` (PR #33; base `main` `2743016`; 41 files, +4183/-54). Merge ref `refs/pull/33/merge` = `e297c7c` (`e297c7c902b3dd647a5cb0796f10349754027b09`), parents `2743016` (current `origin/main`, confirmed with `git ls-remote`) and `7883f9c` |
| Environment | Local: Windows 11, CPython 3.12.10, hash-pinned dev venv, `PYTHONUTF8` unset (cp1252 pipes) unless stated. The branch was tested in the main checkout: `python -m pytest` run there, and a probe test that prints `gmail_pdf.__file__` and `tests.__file__` showed both inside the main checkout (the venv's editable install points at the worktree and was not used; every child probe recorded the `gmail_pdf` it loaded, always the main checkout, or the `gmail_pdf`-only export for NT-05). The merge ref was exported with `git archive` into a new scratch directory and tested there. CI: run 41166243982. Synthetic data and fake sentinels only; the socket guard was on in every child; no network call was made. All temp files (TEMP and TMP) were set to the session scratchpad |
| Date | 2026-10-31 |
| Gate | G7 QA Acceptance. QA tested `7883f9c` only; no code changed during the run (`git rev-parse HEAD` unchanged, `git status` clean apart from the untracked `.claude/agent-memory/`) |
| **Recommendation** | **ACCEPT** (10 of 10 ACs verified; 0 open Sev-1, Sev-2 or Sev-3; 1 new Sev-4, DEF-007, routed to PGD-16; DEF-001, #11 and DEF-005 confirmed fixed) |

## Summary

All ten acceptance criteria pass on `7883f9c` with evidence from my own runs: 1164 passed and 12 skipped in four full runs and in a per-file pass, 99.88 % coverage, ruff, `mypy --strict`, bandit and diff-cover (100 % of 400 changed lines) clean, CI 10 of 10 on the head. The merge ref (current `main` plus this branch) passes 1164 and 12 skips as a work tree (1163 and 13 as a bare export), clean on lint, types and security. Range maths was checked against an independent oracle (every IANA zone, every 2026 offset-change day, plus 24 midnight-DST zones from 2005 to 2030: 5,166 zone-days, 0 mismatches). In real child interpreters, through `python -m gmail_pdf`, the root shim and `gmail-pdf.exe`, AC-6 gave the exact exit code and the exact single stderr line in all 110 rows (119 with the AC-5 rows), including 26 deep-nesting rows up to 1,000,000 levels, with no path, no content, no trace and no file created. The four DEF-005 mutants fail 17, 5, 3 and 3 tests. DEF-001 (#15, including the QUA-39 forms) and #11 are fixed. The one new finding is DEF-007: a start date at or before the Unix epoch (`1970-01-01` in UTC or east of it, and every earlier date) ends in the unexpected-failure line. It is Sev-4, no AC names it, and it fits PGD-16's date rules.

## Check 0 — C35 (test plan)

Confirmed. `docs/07-qa/test-plan.md` v0.2 is at `7945587` on `docs/PGD-1-status-sprint-01` (`git log -1 -- docs/07-qa/test-plan.md`). It holds: NT-01 as exit 1 with the fixed test-only-setting line; NT-02 to NT-05 with their fixed lines and exit 1; NT-03 and NT-04 with master's R1 rows and the binding outcome; NT-09 for real mode (exit 3); NT-01 to NT-05 and NT-09 tied to AC-6 (c.10250, D-61); OQ-1 closed; Annex B row 0.2. One slip in my own document: the header table still says "Version 0.1"; Annex B and the content are 0.2. I will correct it with the next plan update (C32, sprint-02 G4); it is not on this branch and does not affect any row below.

## AC Verification Matrix

"Probe" means a script of mine in the session scratchpad (`qa-g7/probes/`), run against the main checkout. Expected values were derived by me with `calendar.timegm` and fixed UTC offsets, not with `zoneinfo`.

| AC | Test ID(s) | Technique | Result | Evidence |
|----|-----------|-----------|--------|----------|
| AC-1 | `unit/test_daterange.py` (45 pass); probe `p_calc.py` | Literal expected values, boundary-value analysis, independent oracle | Pass | Kolkata 2026-01-01..31: `S` = timegm(2025-12-31 18:30:00Z) = **1767205800**, `E` = timegm(2026-01-31 18:30:00Z) = **1769884200** (= 2026-02-01T00:00+05:30); the code returns the same two numbers and `E - S` = 31 x 86400. Also literal: Kiritimati (UTC+14), Pago_Pago (UTC-11), Kathmandu (+5:45), leap day 2028-02-29, year end 2025-12-31, start == end, Lord_Howe 24.5-hour day (88,200 s), Havana 2026-03-08 (no midnight), Apia 2011-12-30 (skipped day: `S == E`). Oracle (earliest second whose local date is the day): 568 zones, 2,883 zone-days (every 2026 offset-change day +-1), 0 mismatches; second sweep 24 midnight-DST zones 2005-2030, 2,283 days, 0 mismatches. Mutants Q01 (`+86400` per day) and Q03 (ms/s unit) killed |
| AC-2 | `unit/test_planner.py` (40), `e2e/test_select_range.py`; probes `p_calc.py`, `p_cli.py`, `p_explore.py` | Decision table over both fake readings; boundary at 1 s and 1 ms | Pass | Fake with messages at S, S-1 s, E-1 s, E, E-1 ms, S-1 ms. `inclusive` reading: the search returned 6 ids; `exclusive`: 4; the planner selected exactly `first`, `last`, `last-ms` in both. CLI, four-message edge mailbox (00:00:00 Jan 1, 23:59:59 Jan 31, 00:00:00 Feb 1, 23:59:59 Dec 31) in both readings, three entry points: `Messages in range: 2`, 6 of 6 rows. Mutants Q02 (upper bound inclusive) and Q06 (no local re-check) killed |
| AC-3 | `unit/test_daterange.py`, `unit/test_planner.py`; probes `p_calc.py`, `p_explore.py` | Literal DST boundaries; three ranges; CLI at four boundary instants | Pass | `America/New_York`: 2026-03-08 `S` = 05:00Z, `E` = 2026-03-09 04:00Z (82,800 s, 23 h); 2026-11-01 `S` = 04:00Z, `E` = 2026-11-02 05:00Z (90,000 s, 25 h); the range 03-08..11-01 `S` = 03-08 05:00Z, `E` = 11-02 05:00Z. In all three: 23:59:59.999 and 23:59:59 local on the end date in, 00:00:00 the next local day out, first second in, 1 ms before out. CLI at S-1 s, S, S+500 ms, E-1 s, E-1 ms, E for Havana, New_York (both days), Lord_Howe, Kiritimati, Pago_Pago, Kathmandu in both reads: 16 of 16 correct (4 messages in for each real day, 0 for Apia's skipped day; 8 zones x 2 readings). Mutant Q01 killed by `test_new_york_dst_days_are_calendar_days_not_86400_seconds[spring-forward]` |
| AC-4 | `unit/test_query.py` (7), `integration/test_gateway_httpmock.py` (33); probe `p_gateway.py` | Real request building on `HttpMockSequence`, parsed URI | Pass | `q` = `has:attachment filename:pdf after:1767205799 before:1769884201` (no trailing space; a blank user query adds none; a user query follows after one space). Request: `GET https://gmail.googleapis.com/gmail/v1/users/me/messages`, `maxResults=500`, `fields=messages/id,nextPageToken`, `includeSpamTrash=false`, `userId=me` in the path, no other parameter than the library's `alt=json`. `get_message`: `GET .../messages/m1?format=full`. Exactly two requests; the gateway's public methods are `get_message` and `list_message_ids`. Mutants Q04, Q05, Q07, Q08, Q09, Q18 (a write method added) killed |
| AC-5 | `e2e/test_select_range.py::test_a_range_on_the_fake_mailbox_prints_the_interim_count_and_exits_zero`; probe `p_cli.py` | Real children, three entry points, empty cwd listed before and after | Pass | `python -m gmail_pdf`, `python gmail_pdf_downloader.py`, `gmail-pdf.exe`, hook set, `--start 2026-01-01 --end 2026-01-31 --tz Asia/Kolkata`: exit 0, stdout exactly `Messages in range: 2\n`, stderr empty (no `error:`), working directory still empty. Also a range with no match: `Messages in range: 0`. 9 of 9 rows, every child printed the main checkout's `gmail_pdf` |
| AC-6 | `e2e/test_select_range.py`, `unit/test_cli_select_range.py`, `unit/test_bootstrap.py`; probes `p_cli.py`, `p_def001.py` | Equivalence classes of failure, boundary of the depth cap, literal comparison of stderr bytes | Pass | See the NT table below: **110 child rows, 0 failures** (119 with the 9 AC-5 rows). (i) real mode exit **3**, only line `error: Gmail sign-in is not available in this build yet.`; (ii) refused hook exit **1**, only line `error: GMAIL_PDF_TEST_FAKE_MAILBOX is a test-only setting and needs GMAIL_PDF_TESTING=1.`; (iii) unusable file exit **1**, only line `error: The fake mailbox file could not be read; check GMAIL_PDF_TEST_FAKE_MAILBOX.`, and for `tests/` not importable `error: The fake mailbox is only available from a source checkout (tests/ not importable).`. Every row: stdout empty, no `Traceback` or `File "`, neither the file name sentinel nor the content sentinel nor the fixture directory on any stream, nothing created in the cwd. In-process: the log carries the fixed line only, no `exc_info`, no path, and `runner.run` is never called (no fall-through). Exit 3 occurs only in (i) rows and exit 1 only in (ii) and (iii) rows. Mutants Q13, Q14, Q20, Q21 killed |
| AC-7 | `unit/test_retry.py` (57), `unit/test_cancel_token.py`, retry cases in `integration/test_gateway_httpmock.py`; probe `p_gateway.py` | Decision table over statuses; boundary on delays; my own fake clock and cancel | Pass | Retryable (429, 500, 502, 503, 504, 403 `rateLimitExceeded`, 403 `userRateLimitExceeded`, `TimeoutError`, `ConnectionError`, `ssl.SSLError`, `ServerNotFoundError`): each gives exactly 6 attempts, `RetryExhaustedError(attempts=6)` with the last failure as cause, 5 waits through `cancel.wait(delay)`, jitter called with `(0, 1)`, `(0, 2)`, `(0, 4)`, `(0, 8)`, `(0, 16)`; succeeds on attempt 3 after two failures. Non-retryable (403 other, 403 empty reason, 404, 401, 400, 408, 409): raised at once, 1 call, no sleep. `Retry-After` 7 used verbatim, 100 clamped to 64, HTTP date +30 s gives 30, past date 0, garbage and `-5` fall back to jitter; jitter above 64 or below 0 clamped. A pre-set token raises before the first call; a token set during a wait stops with 1 call; a real `CancelToken` set after 0.2 s ended a 30 s `Retry-After` wait in under 2 s. Log: exactly `Retrying list_message_ids: attempt 2 of 6 after 0.0 s`, no URL, query, header or body text, no `exc_info`. Through the real client, a 404 body carrying a sentinel gives `GmailApiError` 404 with `__cause__` and `__context__` both `None`. Mutants Q10, Q11, Q12 killed |
| AC-8 | `integration/test_gateway_httpmock.py`; probe `p_gateway.py` | Run under the socket guard; spy on `build`; stub request | Pass | `build_service(credentials=Credentials(token=<sentinel>))` succeeds with non-loopback sockets blocked: `build("gmail", "v1", ..., cache_discovery=False)`; the bundled `gmail.v1.json` (151,948 bytes, `google-api-python-client` 2.201.0) was used. A stub request records `execute(num_retries=0)` for both calls. `build_service()` with neither credentials nor transport raises `ValueError` (no ambient credentials). The result is recorded in the PR description (AA-03). Mutant Q10 killed |
| AC-9 | PR #33 description; issue #34; SA ruling 6537214922 | Document check | Pass | The record exists in the PR: figures (6,000 units/min per user, 1,200,000 per project, `messages.list` 5, `messages.get` 20 or 60 for `full`), source URL and "last updated 2026-10-16" with the read date, a one-line conclusion ("the margin is NOT far above") and the report to the solution-architect. The PR says the figures came through a summarising tool and need confirming; the SA's ruling confirms them on the raw page. Whether the quota threatens NFR-001/002 is the SA's ruling (#34, PERF-11, PERF-12), not mine |
| AC-10 | `unit/test_daterange.py::test_without_tz_the_system_zone_is_used`, `unit/test_runner.py`; probe `p_calc.py` | Patch `tzlocal.get_localzone_name` | Pass | With the system zone patched to `Asia/Kolkata`: `S` 1767205800, `E` 1769884200 (equals AC-1). Patched to `America/New_York`: `S` = 2026-01-01 05:00Z, `E` = 2026-02-01 05:00Z. Mutant Q17 (default zone forced to UTC) killed |

## Test-plan rows (read row by row)

| Plan item | Result | Evidence |
|-----------|--------|----------|
| 15 PGD-15: BVA with literal epochs (Kolkata, Kiritimati, Pago_Pago, NY DST days, leap day, year edge, start == end), both fake readings | Pass | AC-1 to AC-3 rows |
| 15: exact `q` (no trailing space), `fields`, `maxResults`, `userId`, `includeSpamTrash` on `HttpMockSequence`; recorder shows only allowed methods | Pass | AC-4 row; the two-request recorder; Q18 |
| 15: retry statuses, `Retry-After` seconds and date, delay bounds, 6 attempts, cancel-aware wait | Pass | AC-7 row |
| 15: AC-8 under the guard, no network | Pass | AC-8 row; guard re-probed (203.0.113.7 and example.com blocked, loopback allowed) |
| 15: check AC-9 evidence quality | Pass | AC-9 row |
| 15: verify DEF-001 (#15) fixed | Pass | DEF-001 section |
| 15: NT-01 to NT-04, NT-08 | Pass; NT-08 applies in part | NT table |
| 15: interim `Messages in range: N` and the exit-3 line tracked for removal (R-09) | Tracked | Both are the only places that print them (`messages.py`, `console.py`); STORY-07.04 and STORY-01.04/01.06 carry the replacement ACs (A-5). Re-check when those stories reach G7 |
| 15: probe `--sta` abbreviation (R-10) | Observed | `--sta 2026-01-01 --en 2026-01-31` is accepted and exits 0. FR-045's unknown-flag rule is therefore bypassed for prefixes. Not a PGD-15 defect (OQ-3 owns the decision, due at PGD-16); repeated `--start` takes the last value; `--start=...` works |
| 3 Secret leak, all text surfaces | Pass | Sentinel matrix 65 passed (28 rows added for PGD-15 surfaces); 12 NT-06/07/08 child rows with a sentinel, a token and a registered secret: 0 leaks; Q15 (console without `redact`) killed |
| 3 Range edges | Pass | AC-1 to AC-3 |
| 3 Interrupt and exit codes | Pass | Real console Ctrl+C below |
| 3 Test-infrastructure trust (guard, fake, hook) | Pass | Re-probed (see 5 and EC-1 below) |
| 3 Supply chain | Pass | `pyproject.toml` gained only a mypy override; `test_dependency_allowlist.py` 12 passed; `pip-audit` not run (no dependency manifest changed) |
| 3 Console encoding, charter EC-9 | Pass, no issue found | Exploratory section |
| 3 CI required on `main` (#7, RISK-022) | Pass | #7 is closed; all 10 check runs `success` on the head; PR `mergeable_state` clean; tested `main` SHA `2743016` (RISK-023) |
| 5 Entry criteria | Pass | `gate:g6-pass` label, Jira In QA, Dev Record in the PR, CI green |
| 5 Exit criteria | Pass | Every AC has a verdict from my own runs; no Sev-1/2/3 open; regression repeated; exploratory recorded |
| 5 Re-test rule (changes to `tests/fakes/`, `bootstrap.py`, `tests/conftest.py`) | Pass | Hook probes (NT table) and guard probes re-run; the guard module itself is unchanged |
| 7 Four full runs + each file alone + ruff, mypy, bandit, diff-cover | Pass | Automated results |
| 7 CI legs 3.10, 3.11, Ubuntu, macOS | Pass (CI) | Not run locally; `test (win-310)`, `win-311`, `win-312`, `ubuntu-312`, `macos-312` all `success` |
| 7 Mutation spot checks for enforcement-style tests | Pass | 24 mutants below: 23 killed, 1 equivalent; plus the four DEF-005 mutants |
| 7 Flaky tests, determinism | Pass | 0 failures in the four full branch runs, the per-file pass and the three merge-ref runs (the only red run was the environment issue below, before the short temp path); no real sleeping outside the fake-latency tests |
| 9 Exit-code mapping: item 1 (table for every `RunResult`, no code outside 0..3) | Pass | `test_runner.py::test_the_exit_codes_are_the_closed_set_zero_to_three` (Q23, a code 130, kills it); COMPLETED to 0 in `test_runner.py`, CANCELLED to 1 through `main` (Q24 kills a cancelled run exiting 0). No code 4, 5 or 130 exists in `gmail_pdf/` |
| 9 item 2 (exit 1 shared by four outcomes: distinct first line asserted exactly) | Pass | `Run cancelled`, `error: unexpected failure, see the run log` and the three hook lines are all asserted as exact lines |
| 9 item 3 (Windows Ctrl+C trap) | Pass | Below |
| 9 item 4 (no success look-alikes) | Pass | A cancelled run exits 1; `--help`, no arguments and an empty range exit 0 |
| 9 item 5 (streams) | Pass | stdout and stderr asserted separately in every row |
| 9 table row "Bad arguments or validation error: exit 2" | Pass | Date format, lone `--start`/`--end`, reversed range, unknown zone on the hook exit 2 with a fixed sentence that never echoes the input |
| 11 NT-01 to NT-05, NT-09 as probes with a distinctive file name | Pass | NT table |
| 11 Assertions on both streams; dev-mode flags unset in the child | Pass | `PYTHONDEVMODE`, `PYTHONFAULTHANDLER`, `PYTHONWARNINGS`, `PYTHONSTARTUP` removed from every child environment |
| 11 NT-06, NT-07 | Pass | NT table |
| 11 NT-08 (persistent 503 on the list call) | Pass in part | Through the real gateway on `HttpMockSequence`: exit 1, not reported as empty, stdout empty, last line the unexpected-failure line, 0 leaks. The full "one `error:` line" is PGD-17's AC-4 and cannot hold yet: see "Retry lines on stderr" in the exploratory section |
| 13 R-01 dynamic imports | Pass | `importlib.import_module` only in `bootstrap.py:48` (the gated hook); Q19 (a Google import in the planner) killed by `test_import_boundaries.py` |
| 13 R-02 chain holds the fixture path | Pass | No chained text printed or logged (AC-6 rows, Q21) |
| 13 R-05 console encoding | Pass for this story | Exploratory section |
| 13 R-06 fake fidelity gaps (#11, DEF-001) | Pass | DEF-001 and #11 sections |
| 14 DEF-001: re-run the three reproductions and NT-04 | Pass | DEF-001 section |
| 16 EC-1 (test-support seams), EC-3 (date and zone logic), EC-8 (retry), EC-9 (Windows console) | Done | Exploratory section |
| 17 OQ-1 closed | Confirmed | Check 0 |
| 17 OQ-3 `allow_abbrev` | Open, observed | `--sta` accepted (above); PGD-16 |
| 17 OQ-5 console encoding policy | Open, no new evidence of harm | Exploratory section |
| Annex A NFR-006 (retry), NFR-011 (read-only), NFR-012 (secrets), NFR-014 (no egress), NFR-022 (gates), NFR-024 (formats) | Pass | AC-7; Q18 and the two-request recorder; matrix; guard in every child; static checks; strict date table (26 date forms, `2026-1-1`, `20260101`, `2026-01-01\n`, full-width digits, ... all exit 2) |
| Annex A NFR-003 (overhead, informational) | Pass | Planner overhead excluding the fake's `get_message`: 19 us per message at 1,000 messages (target 50 ms); whole run 79 ms |

## Automated Test Results

| Suite | Command | Total | Passed | Failed | Skipped | Duration |
|-------|---------|-------|--------|--------|---------|----------|
| New acceptance tests (QA) | none added: the head is frozen and the brief forbids writing to `tests/` or `gmail_pdf/`. My probes are scratch scripts outside the repository | 0 | 0 | 0 | 0 | n/a |
| Full regression, branch head, run 1 | `pytest -q --cov=gmail_pdf` (branch coverage on through `pyproject.toml`) | 1176 | 1164 | 0 | 12 | 63.0 s |
| Repeat runs (flakiness) | `pytest -q --no-cov` x3 | 3 x 1176 | 3 x 1164 | 0 | 12 | 54.3 to 56.3 s |
| Per-file isolation | each of the 35 test files alone | 1176 | 1164 | 0 | 12 (1 in `test_select_range.py`, 11 POSIX-mode in `test_private_files.py`) | 0.1 to 27.7 s per file |
| Full regression, merge ref `e297c7c` (export, no `.git`) | `pytest -q --cov=gmail_pdf --cov-branch` in the new export | 1176 | 1163 | 0 | 13 | 61.1 s, coverage 99.88 % |
| Merge ref, export turned into a git work tree | `git init` and one commit in the scratch export, then `pytest -q --no-cov` | 1176 | 1164 | 0 | 12 | 52.4 s |
| Lint | `ruff check .` and `ruff format --check .` | 80 files | clean | 0 | n/a | branch and merge ref |
| Types | `mypy gmail_pdf --strict` | 24 files | clean | 0 | n/a | branch and merge ref |
| Security static | `bandit -q -r gmail_pdf` | n/a | no issues (exit 0) | 0 | n/a | branch and merge ref |
| Coverage | `--cov=gmail_pdf --cov-branch` | 734 statements, 114 branches | 99.88 % (gate 80 %) | n/a | n/a | one partial branch |
| Changed-code coverage | `diff-cover cov-branch.xml --compare-branch=origin/main --fail-under=80` | 400 lines | 400 covered (100 %) | 0 | n/a | n/a |
| CI on the head | `pull_request_read get_check_runs`, run 41166243982 | 10 jobs | 10 `success` (`lint`, `types`, `test` win-310, win-311, win-312, ubuntu-312, macos-312, `coverage`, `security`, `package`) | 0 | 0 | n/a |

**Merge ref.** `git fetch origin refs/pull/33/merge` gives `e297c7c902b3dd647a5cb0796f10349754027b09`, authored by the PR author and committed by GitHub, with parents `274301667504a7ec03a6b57c7facc6399c9b428e` (current `origin/main`) and `7883f9c6cac45892518c685f5f3faeccfbfd632d` (read with `git cat-file -p`). `main` has not moved, so the merge adds nothing to the head.

**Environment issue, not a defect.** My first full run had 3 failures, all in `tests/e2e/test_gitignore_matching.py` (`Filename too long` from git, exit 128): the session scratchpad path is 148 characters, and the pytest `tmp_path` plus a repository's `.git/hooks/*.sample` passes Windows' 260-character limit. With `--basetemp` set to a short directory in the same scratchpad the file passes (47 of 47) and so does everything else; all figures above use that. A shorter temp path in CI (the legs ran green) or a developer machine has no such problem.

**Skips (all platform reasons with reason strings, 12 on the branch):** 11 POSIX-mode tests in `integration/test_private_files.py` ("POSIX mode bits are not meaningful on Windows") and 1 in `e2e/test_select_range.py:222` ("needs POSIX permission bits and a non-root user"): the AC-6 unreadable-file row built with `chmod`. On Windows I covered that row myself by holding the fixture open with no sharing (`PermissionError`): NT-02 passes in all three entry points. The extra skip on a bare export (13) is the `.git` test, as the reviewers noted; it ran and passed once the export was a work tree. The Ubuntu and macOS legs run the POSIX rows; I read their job status, not their per-test output.

## DEF-005 mutants (C30)

One edit per fresh `git archive` export of `7883f9c` in its own scratch directory; the module loaded inside each copy was confirmed with `LOADED <path inside the copy> MIN_SECRET_LENGTH=... THIRD_PARTY_LOGGERS=...` before pytest ran; each copy had a diff against the head of exactly the one line.

| Mutant of `gmail_pdf/redaction.py` | Result | Failing tests |
|---|---|---|
| M13 `THIRD_PARTY_LOGGERS = ()` | **17 failed**, 1146 passed, 13 skipped | 12 in `test_redaction_logging.py`, 5 in `test_redaction_pins.py` |
| M22 `"oauthlib"` removed | **5 failed**, 1158 passed, 13 skipped | `test_third_party_loggers_are_capped_at_warning[oauthlib]`, `test_a_capped_logger_drops_debug_records[oauthlib]`, `..._info_records[oauthlib]`, `test_exactly_four_third_party_loggers_are_capped`, `test_every_pinned_logger_is_capped_at_warning_by_the_installer[oauthlib]` |
| M20 `MIN_SECRET_LENGTH = 4` | **3 failed**, 1160 passed, 13 skipped | `test_values_that_are_too_short_or_blank_are_ignored[seven-characters]`, `test_the_minimum_secret_length_is_eight`, `test_a_seven_character_value_is_not_registered_and_an_eight_character_value_is` |
| M23 `MIN_SECRET_LENGTH = 12` | **3 failed**, 1160 passed, 13 skipped | `test_a_value_of_exactly_the_minimum_length_is_registered`, `test_the_minimum_secret_length_is_eight`, the same seven/eight test |

17, 5, 3 and 3 match the reviewer's figures. The 13th skip in each copy is the `.git` test. Before the fix the same four mutants left every test green (PGD-13 report).

## Confirmations required by master

- **#15 / DEF-001 / PGD-63: fixed, Verified.** The three original reproductions on `7883f9c`: (1) a file containing `"[" * 200000` gives `FakeMailboxUnavailableError` (an `AdapterUnavailableError`) from `build_deps`, message without the path; through the CLI, 100,000 and 1,000,000 levels of `[`, closed arrays and an object chain all exit 1 with the fixed line; (2) page tokens `cursor-0:²`, Arabic-Indic and full-width digits, `-1`, empty, unknown cursor, `garbage` all raise `FakeGmailHttpError` 400 `invalidPageToken`, and `after:²`, `before:٢`, `after:` full-width, `after:-5`, `after:` give `UnsupportedQueryError`, never a raw `ValueError`; (3) `{"format":1,"messages":[{"resource":{"id":"a"},"attachments":{}}]}` and the two one-field variants fail at load with `ValueError`, and through the CLI give exit 1 and the fixed line. **The QUA-39 forms** (NT-03 and NT-04 rows): `payload.parts` `[5]`, `[null]`, `["x"]` with no root filename, `parts` not a list, `labelIds` `5`, `null`, `[[]]`, `internalDate` of 5,000 digits, as a number, superscript digits, missing, `payload` missing, `latency_s` `"inf"`, `1e300`, `NaN`, `-1`, `headers` not a list, and 14 more shapes (33 shapes, 43 rows with the other entry points): every one but a harmless one exits 1 with exactly the fixed line (the one exception is an invalid-base64 attachment value, which loads and succeeds), 0 unexpected-failure lines. Depth: `parts` at 1 and 50 succeed, at 99, 100, 101, 247, 1000, 1400 give the fixed line (the cap counts containers, two per `parts` level); a resource value at 1 succeeds, at 198, 199, 200, 201, 500, 2900 the fixed line; a value under an unread top-level key succeeds at 198 and 199 levels and fails at 200, 201 and 2900, so both sides of the cap that the developer pins behave as stated. **PGD-63 and #15 can close, on the merge of PR #33**: the fix is not on `main` until then, so closing them earlier would misstate the repository. QA sets DEF-001 to Verified now.
- **#11: fixed, Verified.** A baseline token sent with the sweep query, and with the spam flag flipped, gives 400 `invalidPageToken`; the right token with its own query still pages; both searches page independently. Closes with the merge.
- **#31 / DEF-005 / PGD-67: fixed, Verified.** The four mutants fail as above. Closes with the merge.

## Non-Functional Checks

| Check | NFR | Method | Result |
|-------|-----|--------|--------|
| Secret exposure on every surface | NFR-012, FR-005 | Sentinel matrix (65 tests, normal capture) and 12 child runs (6 modes at `PYTHONUTF8` unset and 1) with a sentinel, an `ya29.` token shape and a registered secret raised in the runner, in a chained cause, in a worker thread, as `KeyboardInterrupt`, and in a 503/404 body through the real gateway; plus the 12 PGD-13 child rows | Pass: 0 leaks. Known: argparse usage errors echo the offending argument (#23) |
| No stack trace, no path | D-21, test plan section 11 | NT table; both streams | Pass |
| No egress | NFR-014 | Guard in every child; guard re-probed (RFC 5737 address, DNS name, `getaddrinfo` blocked; loopback allowed) | Pass |
| Read-only | NFR-011 | Two-request recorder; Q18 | Pass |
| Scope and secrets in the diff | NFR-015, CLAUDE.md section 8 | Added-line scan for token shapes and addresses; `git diff` on `CLAUDE.md`, `.claude`, `.github/pull_request_template.md`, `.gitignore` | Pass: no token shape, no address; protected files untouched; only `pyproject.toml` (mypy override) among the config files. gitleaks is not installed here; the CI `security` job is green |
| Secret files (PGD-14 regression) | NFR-013 | `git ls-files -i -c --exclude-standard` (empty); `git check-ignore` on 10 names; 47 `.gitignore` e2e and 27 pattern tests | Pass. `my-credentials.json.bak` is not ignored by `*credentials*.json`: not new, not in this story (DEF-004's class) |
| Performance | NFR-003 | 1,000-message planner, zero latency | 19 us per message overhead, 79 ms total. CLI `--help` median 0.53 s, a 500-message run 0.69 s (including the guard's start-up). NFR-001/002 on the real service: the SA's ruling on #34 |
| Accessibility | NFR-017..019 | n/a: no UI in this story | n/a |
| Exit-code mapping | D-21 | Plan section 9 rows above | Pass |

### No-traceback checks (test plan section 11)

Each row: child interpreter, socket guard on, stdout empty, stderr exactly the one line, no sentinel or path, nothing created in the working directory.

| ID | Rows run | Result on `7883f9c` |
|----|----------|---------------------|
| NT-09 real mode | 6 (neither variable; `GMAIL_PDF_TESTING=1` alone; x3 entry points) | Pass: exit 3, `error: Gmail sign-in is not available in this build yet.`, never exit 1 |
| NT-01 refused hook | 24 (`GMAIL_PDF_TESTING` unset, `0`, empty, `true`, ` 1`, `1 `, `2`, `yes`; x3 entry points) | Pass: exit 1, the test-only-setting line, never exit 3 |
| NT-02 missing, a directory, unreadable (file held open with no sharing, `PermissionError`) | 9 | Pass: exit 1, the "could not be read" line |
| NT-03 content shapes (33 on `-m`, 5 on each of the other two) | 43 | Pass: 42 give exit 1 and that line; 1 (`attachments` value that is invalid base64) loads and succeeds, which the binding outcome allows |
| NT-04 deep nesting: `parts` x8 depths, resource x7, unread key x5, extreme 100,000 and 1,000,000 levels x3 shapes | 26 | Pass: success or the fixed line, 0 unexpected-failure lines, 0 raw `RecursionError` |
| NT-05 `tests/` not importable (a `gmail_pdf`-only export of `7883f9c`, no `tests` on the path, `-m` and the shim) | 2 | Pass: exit 1, `error: The fake mailbox is only available from a source checkout (tests/ not importable).` |
| AC-5 success rows | 9 | Pass |
| NT-06 sentinel exception in the runner, with a chained cause, and in a worker thread | 6 (x2 encodings) | Pass: `error: unexpected failure, see the run log`; exit 1 (runner, chain); a worker failure with a completed run prints the line and exits 0 (known R-12) |
| NT-07 `KeyboardInterrupt(sentinel)` in the runner | 2 | Pass: `Run cancelled`, exit 1 |
| NT-08 persistent 503 | 2 (+2 for a 404 body) | See the table above and the exploratory note |

### PGD-13 and PGD-14 regressions

The earlier QA child-process script (`scratchpad/probes/child_probes.py`, written for the PGD-13 G7) was re-run unchanged against the main checkout: an exception carrying a sentinel out of the parser gives exactly `error: unexpected failure, see the run log`, exit 1; a raised `KeyboardInterrupt`, a real `SIGINT` and an actual console `CTRL_C_EVENT` each give exactly `Run cancelled`, exit 1, in all three entry points (12 of 12 PASS), 0 sentinels, no trace; the hook-order probe reports all three hooks owned by `gmail_pdf.redaction` when the parser is built. The known limits are unchanged (`--bogus=<sentinel>` echoed by argparse, #23; an interrupt inside the failure report ends with `0xC000013A`, #29). New for this story, a real console Ctrl+C delivered 2 s into a run whose fake Gmail call sleeps 30 s: exit 1, stderr exactly `Run cancelled`, stdout empty, the run ended after 2.7 s (both `PYTHONUTF8` settings). Secret files: see the table above.

### Mutation spot checks (24 mutants, one edit each, fresh export of `7883f9c`, `pytest -x`)

| ID | Mutant | Result | First failing test |
|----|--------|--------|--------------------|
| Q01 | end = start + 86400 x days | Killed | `test_new_york_dst_days_are_calendar_days_not_86400_seconds[spring-forward]` |
| Q02 | `contains` upper bound inclusive | Killed | e2e `..._prints_the_interim_count_and_exits_zero` |
| Q03 | `_MS_PER_SECOND = 1` | Killed | same e2e |
| Q04 | widening removed | Killed | `test_the_baseline_search_sends_exactly_the_specified_request` |
| Q05 | trailing space | Killed | same |
| Q06 | no local re-check | Killed | e2e |
| Q07 | `includeSpamTrash` default true | Killed | same gateway test |
| Q08 | `maxResults` 100 | Killed | same |
| Q09 | `fields` changed | Killed | same |
| Q10 | `num_retries=3` | Killed | `test_requests_are_executed_with_num_retries_zero` |
| Q11 | 5 attempts | Killed | `test_a_retry_is_logged_under_the_name_of_the_gateway_method[list]` |
| Q12 | delay clamp removed | Killed | `test_retry_after_is_clamped_to_zero_to_sixty_four_seconds[over-the-cap]` |
| Q13 | refused hook exits 3 | Killed | `test_a_refused_hook_exits_one_with_the_fixed_line` |
| Q14 | real mode exits 1 | Killed | `test_real_mode_exits_three_with_the_interim_sign_in_line` |
| Q15 | console prints without `redact` | Killed | `test_every_line_passes_through_the_redaction_path[error]` |
| Q16 | `\d` instead of `[0-9]` in the date pattern | **Equivalent** | `date.fromisoformat` rejects non-ASCII digits on 3.12, so the stricter regex is belt and braces; behaviour unchanged (full-width digits give exit 2 in the real code too) |
| Q17 | default zone forced to UTC | Killed | `test_without_tz_the_system_zone_is_used[kolkata]` |
| Q18 | write method added to the gateway | Killed | `test_the_gateway_has_exactly_the_two_read_methods_of_this_story` |
| Q19 | planner imports `googleapiclient` | Killed | `test_the_real_package_obeys_the_layering_rules` |
| Q20 | unreadable file falls through to the sign-in line and exit 3 | Killed | `test_an_unusable_fake_mailbox_file_exits_one_and_never_falls_through_to_real_mode[missing]` |
| Q21 | hook-failure log carries `exc_info` | Killed | `test_a_hook_failure_logs_only_the_fixed_line_without_exception_details` |
| Q22 | reversed range allowed | Killed | `test_a_bad_zone_or_range_order_exits_two[end-before-start]` |
| Q23 | `ExitCode` gains 130 | Killed | `test_the_exit_codes_are_the_closed_set_zero_to_three` |
| Q24 | cancelled run exits 0 | Killed | `test_a_cancelled_run_prints_the_notice_and_exits_one` |

## Exploratory Testing

**Charters:** EC-3 (date and zone logic), EC-8 (retry), EC-9 (Windows console and encoding, `PYTHONUTF8` unset), EC-1 (the test-support seams, because `tests/fakes/`, `bootstrap.py` and `tests/conftest.py` changed). **Time-box:** one session. **Areas:** every entry point as a user runs it; zone forms; date forms and extremes; DST-gap and odd-day zones through the CLI; non-ASCII text in the mailbox, in the mailbox path, in the working directory and in the arguments; a working directory with spaces; option forms; first-page limit; hook variable edge values; a real console Ctrl+C during a run.

- **Console encoding (OQ-5, R-05): no failure on this story's output.** With cp1252 pipes, a mailbox whose subjects, file names, senders and labels contain Japanese, Greek, an accented name and emoji ran with `Messages in range: 4`, exit 0, empty stderr (the planner keeps ids and dates only, so no mailbox text is ever printed). A fixture path and a working directory containing `Ünï 日本 ✓` and spaces also ran, and a missing such path gives the fixed line without the path. Rejections never echo the input: `--tz Ásia/日本✓`, `--start ２０２６-０１-０１` and `--start 😀` give fixed ASCII sentences, exit 2, in both encodings. The one place user text is echoed is argparse's own error (#23): an unknown option `--日本✓` is printed as `--日本✓` on a cp1252 stderr (backslash replace) and as itself on UTF-8; no crash. So OQ-5 still needs its decision before the first story that prints file names, but nothing in PGD-15 triggers it. (My own probe died once printing a `²` to a cp1252 stdout, the failure R-05 describes, which I had to work around.)
- **Unusual `--tz` forms (50 tried), nothing reached the unexpected-failure line.** Accepted as zones: `UTC`, `utc`, `Etc/UTC`, `GMT`, `EST`, `EST5EDT`, `MST7MDT`, `Factory`, `Asia/Calcutta`, `Etc/GMT-14`, `Etc/GMT+12`, `Europe/Kiev`, `Europe/Kyiv`, and, because Windows normalises file names inside the `tzdata` lookup, `Asia/Kolkata ` (trailing space) and `Asia\Kolkata`. Rejected with the zone sentence, exit 2: `Z`, `asia/kolkata`, `ASIA/KOLKATA`, ` Asia/Kolkata`, `Asia//Kolkata`, `./`, `../` and absolute and UNC forms, `Asia/../UTC`, `UTC+5:30`, `+05:30`, `Etc/GMT+14`, `posixrules`, `localtime`, `zone.tab`, `tzdata.zi`, `iso3166.tab`, `Asia`, `America`, `Asia/`, empty, `Mars/Olympus`, a 5,000-character name, a DEL character. No path traversal or file read outside the `tzdata` package. The mix (lower-case `utc` accepted, `asia/kolkata` refused, a trailing space accepted) is inconsistent; harmless here, and a rule for PGD-16 to state (trim? case?). Not logged as a defect.
- **Dates (26 forms plus extremes).** Every malformed form gives exit 2 and the fixed sentence (`2026-1-1`, `20260101`, `2026-01-01T00:00`, a trailing newline, leading or trailing space, `+2026-01-01`, `0000-01-01`, `2027-02-29`, month 13, `2026-W01-1`, `2026/01/01`, empty). `9999-12-31` gives exit 2 "outside the range this program can handle", `9999-12-30` works. **`1970-01-01` (UTC, Kolkata) and every earlier date give exit 1 and the unexpected-failure line: DEF-007.** 1970-01-01 in New_York, Kiritimati and Pago_Pago (S above 0) works.
- **DST gaps and odd days through the CLI (EC-3).** Havana 2026-03-08 (no midnight), New_York both DST days, Lord_Howe 2026-04-05 (24.5 h), Kiritimati, Pago_Pago, Kathmandu: messages at S-1 s, S, S+500 ms, E-1 s, E-1 ms, E selected exactly (4 of 4), in both fake readings. Apia 2011-12-30 (`S == E`, the day does not exist) selects 0, and the query `after:X-1 before:X+1` returns the message at `X`, which the local check drops.
- **First page only (known limit).** A fake mailbox with 1,203 matching messages and page size 500 prints `Messages in range: 500`; 50 messages at page size 20 print `20`. The count is silently truncated; documented in the planner (STORY-02.04 follows `nextPageToken`) and not a defect. It matters for the interim line: do not read `N` as complete until STORY-02.04.
- **Hook values.** `GMAIL_PDF_TEST_FAKE_MAILBOX=""` with `GMAIL_PDF_TESTING=1` is treated as unset, so real mode: exit 3 (the code tests truthiness). A whitespace or relative path gives the fixed unreadable line. Fine for a test-only hook; noted.
- **Retry lines on stderr (for PGD-17 and STORY-07.02).** With the real gateway behind `main` (injected in a child), a persistent 503 prints five `Retrying list_message_ids: attempt N of 6 after X s` lines on stderr before the unexpected-failure line, because the retry logger's WARNING reaches `logging.lastResort` while no handler exists (the redaction filter is on it, so nothing leaks). PGD-17's AC-4 and plan row NT-08 ask for one `error:` line; they will need either the run-log handler (STORY-07.02) first or a decision that retry notices are allowed. Unreachable today: `build_deps` never constructs the gateway.
- **Option forms.** `--sta/--en` abbreviations accepted (R-10); `--start=...` works; repeated `--start` takes the last; `--start --end` gives argparse's "expected one argument" (exit 2, usage); positional junk exits 2; `--tz` alone prints the usage and exits 0 (dev decision 3).
- **Directory with spaces.** The repository path itself has a space (`ProCaliber Tech`) and every probe ran from it or from a scratch directory with spaces and Unicode: no difference.
- **Files created.** After every AC-5 and AC-6 row the working directory was empty (listed before and after, recursively); the fixture directory was not modified; the repository stayed clean.

## Defects

| ID | Title | Severity | Status | Linked AC | Jira | GitHub |
|----|-------|----------|--------|-----------|------|--------|
| DEF-007 | A start date at or before 1970-01-01 (UTC, or any date before 1970) ends in the unexpected-failure line instead of a rejection | Sev-4 Minor (P3), type Product | New | none fails; input validation is PGD-16 (AC-1) | [PGD-69](https://sankumar76.atlassian.net/browse/PGD-69) | [#39](https://github.com/sankumar76/pdf-download-gmail/issues/39) |

Open by severity for this story: Sev-1 0, Sev-2 0, Sev-3 0, **Sev-4 1** (DEF-007, linked to PGD-15 and cross-linked to #39). DEF-001 and DEF-005 are Verified (see above; they close with the merge). DEF-002 to DEF-004 and DEF-006 (other stories) are unchanged and not re-logged. No environment or test-code defects found; the long-path failure above is an environment condition of my scratch path. Rating note: DEF-007 is Sev-4 because no mailbox can hold a message before 2004, the selection stays exact because of the local re-check, and only the wording of an error is wrong; the developer documented "dates before 1970 are not rejected here" (decision 9) but the consequence (the D-21 internal-failure line for a harmless date) and the extra case `1970-01-01` were not stated.

## Known Limits (recorded, not defects)

1. **Python 3.10 and 3.11** run no document near the depth cap through `get_message`; that read rests on arithmetic there (#38, master's note). Not re-opened. A legal `latency_s` of 3600 sleeps for an hour: legal, not logged.
2. **Quota and throughput** (PERF-11, PERF-12, #34, #35): the SA's rulings stand; nothing measured on real Gmail.
3. **First page only**, **interim count line** and **interim sign-in line** (R-09): STORY-02.04, STORY-07.04, STORY-01.04/01.06.
4. **Not covered by the AC-6 outcome (from the fake's docstring):** `MemoryError` on a huge file, and reads that later stories add. "Any file content" cannot be proved by tests; my evidence is the 110 AC-6 child rows above (including 43 content-shape and 26 depth rows) and the reviewers' volumes.
5. Closed-pipe exit 120 (DEF-006, #32), argparse echo (#23), worker-thread exit 0 (R-12), `0xC000013A` on an interrupt inside the failure report (#29) are unchanged.

## Issues for other roles

- **product-owner / PGD-16:** DEF-007 (add a lower bound or a rule for ranges that start at or before the epoch); decide `--tz` trimming and case (observed above); `--sta` abbreviations (OQ-3).
- **PGD-17 / STORY-07.02 (developer, scrum-master):** retry WARNING lines will reach stderr before the run-log handler exists; plan row NT-08 says "one `error:` line".
- **qa-engineer (me):** test plan header version slip (above).
- **scrum-master:** nothing new; C38 stands.

## Residual Risks / Notes

1. Real Gmail epoch-bound semantics (AA-01) and the quota behaviour remain W3 items; the fake's two readings and the +-1 s widening are the mitigation.
2. Not run here: Python 3.10 and 3.11 locally, Ubuntu and macOS (CI job status only), a built wheel (the NT-05 export is a `gmail_pdf`-only copy of the head, not a wheel), `pip-audit`, gitleaks, Python 3.14.
3. Scratch artefacts (probes, exports, mutant copies, outputs) are in the session scratchpad only; the only file added to the repository is this report. I did not delete anything: one compound command containing an `rm` of my own old output files was denied by the permission system and I did not repeat it another way (the old files stay in the scratchpad). A temporary `subst` drive letter mapped to the scratch temp directory was removed at the end.

## Sign-off

QA recommends **ACCEPT** for G7. PGD-15 stays In QA until master's G7 decision is relayed; then qa-engineer moves it to Done (GO) or back to In Progress (NO-GO). Merging PR #33 is a human action under `MERGE_POLICY = docs-auto, code-human`; before the merge request, CI 10/10 on the head and the tested `main` SHA (`2743016`, current at 2026-10-31) are on record here, and the request should name PERF-11, PERF-12, #35, #38, DEF-007, and that PGD-63/#15, #11 and PGD-67/#31 close with the merge.
