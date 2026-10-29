# UX Specification — Gmail PDF Attachment Downloader (R1 CLI interaction, R2 Desktop GUI, R3 outline)

| Field | Value |
|-------|-------|
| Version | 0.2 (aligned to PRD v0.3: PD-11..16) |
| Owner | ux-expert |
| Status | In Review (G3) |
| Inputs | PRD v0.3 (FR-001..066, NFR-017..021, PD-01..09), project brief v0.1 (P-01, P-02), requirements catalogue GUI-01..19, decision log D-01..D-13, CLAUDE.md §9, RD §2.1 and §3 |
| Jira | [PGD-1](https://sankumar76.atlassian.net/browse/PGD-1) |
| Supporting files | [wireframes/main-window.md](wireframes/main-window.md) (W-01..W-06), [wireframes/dialogs.md](wireframes/dialogs.md) (DLG-01..08, SCR-07) |

**Conventions.** Sizes are logical px (1 logical px = 1 device px at 100 % OS scaling). `UA-nn` = UX assumption, `UQ-nn` = UX open question (section 11). Terms follow the PRD: *run*, *dry run*, *output folder*, *time zone*, *run log*, *CSV report*; user-facing text says **download history** for the PRD's *manifest* (the file `.manifest.json`; first use in a dialog names both). Statuses are the LOG-03 values. No framework is assumed (ADR pending, RISK-012); section 11 lists what the framework must support.

## 0. Answers and decisions in this spec

| Item | Answer |
|------|--------|
| **PQ-03 minimum window size (closed by PD-12)** | **800 × 560 logical px.** Where the work area is smaller than that (1920 × 1080 at 200 % scaling: desktop 960 × 540, work area about 960 × 520 after the taskbar), the window is **clamped to the work area and content scrolls**; nothing is clipped (NFR-021). The clamp rule, not the number, protects that display. Below 640 px of height each column scrolls. Default size on first launch: 1100 × 720, clamped to 90 % of the work area, centred. (UA-01: SA confirms the framework can clamp or scroll below its own minimum) |
| **PQ-03 default folders when launched by double-click** | The GUI never uses the working directory (it is unpredictable on double-click). Defaults: credentials and token in a per-user private app-data folder under the user profile (SEC-04), e.g. `%LOCALAPPDATA%\GmailPdfDownloader\secrets\` on Windows; output folder `<user Downloads>\Gmail PDFs`. Reason: inside the profile, private by default, and not in a cloud-synced Documents folder (RISK-009). `GMAIL_CREDENTIALS_PATH` and `GMAIL_TOKEN_PATH` still override (FR-002). The CLI keeps `./secrets/` and `./downloads` (RD §3). SCR-03 always shows the exact expected path. (UA-02, SA confirms base folders and permissions in the ADR) |
| **PQ-01 dry run and bytes** | Spec works for both outcomes. Working assumption (PRD): metadata only, so SCR-04 shows the notice "PDFs are not opened in a dry run" and cannot show `Not a PDF`. If the SA decides to fetch bytes, delete that notice and add the `Not a PDF` result (UA-03) |
| **PQ-02 outcomes (PD-13)** | Cancelled run, unreadable download history and unexpected internal failure are neither success nor an attachment error. Each exits non-zero (not 2 or 3; PM position 1, the numeric mapping is the SA's) and each has its own first line, **identical in GUI and CLI** (table in section 12). No stack trace, no secret |
| **Dark theme (PD-14)** | Won't in R2. One light palette: halves the contrast and screenshot matrix (NFR-018, NFR-021). Tokens are semantic, so a dark set can be added later without touching screens |
| **Re-fetching a deleted file (PD-11)** | The only advice anywhere in the UI, CLI and README pointer is "choose a new output folder". Deleting or moving `.manifest.json` is never advised: it makes every PDF in the folder download again with `_1`, `_2` endings (until FR-034, R3) |
| **Account address** | Not shown. Reading it needs `users.getProfile`, outside the allowed methods (NFR-011). Header shows only `Signed in` / `Not signed in` |

## 1. Design Principles

1. **Safe by default.** Dry run is the Enter-key default; Cancel and closing never lose data; nothing is overwritten. Say what is *not* touched ("Nothing was saved", "Your mail is never changed").
2. **Show state before asking for action.** Sign-in status, run state and folder warnings are visible before the user presses Run.
3. **One window, one path.** Settings on the left, results on the right; the same seven controls from first launch to re-run (PD-01).
4. **Plain words, never secrets.** Every message says what happened and what to do next in one or two sentences; no stack traces; no token, secret or auth code ever reaches any text (FR-005).
5. **One hand.** Every screen uses the same four type roles, one spacing scale, one palette and one button component (CLAUDE.md §9.2).

## 2. Personas & Key Tasks

| Persona | Top tasks | Context of use |
|---------|-----------|----------------|
| P-01 GUI user (today Santhosh), primary | One-time Google setup; pick dates; preview with dry run; run; watch progress; cancel; open folder, log, CSV; re-run | Windows 11 laptop or monitor, mouse and keyboard; ad hoc, about one run per period (PA-03); not a developer, so no terminal and no config files |
| P-02 CLI user (same person), secondary | Run with flags; script or repeat; read exit code; open log and CSV | Terminal or script; same rules and messages as the GUI (FR-064). Covered in section 12 |
| Approver (Santhosh at G8) | None in the UI | n/a |

No new personas.

## 3. User Journeys

### UJ-01 First-run Google setup and sign-in (P-01) — FR-001, 003, 005, 006, 065
- **Trigger:** first launch, `credentials.json` not found.
- **Steps:** 1 Launch; window opens on SCR-03 (setup steps, expected folder path, buttons disabled). 2 Do steps 1-6 in the browser (`Open Google Cloud Console` button). 3 `Open folder` and place `credentials.json`. 4 `Check again`: the view becomes SCR-02 and the header shows `Not signed in`. 5 Enter dates, press `Dry run` (UJ-02). 6 DLG-01 opens, browser opens, user chooses Allow (may pass Google's "not verified" page, text in SCR-03 step 8). 7 Dialog closes, header shows `Signed in`, the dry run continues by itself.
- **Recovery:** `Check again` with the file still missing keeps SCR-03 and says "Not found yet: credentials.json" (path shown). Denied or closed browser: DLG-02 `denied`. Help is always available (F1, DLG-07). Wrong file type is not detected by name; if Google rejects it the error is "Google did not accept the credentials file. Download it again as a Desktop app OAuth client." (UA-05).
- **Emotion / pain:** highest friction of the product (TR-006) and outside the app. Mitigation: numbered steps, buttons that do the two file actions, no jargon beyond Google's own labels.
- **Success:** token saved, second launch needs no browser (AC-01). Setup steps are identical to the README (single text source).

### UJ-02 Dry run (P-01) — FR-044, 047, 048, 049, 015
- **Trigger:** user wants to preview names. **Steps:** enter Start and End (time zone and folder already filled) → `Dry run` or Enter → validation → (sign-in if needed) → SCR-05 with "Searching Gmail..." → SCR-04 list, counts, notices.
- **Recovery:** invalid input shows inline errors and moves focus to the first one (nothing starts). Unreadable history: DLG-03. Zero results: SCR-04 shows `0 PDFs found`.
- **Success:** output folder tree identical before and after (the folder is not even created; the note under Output folder says so). GOAL-09: launch to list in ≤ 5 min after setup.

### UJ-03 Standard run (P-01) — FR-047, 050, 052, 042
- **Trigger:** user is happy with the plan or wants to download directly. **Steps:** `Run` (Ctrl+Enter) or `Run with these settings` → validation → folder check (MW states) → SCR-05 live counts → SCR-06 summary → `Open output folder`.
- **Recovery:** per-file errors do not stop the run (FR-036), they end as "Run finished with errors". Sign-in lost: DLG-02, then the run continues. Network or quota trouble: automatic retries (NFR-006) are invisible except that the elapsed time grows; a failing file becomes an Error row.
- **Success:** summary counts equal the CSV (GOAL-10); three open buttons work.

### UJ-04 Re-run, resume and duplicates (P-01) — FR-029, 030, 032, 033
- **Trigger:** same range again, or after Cancel or a crash. **Steps:** press `Run` (or `Run again` on SCR-06) → saved attachments report "Skipped, already downloaded" → summary shows 0 new files.
- **History states (all with exact text in 6.B):** MW-0 history fine (no notice). MW-1 no history file but folder holds date-prefixed PDFs: DLG-04 before a real run, notice in SCR-04, notice in SCR-06. MW-2 history lists files missing from the folder: notice in SCR-04 and SCR-06 (never a dialog; they are *not* re-downloaded, PD-02). MW-3 history unreadable: DLG-03 stops the run and dry run before anything is written (FR-032).
- **Success:** 0 duplicates, 0 lost; user understands why a deleted file did not come back.

### UJ-05 Errors and recovery (P-01) — FR-003, 006, 015, 032, 036, 005
| Situation | Where shown | User action |
|-----------|-------------|-------------|
| Invalid date, reversed range, bad time zone, bad folder | Inline under the field (SCR-01) | Fix the field |
| Credentials missing | SCR-03 | Follow steps, `Check again` |
| Token expired or revoked | DLG-02 (token already removed) | `Sign in`, run resumes |
| Consent denied | DLG-02 `denied` | `Try again` or `Close` |
| History unreadable | DLG-03 | Restore or move the file, run again |
| One attachment fails | SCR-06 Errors table, `Show details` (DLG-05) | Optionally `Run again` (errors are retried because they are not in the history, UA-06) |
| Sign-in fails during a run | SCR-06 `Could not sign in`; run log and CSV exist (GOAL-10) | `Open run log`, sign in again |
| Unexpected internal failure | SCR-06 `Unexpected failure` + `Show details` (redacted) | Open run log, copy details, report |
- **Success:** every message names the next step and contains no secret (sentinel-secret test, NFR-012).

### UJ-06 Cancel (P-01) — FR-037, 051
- **Steps:** during SCR-05 press `Cancel` (no confirmation: it is safe and resumable) → heading `Stopping...`, button disabled → within 5 s (NFR-004) SCR-06 `Run cancelled` with partial counts, log and CSV openable.
- **Recovery:** window close during a run: DLG-06. A hard kill is handled by the core (NFR-007); next launch needs nothing from the user.
- **Success:** no temp file, valid history, summary shown; text says a later run continues where this one stopped.

### UJ-07 CLI run (P-02) — FR-043, 045, 046, 015, 037 (section 12)
- **Steps:** run with flags → progress on stderr → summary on stdout → exit code. **Recovery:** exit 2 with a one-line fix hint; exit 3 prints the setup steps; Ctrl+C stops safely. **Success:** a script can branch on 0, 1, 2, 3.

### UJ-08 Sign out and Advanced (P-01, R3) — FR-007, 061, 063
- Header menu `Sign out` opens DLG-08 (destructive). `Advanced` opens SCR-07. Outline only; detailed when R3 is planned.

## 4. Information Architecture

Single-window application. No navigation menu, no tabs, no URLs, no deep links (desktop). The only "routes" are results-panel views and dialogs.

```
Main window (SCR-01)
|-- Header: app name | sign-in status | [Sign in] | [Help] (R3: account menu: Advanced, Sign out)
|-- Sidebar "Download settings": Start date, End date, Time zone, Output folder + Browse,
|                                Extra Gmail search, Include Spam and Trash, [Dry run], [Run]
|-- Results panel (exactly one view at a time)
|     SCR-02 Ready  |  SCR-03 Set up Google access  |  SCR-04 Dry-run results
|     SCR-05 Run in progress  |  SCR-06 Run summary
|-- Status bar: state text | version
Dialogs: DLG-01 waiting for sign-in | DLG-02 sign in again | DLG-03 history unreadable
         DLG-04 folder has PDFs, no history | DLG-05 details | DLG-06 close while running
         DLG-07 Google setup help | R3: DLG-08 sign out, SCR-07 Advanced
Entry points: launch (double-click or `python -m` command, SA decides) always opens SCR-01.
View rules: launch -> SCR-03 if credentials missing, else SCR-02.
            Dry run -> SCR-05 -> SCR-04.  Run -> SCR-05 -> SCR-06.
            Editing any setting after SCR-04 or SCR-06 leaves the view in place, marked "Settings changed".
```
Section names: "Download settings" (not "Parameters"), "Results" is never used as a visible label (each view has its own heading).

## 5. Screen Inventory

| Screen | Name | Purpose | Persona | Journeys | FRs |
|--------|------|---------|---------|----------|-----|
| SCR-01 | Main window shell + Download settings | Enter the seven settings, start dry run or run, sign-in status | P-01 | UJ-01..06 | 047, 048, 015, 008, 010, 013, 001, 053, 058..060 |
| SCR-02 | Ready (empty state) | Orient the user before any run | P-01 | UJ-02, 03 | 047 |
| SCR-03 | Set up Google access | Missing credentials: steps and next action | P-01 | UJ-01 | 006, 065 |
| SCR-04 | Dry-run results | Planned names and folder warnings | P-01 | UJ-02, 04 | 044, 049, 033 |
| SCR-05 | Run in progress | Live counts, cancel | P-01 | UJ-03, 06 | 050, 051, 053, 037 |
| SCR-06 | Run summary | Outcome, counts, open log/CSV/folder, errors | P-01 | UJ-03..06 | 042, 052, 036, 033, 016 |
| DLG-01..06 | Dialogs | Sign-in wait, re-consent, history, details, close | P-01 | UJ-01, 04..06 | 001, 003, 005, 032, 033, 037 |
| DLG-07 | Google setup help | Setup steps from anywhere | P-01 | UJ-01 | 006, 065 |
| DLG-08, SCR-07 | Sign out, Advanced (R3) | Outline | P-01 | UJ-08 | 007, 061 |
| CLI | Command line | Flags, progress, exit codes | P-02 | UJ-07 | 043, 045, 046 |

## 6. Screen Specifications

### 6.0 Cross-screen rules

**Run state machine (drives every screen).**
```
IDLE --submit--> VALIDATING --invalid--> IDLE (errors shown)
                      | valid
                      v
        [SIGNING_IN]* --> CHECKING_FOLDER --MW-3--> IDLE + DLG-03
                              | ok / confirmed (DLG-04)
                              v
                           SEARCHING --> RUNNING --> DONE_OK | DONE_ERRORS | DONE_NOTHING
                              |            |
                              |            +--Cancel--> CANCELLING --> DONE_CANCELLED
                              +--sign-in failed--> DONE_SIGNIN_FAILED       (* only when no valid token)
   Dry run follows the same path but ends in DRY_RESULT (never DONE_*), writes nothing, skips DLG-04.
```

**Interaction and state matrix.**

| State | Settings fields | Dry run / Run | Cancel | Results panel | Status bar | Announcement (live region) |
|-------|-----------------|---------------|--------|---------------|------------|----------------------------|
| IDLE (no credentials) | Editable | Disabled | n/a | SCR-03 | `Google setup needed` | none |
| IDLE (ready) | Editable | Enabled | n/a | SCR-02, or SCR-04/06 from last run | `Ready` | none |
| VALIDATING | Editable | Busy (labels unchanged, double-press ignored) | n/a | unchanged | `Checking settings...` | On failure: `N problems found. <first message>` (assertive) |
| SIGNING_IN | Read-only | Disabled | DLG-01 `Cancel` | SCR-05 `Waiting for Google sign-in` | `Waiting for Google sign-in` | `Waiting for Google sign-in` (polite) |
| CHECKING_FOLDER / SEARCHING | Read-only | Disabled | Enabled | SCR-05, bar indeterminate, `Searching Gmail...` | `Searching Gmail...` | `Searching Gmail` (polite) |
| RUNNING | Read-only | Disabled | Enabled | SCR-05 determinate | `Running: N of M messages` | Phase change; progress every 10 s at most, `412 of 1,000 messages, 2 errors` (polite) |
| CANCELLING | Read-only | Disabled | Disabled, label `Stopping...` | SCR-05 heading `Stopping...` | `Stopping...` | `Stopping, finishing the current file` (polite) |
| DONE_OK | Editable | Enabled | n/a | SCR-06 `Run complete` | `Run complete` | `Run complete. 301 saved, 0 errors.` (polite); focus moves to heading |
| DONE_ERRORS | Editable | Enabled | n/a | SCR-06 `Run finished with errors` | `Finished with errors` | `Run finished with errors. 2 errors.` (assertive) |
| DONE_NOTHING | Editable | Enabled | n/a | SCR-06 `No PDFs found` | `No PDFs found` | `No PDFs found` (polite) |
| DONE_CANCELLED | Editable | Enabled | n/a | SCR-06 `Run cancelled` | `Run cancelled` | `Run cancelled. N saved so far.` (polite) |
| DONE_SIGNIN_FAILED / stopped | Editable | Enabled | n/a | SCR-06 `Could not sign in` / `Unexpected failure` | same | assertive |
| DRY_RESULT | Editable | Enabled | n/a | SCR-04 | `Dry run complete` | `Dry run complete. 6 PDFs would be saved.` (polite) |
| DRY_RESULT stale | Editable | Enabled | n/a | SCR-04 plus notice `Settings changed since this preview. Choose Dry run to refresh.` | `Ready` | none |

Rules: **Validation timing**: a field is checked on blur; an errored field re-checks as the user types and clears the moment it is valid; all fields and the date order are checked on submit. **Undo**: none needed; no action is destructive except R3 Sign out. **Window close** during RUNNING/CANCELLING: DLG-06. **Responsiveness**: the UI thread never waits on the core (FR-053); counts update at most 4 times a second.

**Manifest warning states (FR-033).** All text is final.

| ID | Condition | Shown | Text |
|----|-----------|-------|------|
| MW-0 | History readable and consistent | nothing | none |
| MW-1 | No history file; output folder holds `YYYYMMDD_*.pdf` files | DLG-04 (real run); warning notice in SCR-04 and SCR-06 | Notice: `This folder has 42 PDFs but no download history file. If you continue, every PDF is saved again and names that match get a _1, _2 ... ending. Nothing is overwritten. To avoid this, choose a new output folder.` |
| MW-2 | History lists N files that are not in the folder | warning notice in SCR-04 and SCR-06 | `N files in the download history are no longer in the folder, so they are not downloaded again. To get them again, choose a new output folder. See the README section "Deleted files".` |
| MW-3 | History exists but cannot be read | DLG-03 (blocks run and dry run) | see dialogs.md |

**6.A Components (map to the design system in section 7).** AppButton (the only button), TextField, DateField, ComboBox, Checkbox, FolderField (TextField + secondary AppButton), Notice (info/success/warning/danger), StatusChip, ProgressBar, StatGroup, DataTable, Dialog, SetupSteps (shared by SCR-03 and DLG-07 and the README text), Header, StatusBar. A third-party control may be used only if it takes its look entirely from tokens.

**6.B Content and microcopy rules.**
1. Message shape: *what happened* + *what to do*, at most two sentences, no blame ("Enter the date as..." not "You entered an invalid date"), no error codes in the main text, no exclamation marks.
2. Technical detail goes only behind `Show details` (DLG-05), passed through the single redaction path (FR-005, GUI-11). Never in any text: tokens, refresh tokens, client secret, authorization codes, the full sign-in address, message body text. File paths, folder names, dates and attachment names may appear. Example addresses in docs and tests: `user@example.com`, `billing@example.com`.
3. Same sentence in GUI and CLI for the same condition (FR-064); the CLI prefixes the flag name.
4. Sentence case everywhere; buttons are verbs or verb phrases of at most three words; ellipsis only for "Browse...".
5. Numbers use thousands separators (`1,000`); sizes use `MB` with 1 MB = 1,000,000 bytes (UA-07); elapsed time `hh:mm:ss`; dates `YYYY-MM-DD`; file names exactly as saved.
6. Result labels (StatusChip, always icon + text): `SAVED` Saved; `SAVED_RENAMED` Saved, renamed; `SKIPPED_ALREADY_DOWNLOADED` Skipped, already downloaded; `SKIPPED_IDENTICAL` Skipped, identical (backlog); `NOT_A_PDF` Not a PDF; `ERROR` Error. Dry-run labels: `Would save`, `Would save, renamed`, `Already downloaded`.

Standard messages:

| Condition | Text |
|-----------|------|
| Start empty / End empty | `Enter a start date.` / `Enter an end date.` |
| Date malformed | `Enter the date as YYYY-MM-DD, for example 2026-01-31.` |
| Start after end | `Start date must be on or before the end date.` |
| End in the future (warning, run continues) | `End date is in the future. Only mail received so far is included.` |
| Time zone unknown | `Time zone not recognised. Pick one from the list, for example Europe/London.` |
| Folder empty | `Choose an output folder.` |
| Folder is a file | `That path is a file, not a folder. Choose a folder.` |
| Folder not writable (real run only) | `This folder cannot be used. Choose a folder you can write to.` |
| Extra search rejected by Gmail | `Gmail did not accept the extra search text. Check it and try again.` |
| Credentials missing | `Credentials file not found. Follow the setup steps, then choose Check again.` |
| Credentials rejected | `Google did not accept the credentials file. Download it again as a Desktop app OAuth client.` |
| Attachment error row | `Could not download it.` / `Could not save it in the output folder.` / `Gmail did not respond after several tries.` |
| Zero matches | `No PDF attachments were found from 2026-01-01 to 2026-01-31 (Asia/Kolkata). Check the dates, time zone and extra search text.` |
| Cancelled (first line `Run cancelled`, PD-13) | `Run cancelled. 120 PDFs were saved and kept; the date range was not completed. Run the same range again to carry on: files already saved are skipped.` |
| Download history unreadable (first line, GUI and CLI) | `<folder>\.manifest.json cannot be read.` then `Nothing was downloaded and the file was not changed. Restore it from a backup, or choose a new output folder.` |
| Sign-in failed | `Google sign-in did not finish, so nothing was downloaded. Open the run log for details.` |
| Unexpected failure (first line, GUI and CLI) | `Unexpected failure, see the run log. Your saved files are safe.` (GUI adds `Show details`) |

### SCR-01 Main window shell and Download settings
Wireframes W-01, W-02. **Components:** Header, FolderField, DateField x2, ComboBox, TextField, Checkbox, AppButton x2 (Dry run secondary, Run primary), StatusBar.

**Form fields**

| Field | Type | Required | Default | Validation (timing) | Error message |
|-------|------|----------|---------|---------------------|---------------|
| Start date | DateField, typed `YYYY-MM-DD`, optional calendar | Yes | empty | Real calendar date (blur, submit) | Empty/malformed messages above |
| End date | same | Yes | empty | Same; `>=` start (change of either, submit); future date is a warning | Same; order message shown once under the date pair, both fields marked invalid |
| Time zone | Editable ComboBox, IANA names, type-ahead | No | system zone, shown as `Asia/Kolkata (system)` | Must be in list (blur, submit) | Time zone message |
| Output folder | FolderField, typed path + `Browse...` | Yes | per UA-02 | Not empty, not a file (blur, submit); writable only checked on real run at submit | Folder messages |
| Extra Gmail search | TextField, optional | No | empty | None client-side (Gmail validates, FR-010) | Extra search message |
| Include Spam and Trash | Checkbox | No | off | n/a | n/a |

Helper text (Small label, always visible): Time zone `Dates and file names use this time zone.`; Output folder `A dry run does not create or change this folder.`; Extra search `Added to the Gmail search, for example from:billing@example.com`.

**Header.** App name (Subheading). Status chip: `Signed in` (success, check icon) or `Not signed in` (neutral, circle icon) with `Sign in` button only when not signed in and credentials exist; `Help` button always. Sign-in from the header runs the same flow as DLG-01 without a following run.

**States**

| State | Behaviour |
|-------|-----------|
| Default | Fields as above, no errors, both action buttons enabled |
| Loading | Not applicable at launch (window visible ≤ 3 s, NFR-004); time zone list populates before first paint |
| Empty | Dates empty is the default state; no errors until blur/submit |
| Partial | Some fields invalid: errors only on those, others untouched; focus on first invalid field on submit |
| Error | Field border `color.danger`, error icon and message under the field (Body role), field `aria-invalid` equivalent, described-by link to message |
| Success | No success state on the form |
| Disabled | Dry run and Run disabled when credentials are missing or a run is active; fields read-only (not disabled) during a run so text stays readable and copyable |
| Permission denied | Output folder not writable on a real run: folder error; sign-in denied: DLG-02 `denied` |

**Interactions.** Enter inside any field = Dry run (the safe action, writes nothing). Ctrl+Enter = Run, so a stray Enter can never start writing files (PD-15). A bare Enter on a focused button activates that button only. Both shortcuts are shown on screen as helper text (Small label) under the action buttons: `Enter: Dry run   Ctrl+Enter: Run`, and neither is the only way to start anything. `Browse...` opens the OS folder picker, returns focus to the field with the chosen path. Editing any field after a result adds the stale notice (only SCR-04). Pressing Dry run or Run while not signed in starts sign-in first (DLG-01) then continues with the chosen action; pressing while credentials are missing is impossible (buttons disabled, SCR-03 shown).

**Responsive.** 800-999 sidebar 320, 1000+ sidebar 360; panel takes the rest. Above content max width 1440 the whole layout stays 1440 wide and centred. Sidebar body scrolls; Dry run/Run are pinned at its bottom (sticky) and focused fields scroll into view above them (WCAG 2.4.11). Start and End sit side by side at all sizes (each ≥ 138 px wide).

**Accessibility.** Tab order: Help, Sign in (if shown), Start date, End date, Time zone, Output folder, Browse..., Extra Gmail search, Include Spam and Trash, Dry run, Run, then the results panel (heading target, then its controls in reading order). Labels are visible Small-label text bound to controls; helper and error text bound as descriptions. Calendar dropdown (if the date control has one) opens with Alt+Down and is never the only way to enter a date. Chips never rely on colour alone.

### SCR-02 Ready
W-01. Heading `Ready when you are`; body explains Dry run and Run in two bullets and says `Only PDF attachments are saved. Gmail is read-only: your mail is never changed.` If not signed in, a neutral Notice: `You will be asked to sign in to Google the first time you run.` **States:** default only (no data). **Accessibility:** heading is the programmatic focus target (focusable, not in tab order).

### SCR-03 Set up Google access
W-03, DLG-07. **Components:** SetupSteps, FolderField (read-only path), AppButton (Check again primary; Open folder, Copy path, Open Google Cloud Console secondary), Notice.
**Content:** the eight steps in W-03 (RD §2.1 steps 1-7 with the first-run sign-in note); step 8 adds `Google may say "Google hasn't verified this app". This is expected for an app you created yourself.` Footer line `Not found yet: credentials.json` appears after a failed check.
**States:** Default (not found); Checking (`Check again` busy for up to 2 s); Found (view switches to SCR-02, status `Credentials found`, announced); Error: file exists but unreadable `The credentials file could not be read. Download it again from Google and replace it.`; Permission denied: folder cannot be created `The folder could not be created. Choose Copy path and create it yourself.`
`Open Google Cloud Console` opens the system browser (the app itself makes no request, UQ-12). `Open folder` creates the folder if missing with private permissions (SEC-04) and opens it in the OS file manager.
**Responsive:** one column of text, max readable width 640 inside the panel. **Accessibility:** ordered list semantics; the path is selectable text; buttons in reading order; no step is conveyed by image.

### SCR-04 Dry-run results
W-04. **Components:** Heading, summary line (Body), Notice (0-3: PQ-01 notice, MW-1, MW-2), StatGroup (Would save, Renamed, Already downloaded, Messages scanned), DataTable, Details strip, AppButton `Run with these settings` (primary).
**Heading:** `Dry run: 8 PDFs would be saved`; zero: `Dry run: 0 PDFs found`. Subline: `2026-01-01 to 2026-01-31, Asia/Kolkata. Nothing was saved.` Table rows are in run order (received time, then message, then part: FR-014); long names truncate in the middle keeping the date prefix and extension, full name in the Details strip and tooltip.
**Columns by width:** 800-999 Result, Planned file name, Email date; 1000-1279 + Original name; 1280+ + From, Subject.
**States:** Default (list); Loading = SCR-05 view (no skeleton); Empty (0 found): table replaced by `No PDF attachments were found from ... Check the dates, time zone and extra search text.` and no `Run with these settings` button; Partial (folder does not exist): Notice `The output folder does not exist yet. It is created on a real run.`; Error: DLG-03 or a Notice (danger) `The dry run could not finish. Choose Show details.`; Stale: notice per matrix; Success: n/a.
**Interactions:** the table is one Tab stop; Up/Down/Home/End move the selected row, which fills the Details strip (original name, From, Subject, received date, planned name); Page Up/Down scroll. No sorting or filtering in MVP (UA-08). `Run with these settings` = Run.
**Accessibility:** data table with column headers and row count announced (`Table, 8 rows`); selection change announces the planned name and result; result labels are text, icon is decorative; table focus ring inside the panel; if the panel scrolls, the focused row stays visible.

### SCR-05 Run in progress
W-05. **Components:** Heading, phase line, ProgressBar, current-item line, StatGroup (Scanned, Saved, Renamed, Skipped, Errors), AppButton Cancel (secondary), helper text.
**Content:** heading `Downloading PDFs` (dry run: `Checking your mailbox`). Phase line `Message 412 of 1,000` plus elapsed time right-aligned; the percentage is shown as text beside the bar. Before the total is known: `Searching Gmail...` with an indeterminate bar (UQ-02: needs a total from the core after listing). Current-item line `Now: 20260115_Invoice_1.pdf`, truncated in the middle. Counts use the Heading role for numbers and Small label for captions.
**States:** Default running; Loading = signing in (`Waiting for Google sign-in`, bar indeterminate); Partial = some errors (Errors count turns `color.danger` and shows the error icon; text stays); Cancelling = `Stopping...`; Error: if the core fails fatally the view moves to SCR-06 `Unexpected failure`; Success: moves to SCR-06.
**Interactions:** Cancel needs no confirmation and acts once (second press ignored). Counts refresh ≤ 4 times per second; screen-reader announcements throttled (matrix).
**Responsive:** StatGroup is five columns at ≥ 480 px panel width, wraps 3 + 2 below. **Accessibility:** programmatic focus lands on the heading when the view opens; next Tab is Cancel. Progress bar exposes value, min, max and text `412 of 1,000 messages`. Reduced motion: no moving bar; show `Working...` and the changing numbers only.

### SCR-06 Run summary
W-06. **Components:** Heading, subline (range and time zone), outcome Notice (success, danger, warning or info), conditional history Notice (MW-1, MW-2), StatGroup with the seven LOG-04 fields (Messages scanned, PDFs saved, Renamed, Skipped, Errors, Total size, Elapsed), three AppButtons (secondary) Open output folder, Open run log, Open CSV report, Errors DataTable (only when errors > 0), `Show details`, `Run again` (secondary).
**Variants:** `Run complete` (success: `301 PDFs saved.`); `Run finished with errors` (danger: `2 PDFs could not be saved. The others were handled.`); `Run cancelled` (warning, text in 6.B); `No PDFs found` (info, zero-match text; counts still shown, "messages scanned" visible for the recall gap, PD-06); `Could not sign in` (danger); `Unexpected failure` (danger, text per 6.B). Each outcome has its own heading, so cancel, unreadable history (DLG-03) and internal failure are never confused with each other or with `Run complete` (PD-13). Open buttons appear only for files that exist (a stopped-before-writing run shows only what was written). Errors table columns: Original name, Email date, What happened (one of the 6.B phrases).
**States:** Default (above); Loading: none; Empty: `No PDFs found` variant; Partial: `finished with errors`; Error: `stopped`; Success: `complete`; Disabled: an Open button whose target was moved or deleted shows the status-bar message `That file is no longer there.`; Permission denied: `The folder could not be opened.` (status bar).
**Interactions:** open buttons call the OS shell; `Run again` repeats the run with current settings; focus is moved to the heading on arrival.
**Accessibility:** outcome Notice has a role announced on arrival (matrix); count pairs are label + value in reading order; tab order: three open buttons, Show details, Run again, Errors table.

### DLG-01..08, SCR-07
Full wireframes, text and keys in [wireframes/dialogs.md](wireframes/dialogs.md). Common rules: modal with scrim `color.scrim`; focus moves into the dialog on open (first button as listed there) and returns to the opener on close; Tab cycles inside; Esc = the dialog's safe action; title is the dialog's accessible name and the body its description; one primary button at most; dialog states beyond default: DLG-01 has a busy state, DLG-05 has `Copied` feedback; no dialog has a loading, empty or permission-denied state of its own.

## 7. Design Tokens / System Usage (CLAUDE.md §9.2)

Single source of truth: one token file consumed by every screen; nothing else may define a size, weight, spacing, radius or colour (FR-054..057; checked by code search at G6).

### 7.1 Typography — exactly four roles
Font family `font.ui` = the platform UI font (Segoe UI Variable, falling back to Segoe UI, on Windows; system UI font elsewhere). No bundled font (no dependency, always crisp at any scaling). No monospace, italics or underline-for-emphasis. Counts use tabular figures where the font has them.

| Role token | Size / line height | Weight | Used for |
|------------|--------------------|--------|----------|
| `type.heading` | 24 / 32 | 600 | One per view or dialog-less panel title; large numbers in StatGroup |
| `type.subheading` | 16 / 24 | 600 | App name in header, `Download settings`, dialog titles, `Errors (2)`, section titles |
| `type.body` | 14 / 20 | 400 | Body text, field values, inline error text, table cells, **button labels**, notices |
| `type.label` | 12 / 16 | 500 | Field labels, helper text, table column headers, chips, StatGroup captions, status bar |

### 7.2 Spacing — one scale
`space.1` 4, `space.2` 8, `space.3` 12, `space.4` 16, `space.5` 24, `space.6` 32, `space.7` 40, `space.8` 48. Usage: label-to-field `space.1`; field-to-field `space.4`; icon-to-text `space.2`; card/dialog padding `space.4` (dialog `space.5`); panel and window gutters `space.4` below 1000 px wide, `space.5` from 1000 px; section gaps `space.5`; control height `space.7` (40); header `space.8` (48); status bar `space.6` (32). Layout sizes (not spacing): `layout.window.min` 800 × 560, `layout.window.default` 1100 × 720, `layout.sidebar` 320 / 360, `layout.content.max` 1440, `layout.dialog` 480 / 560, `layout.read.max` 640. Shape: `shape.radius` 6 (every control, card, dialog), `shape.border` 1, `shape.focus-ring` 2 with offset 2, `shape.icon` 16. Motion: `motion.fast` 120 ms for hover and focus changes only; 0 when the OS asks for reduced motion.

### 7.3 Palette — one light palette (UA-09: no dark theme in R2)

| Token | Value | Use |
|-------|-------|-----|
| `color.bg` | #F4F6FA | Window background |
| `color.surface` | #FFFFFF | Sidebar, panel cards, dialogs, fields |
| `color.surface-sunken` | #E8ECF3 | Table header, progress track, read-only fields, secondary hover |
| `color.surface-pressed` | #D8DEE9 | Secondary pressed |
| `color.divider` | #D3D9E3 | Decorative separators only (never the only boundary of a control) |
| `color.border` | #6B7587 | Field and secondary-button borders |
| `color.text` | #14181F | Primary text |
| `color.text-muted` | #4A5466 | Helper text, captions |
| `color.text-disabled` | #7C8596 | Disabled text (exempt from contrast, kept ≥ 3:1) |
| `color.accent` / `-hover` / `-pressed` | #1D4ED8 / #1A44BD / #16399E | Primary button, progress fill, selected-row bar, info icon |
| `color.on-accent` | #FFFFFF | Text on accent and danger |
| `color.danger` / `-hover` / `-pressed` | #B42318 / #9C1E14 / #85190F | Destructive button, errors |
| `color.success`, `color.success-bg` | #0F6B3E, #E3F3EA | Success icon/text, notice fill |
| `color.warning`, `color.warning-bg` | #7A4300, #FFF1D6 | Warning icon/text, notice fill |
| `color.danger-bg`, `color.info-bg` | #FDE8E6, #E6EDFD | Error and info notice fill |
| `color.focus` | #0B2A8A | Focus ring on every focusable control |
| `color.scrim` | #14181F at 40 % | Behind dialogs |

Verified contrast (computed from the values above, WCAG relative luminance): text on bg 16.5, on surface 17.8, on sunken 15.0; muted on surface 7.6, on sunken 6.4; on-accent on accent 6.7, hover 8.1, pressed 9.9; on-accent on danger 6.6; accent on surface 6.7; danger on surface 6.6 and on danger-bg 5.6; success on success-bg 5.7; warning on warning-bg 7.2; text on every notice fill ≥ 15; `color.border` on surface 4.7, on bg 4.3, on sunken 3.9 (needs 3:1); `color.focus` on bg 11.3, on surface 12.3, on sunken 10.4; progress fill on track 5.7. All pass NFR-018 (4.5:1 text, 3:1 UI). A script re-checks this table from the token file (NFR-018).

### 7.4 AppButton — the only button (FR-056)
One component, one size (height 40, min width 96, horizontal padding `space.4`, radius `shape.radius`, label `type.body`, optional 16 px leading icon). No icon-only buttons exist (a date control's built-in calendar is part of the field). Variants:

| Variant | Fill / border / label | Hover | Pressed | Use |
|---------|-----------------------|-------|---------|-----|
| primary | accent / none / on-accent | accent-hover | accent-pressed | The one recommended action in a view or dialog |
| secondary | surface / `color.border` 1 / `color.text` | surface-sunken | surface-pressed | Every other action |
| destructive | danger / none / on-accent | danger-hover | danger-pressed | Only R3 `Sign out` (removes local sign-in) |

States for all variants: default, hover, pressed, focus-visible (ring `color.focus` 2 px, offset 2), disabled (fill surface-sunken, label text-disabled, no border change), busy (label replaced by the busy label, e.g. `Stopping...`, input ignored). Rules: at most one primary per view and per dialog; label states the action, not `OK`.

### 7.5 Fields, notices, table (all token-driven)
Field: height 40, border `color.border`, radius, error state border `color.danger` plus icon plus message, read-only fill `color.surface-sunken`. Notice: fill `*-bg`, 16 px icon in the semantic colour, text `color.text`. DataTable: header `type.label` on `color.surface-sunken`, rows separated by `color.divider`, selected row = `color.info-bg` fill plus a 4 px leading bar in `color.accent` plus the focus ring when focused.

### 7.6 Layout, reflow and high-DPI (FR-058, 059; NFR-021)
- **Window:** resizable, minimum 800 × 560 (PD-12), maximise allowed. If the work area is smaller than the minimum the window is clamped to the work area and content scrolls instead of clipping; below 800 px wide the layout stacks (sidebar above panel) with one vertical scroll.
- **Reflow:** 800-999 compact (sidebar 320); 1000-1439 regular (sidebar 360); 1440+ content stops at `layout.content.max`, centred, extra space becomes gutter and the table gains rows, not stretched columns. Table columns follow the rules in SCR-04.
- **Overflow:** names truncate in the middle; no horizontal page scroll at ≥ 800 px; only the table and DLG-05 text may scroll horizontally if needed.
- **High-DPI:** every size is logical px; icons are vector; the app must be per-monitor DPI aware and re-lay out when moved between monitors; 1 px borders stay 1 logical px. If the OS text size is increased, layouts must grow, not clip (best effort, Should).
- **Test matrix (screenshots at G7):**

| Physical screen | Scaling | Logical size | Check |
|-----------------|---------|--------------|-------|
| 1366 × 768 | 100 % | 1366 × 768 | regular layout |
| 1920 × 1080 | 100 % | 1920 × 1080 | content capped at 1440 |
| 1920 × 1080 | 150 % | 1280 × 720 | regular layout |
| 1920 × 1080 | 200 % | 960 × 540 (work area about 960 × 520) | **PD-12:** window clamped to the work area, below the 560 minimum; columns scroll; nothing clipped (FR-058 screenshot) |
| 3840 × 2160 | 100 % | 3840 × 2160 | content capped and centred |
| 3840 × 2160 | 200 % | 1920 × 1080 | as 1920 × 1080 |
| any | 100 / 150 / 200 % | min window 800 × 560 | W-02 intact |

## 8. Accessibility Requirements (reference WCAG 2.2 AA; formal conformance is a Won't, NFR-017..019)

### 8.1 Keyboard (Must, FR-060)
| Key | Action |
|-----|--------|
| Tab / Shift+Tab | Next / previous control in the order of SCR-01 |
| Enter in a field | Dry run |
| Ctrl+Enter | Run (when enabled); shown on screen with Enter (PD-15) |
| Enter on a focused button | Activates that button only |
| Space / Enter on a button | Activate |
| F1 | Help (DLG-07) |
| Esc | Close the open dialog with its safe action; never cancels a run |
| Alt+Down | Open ComboBox list or date calendar |
| Up/Down, Home/End, Page Up/Down | Move in table, lists, combo list |
| Alt+letter access keys | Should (platform convention), listed in the ADR |
Enter and Ctrl+Enter are fixed by PD-15; no shortcut is the only way to do something. No keyboard trap anywhere (dialogs cycle but Esc exits).

### 8.2 Focus
Visible ring (`color.focus`, 2 px, offset 2, ≥ 3:1) on 100 % of focusable controls; never removed or covered (sticky action bar must not hide the focused field). Moves: open dialog → first button listed; close → opener; view change → new view's heading (focusable, not in tab order); failed submit → first invalid field; run start → results heading; run end → summary heading; `Choose another folder` → Browse button.

### 8.3 Colour, size, motion
Contrast per 7.3. Colour is never the only signal: every status has icon + text, errors have icon + text, selection has a bar. Targets ≥ 40 × 40 px (WCAG minimum 24 × 24). Motion: only progress and 120 ms transitions; none when OS reduce-motion is on. Text never below 12 px logical.

### 8.4 Error identification and status messages
Errors are text under the field, linked to it; on submit failure one assertive announcement `N problems found. <first message>`. Dynamic updates use two live regions: polite (progress, phase, completion) and assertive (errors, stopped); progress announced at most every 10 s. Dialogs expose title and description.

### 8.5 Screen reader (Should, R3, FR-063/NFR-019)
Designed in from R2 so it is not rework: every control has a visible label used as its name; roles: window, banner (header), form group `Download settings`, status (status bar), progress bar with value text, table with headers, dialog/alertdialog (DLG-03, DLG-04 are alertdialogs), list (setup steps). Narrator walkthrough of UJ-02 and UJ-03 is the R3 test.

## 9. FR → Screen Coverage (every user-facing FR)

| FR | Screens / states | Journeys |
|----|------------------|----------|
| 001 | Header chip + Sign in, DLG-01, DLG-02 | UJ-01 |
| 002 | Defaults per 0 (PQ-03); SCR-07 (R3); CLI | UJ-01, 08 |
| 003 | DLG-02 | UJ-05 |
| 004 | SCR-03 (shows private folder), defaults in 0 | UJ-01 |
| 005 | 6.B rule 2, DLG-05, every message | all |
| 006 | SCR-03, DLG-07, CLI exit 3 | UJ-01 |
| 007 (R3) | DLG-08 | UJ-08 |
| 008 | SCR-01 Start, End, Time zone | UJ-02, 03 |
| 009, 011, 012, 014 | No UI of their own; order visible in SCR-04 list; `of N` in SCR-05 | UJ-02, 03 |
| 010 | SCR-01 Extra Gmail search | UJ-02, 03 |
| 013 | SCR-01 Include Spam and Trash | UJ-02, 03 |
| 015 | SCR-01 validation, 6.B messages, CLI errors | UJ-02, 05 |
| 016 | SCR-04 empty, SCR-06 `No PDFs found` | UJ-02, 03 |
| 017 | "Messages scanned" in SCR-04/06 (PD-06) | UJ-02, 03 |
| 018-021 | Not a UI concern; `Not a PDF` label (6.B) when produced; counts in SCR-06 | UJ-03 |
| 022-026 | Planned names in SCR-04, saved names in CLI/CSV | UJ-02 |
| 027 | SCR-06 Errors row `Could not save it in the output folder.` | UJ-05 |
| 028, 031 | No UI (safety text in SCR-05 helper) | UJ-06 |
| 029 | SCR-04 `Already downloaded`, SCR-06 Skipped | UJ-04 |
| 030 | SCR-05 helper, SCR-06 cancelled text, `Run again` | UJ-04, 06 |
| 032 | DLG-03 (MW-3) | UJ-04, 05 |
| 033 | DLG-04, MW-1/MW-2 notices in SCR-04 and SCR-06 | UJ-04 |
| 034 (R3), 035 (BL), 038 (BL) | No UI in MVP; MW-1 text revisited in R3 | n/a |
| 036 | SCR-06 `finished with errors`, Errors table | UJ-05 |
| 037 | SCR-05 Cancel, `Stopping...`, DLG-06, CLI Ctrl+C | UJ-06 |
| 039-041 | SCR-06 `Open run log`, `Open CSV report` | UJ-03 |
| 042 | SCR-06 seven fields; CLI summary | UJ-03, 07 |
| 043 | CLI exit codes (section 12) | UJ-07 |
| 044 | SCR-04, folder untouched note | UJ-02 |
| 045 | CLI flags (section 12) | UJ-07 |
| 046 | CLI `--log-level`; SCR-07 (R3) | UJ-07 |
| 047 | SCR-01..06 | UJ-02, 03 |
| 048 | SCR-01 validation | UJ-02, 05 |
| 049 | SCR-04 | UJ-02 |
| 050 | SCR-05 StatGroup | UJ-03 |
| 051 | SCR-05 Cancel | UJ-06 |
| 052 | SCR-06 | UJ-03 |
| 053 | 6.0 responsiveness rule, 7.6 | all |
| 054-057 | Section 7.1-7.3, 7.4 | all |
| 058, 059 | Section 7.6, matrix | all |
| 060 | Section 8.1, 8.2 | all |
| 061 (R3) | SCR-07 | UJ-08 |
| 062 | Section 10 checklist | n/a |
| 063 (R3) | Section 8.5 | UJ-02, 03 |
| 064 | 6.B rules 3, CLI messages, same statuses and counts | UJ-07 |
| 065, 066 | `SetupSteps` text is the README text (single source); revoke text in DLG-07 | UJ-01 |

All 66 FRs are mapped; FRs with no direct UI are listed so nothing is orphaned.

## 10. Usability Risks, Validation Plan and FR-062 Checklist

| Risk / assumption | Test | Success measure |
|-------------------|------|-----------------|
| UR-1 Google setup (SCR-03) is too long to finish unaided | Task T1: from a fresh profile reach `Signed in` using only the app text | Completed without help; time recorded (not part of GOAL-09) |
| UR-2 "Dry run" is not understood | T2: "Check what would be saved for last week without saving" | Chooses Dry run first time; reads "Nothing was saved" aloud correctly |
| UR-3 GOAL-09 (≤ 5 min launch to dry-run list) | T3: three timed trials by the sponsor at G7 (needs TR-006) | Median ≤ 5 min; no command typed |
| UR-4 Cancel is feared as destructive | T4: cancel mid-run, then re-run | Says files stay; re-run saves 0 duplicates |
| UR-5 "Deleted file is not re-downloaded" (MW-2) surprises the user | T5: delete a PDF, re-run, read the notice | Explains why it did not return |
| UR-6 Progress without a total in the search phase looks stuck | Observe T3/T4 | No user presses Cancel because of a stalled bar |
| UR-7 12 px labels hard to read | T6 at 100 % and 150 % scaling | No missed field label or helper |
| UR-8 Unverified-app page frightens the user | T1 observation | Continues after reading step 8 |
Small sample (one real user plus two proxy testers, UA-11); results are findings, not statistics.

**FR-062 UX consistency checklist (signed at G6/G7):** (1) only four text styles in use; (2) every gap, padding and margin from the scale; (3) one button component, variants only primary/secondary/destructive, at most one primary per view; (4) no literal colour outside the token file; (5) same header, panel heading, notice, table and dialog frame on every view; (6) every error is icon + text + next step; (7) focus ring visible on every control; (8) min-size and 100/150/200 % screenshots clean; (9) no secret in any text (sentinel test); (10) wording matches section 6.B and the CLI.

## 11. Open Questions, Assumptions, Needs for the Architect

| ID | Item | Owner | Needed by | Working assumption |
|----|------|-------|-----------|--------------------|
| UA-01 | Framework can clamp the window to the work area and scroll below its own minimum (PD-12 fixed 800 × 560; only feasibility is open) | SA | G3 ADR | Yes |
| UA-02 | GUI default folders (section 0) | SA | G3 | As stated; CLI unchanged |
| UA-03 | Dry run fetches no bytes (PQ-01) | SA | G3 | Notice in SCR-04 |
| UA-04 | **Closed (PD-13)** for the product rule: non-zero, not 2/3, distinct first line. Only the numeric mapping is open (PM position 1) | SA | G3 | 1 for all three |
| UA-05 | Distinguish a wrongly-typed credentials file | SA | R2 | Message only if Google rejects it |
| UA-06 | Errored attachments are not recorded in the history, so a re-run retries them | SA | G3 | Yes |
| UA-07 | **Closed (PD-14a)** decimal MB | | | |
| UA-08 | **Closed (PD-14b)** no sort or filter in R2 | | | |
| UA-09 | **Closed (PD-14c)** light theme only | | | |
| UA-10 | **Closed (PD-15)** Enter = Dry run, Ctrl+Enter = Run, shortcuts shown on screen | | | |
| UA-11 | Small-sample usability testing | qa-engineer | G7 | Yes |
| UQ-02 | Core emits a total after listing, the current item name and per-attachment error reason (for SCR-05/06) | SA | G3 | Yes; otherwise indeterminate bar for the whole run |
| UQ-05 | **Closed (PD-14d)** last folder and Spam/Trash choice not remembered | | | |
| UQ-06 | Timeout for DLG-01 | SA | G3 | UX only needs Cancel always available |
| UQ-09 | **Closed (PD-14c)** no dark theme in R1/R2 | | | |
| UQ-10 | **Closed (PD-16)** `--help` / `-h` allowed, exits 0, no network or credential access | | | |
| UQ-12 | `Open Google Cloud Console` opens the system browser (no app network call; consistent with NFR-014) | SA | G3 | Yes |

**Framework requirements to test in the RISK-012 spike (SA):** full token-driven theming (no per-widget literals), one custom button component with the three variants, per-monitor DPI awareness and re-layout, visible customisable focus ring, tab order control, minimum window size, keyboard-navigable table with one tab stop, status/live announcements (UIA notifications or equivalent), accessible names and roles (R3), reduced-motion signal, native folder picker, opening files and folders in the OS shell, a time zone list from the chosen time zone data package (Q-08).

**Issues for other roles**
- **product-manager:** all earlier UX issues are closed by PRD v0.3 (PD-11..16). Nothing open for the PM from this spec.
- **solution-architect:** UA-01 (clamp/scroll below the framework minimum), UA-02, UA-03, UA-04 numeric mapping, UA-05, UA-06, UQ-02, UQ-06, UQ-12, and the spike list above; the core must emit progress events (total, current item, counts) and an error reason per attachment, and a cancel signal that ends within 5 s.
- **product-owner / scrum-master:** stories should reference SCR/DLG IDs; SetupSteps is a shared component that the README must reuse as text. The README sections the UI points to ("Deleted files", "Download history") must give the PD-11 advice: choose a new output folder; do not delete or move `.manifest.json`.

## 12. CLI Interaction (P-02; FR-043, 045, 046, 015, 037, 064)

**Invocation (RD §3):** `python gmail_pdf_downloader.py --start 2026-01-01 --end 2026-01-31 [options]`.

| Flag | Default | Notes |
|------|---------|-------|
| `--start`, `--end` | required | `YYYY-MM-DD`, inclusive |
| `--out` | `./downloads` | created on a real run only |
| `--tz` | system zone | IANA name |
| `--query` | empty | extra Gmail search text |
| `--include-spam-trash` | off | |
| `--dry-run` | off | writes nothing |
| `--credentials`, `--token` | `./secrets/...` or `GMAIL_CREDENTIALS_PATH`, `GMAIL_TOKEN_PATH` | option beats env var beats default |
| `--log-level` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
Unknown flags exit 2 (FR-045). `--help` / `-h` (PD-16) prints this table with defaults and exits 0, without contacting Google or reading credentials. No `--version` or other extra flag.

**Streams.** stdout carries the dry-run list and the final summary (safe to redirect to a file). stderr carries progress, warnings and errors. No colour is needed; if added later it must honour `NO_COLOR` and never be the only signal.

**Progress (stderr).** Interactive terminal: one updating line `Searching Gmail...` then `412/1,000 messages | saved 301 | renamed 12 | skipped 97 | errors 2 | 00:06:41`, redrawn at most once a second. Not a terminal (piped, scheduled): no redraw; a plain line every 10 % or 60 s, whichever is later. Sign-in: `Opening your browser to sign in to Google (read-only access). Waiting...`; if the browser cannot open, the sign-in address is printed (contains no token; UQ-12/SA to confirm).

**Dry-run output (stdout).** One line per planned file, stable lower-case result tokens, then the summary with `Dry run: nothing was written.`
```
would-save           20260115_Invoice.pdf     (Invoice.pdf, received 2026-01-15)
would-save-renamed   20260115_Invoice_1.pdf   (Invoice.pdf, received 2026-01-15)
already-downloaded   20260116_Invoice.pdf     (Invoice.pdf, received 2026-01-16)
```

**Final summary (stdout), same seven fields and labels as SCR-06.**
```
Run complete
  Range              2026-01-01 to 2026-01-31 (Asia/Kolkata)
  Messages scanned   1,000
  PDFs saved         301
  Renamed            12
  Skipped            97
  Errors             2
  Total size         412.3 MB
  Elapsed            00:09:58
Output folder: ./downloads
Run log:       ./downloads/logs/run_20260129_101500.log
CSV report:    ./downloads/logs/report_20260129_101500.csv
```
First line varies: `Run complete`, `Run finished with errors`, `Run cancelled`, `No PDFs found` (also prints `0 PDFs found.`). History notices (MW-1, MW-2) print as `warning:` lines before and in the summary, with the same text as the GUI (section 6.0), including the new-output-folder advice (PD-11).

**Errors (stderr), one line each:** `error: --start: Enter the date as YYYY-MM-DD, for example 2026-01-31.`; `error: Start date must be on or before the end date. (--start 2026-03-31 --end 2026-01-01)`; `warning: End date is in the future. Only mail received so far is included.`; credentials missing prints the eight SCR-03 steps (plain text) after `error: Credentials file not found: <path>`. Stack traces never print; at `DEBUG` the same redaction applies.

**Cancel.** First Ctrl+C: `Stopping: finishing the current file and saving progress...` then the summary as `Run cancelled`. A second Ctrl+C prints `Already stopping, please wait.` and is otherwise ignored (closing the terminal is a safe hard kill, FR-028/030).

**First lines for outcomes the RD does not name (PD-13; identical wording in the GUI heading or dialog text).**

| Outcome | CLI first line | GUI |
|---------|----------------|-----|
| Cancelled | `Run cancelled` (then the summary) | SCR-06 heading `Run cancelled` |
| History unreadable | `error: <folder>/.manifest.json cannot be read. Nothing was downloaded and the file was not changed. Restore it from a backup, or choose a new output folder.` | DLG-03 |
| Internal failure | `error: unexpected failure, see the run log` | SCR-06 `Unexpected failure` |
| Attachment errors | `Run finished with errors` | SCR-06 same |
No stack trace and no secret in any of them (FR-005).

**Exit codes (LOG-05, FR-043).**

| Code | Meaning | Output |
|------|---------|--------|
| 0 | Success, including 0 PDFs found and dry run | Summary |
| 1 (PM position; numeric mapping is the SA's, PD-13) | At least one attachment errored; also cancelled, unreadable history, unexpected failure. Never 0, 2 or 3 for these | See first-line table below |
| 2 | Bad arguments or unknown flag | One-line `error:` plus hint |
| 3 | Credentials missing or authentication failed | Setup steps or `error: Google sign-in did not finish.` |

## 13. Change Log
| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-10-29 | Initial UX spec for G3: PQ-03 answered, tokens, 6 views, 8 dialogs, CLI interaction |
| 0.2 | 2026-10-29 | Aligned to PRD v0.3: PD-11 MW-1/MW-2/DLG-03/DLG-04 text now advises a new output folder, never deleting the manifest; PD-12 clamp-to-work-area rule and 1920 × 1080 / 200 % matrix row; PD-13 distinct first lines for cancel, unreadable history and internal failure (GUI and CLI); PD-14 UA-07..09, UQ-05, UQ-09 closed; PD-15 shortcuts shown on screen; PD-16 `--help` / `-h`. Closed UA-04 (product rule), UA-07..10, UQ-05, UQ-09, UQ-10 |
