# Wireframes — Main window (SCR-01 shell and views SCR-02..06)

Companion to [../ux-spec.md](../ux-spec.md) (spec for every region, state, text and keyboard rule). ASCII only; widths are logical px. `[ Button ]` is the one shared AppButton (variant in brackets where it matters). `(*)` marks the programmatic focus target of a view. No real data: names, dates and counts are placeholders.

## W-01 Shell at regular size (1000 × 700), view SCR-02 Ready

```
+------------------------------------------------------------------------------------------------+
| Gmail PDF Attachment Downloader                  (o) Not signed in  [Sign in]  [Help]          |  HEADER 48
+---------------------------------+--------------------------------------------------------------+
| Download settings               |  Ready when you are                                    (*)   |
|                                 |                                                              |
| Start date          End date    |  Pick a date range, then:                                    |
| [2026-01-01 ]  [2026-01-31 ]    |   - Dry run lists the file names without saving anything.    |
|                                 |   - Run saves the PDFs into your output folder.              |
| Time zone                       |                                                              |
| [Asia/Kolkata (system)      v]  |  Only PDF attachments are saved. Gmail is read-only: your    |
| Dates and file names use this   |  mail is never changed.                                      |
| time zone.                      |                                                              |
|                                 |                                                              |
| Output folder                   |                                                              |
| [C:\Users\you\Downloads\...][Browse...]                                                        |
|                                 |                                                              |
| Extra Gmail search (optional)   |                                                              |
| [from:billing@example.com   ]   |                                                              |
| Added to the Gmail search.      |                                                              |
|                                 |                                                              |
| [x] Include Spam and Trash      |                                                              |
|                                 |                                                              |
| [ Dry run ]  [ Run ]            |                                                              |  pinned action bar
+---------------------------------+--------------------------------------------------------------+
| Ready                                                                              Version 0.0  |  STATUS BAR 32
+------------------------------------------------------------------------------------------------+
  SIDEBAR 360 (320 below 1000)      RESULTS PANEL (fluid)
```
`[ Dry run ]` is secondary, `[ Run ]` is primary. Header `[Sign in]` and `(o) Not signed in` are shown only when the token is missing; when signed in the chip reads `(v) Signed in`. The account address is never shown (no API call is allowed to fetch it: NFR-011).

## W-02 Shell at minimum size (800 × 560), view SCR-02

```
+------------------------------------------------------------------------+
| Gmail PDF Attachment Downloader      (o) Not signed in [Sign in] [Help]|  48
+----------------------------+-------------------------------------------+
| Download settings          | Ready when you are                  (*)   |
| Start date    End date     |                                           |
| [2026-01-01] [2026-01-31]  | Pick a date range, then:                  |
| Time zone                  |  - Dry run lists the file names ...       |
| [Asia/Kolkata (system)  v] |  - Run saves the PDFs ...                 |
| Output folder              |                                           |
| [C:\Users\you\Dow..][Browse]                                           |
| Extra Gmail search (opt.)  |                                           |
| [                        ] |                                           |
| [x] Include Spam and Trash |                                           |
| ~ sidebar body scrolls ~   |  ~ panel scrolls ~                        |
| [ Dry run ] [ Run ]        |                                           |  pinned
+----------------------------+-------------------------------------------+
| Ready                                                      Version 0.0 |  32
+------------------------------------------------------------------------+
  SIDEBAR 320                 RESULTS PANEL (fluid, 480)
```
Each column scrolls on its own; the action bar and header never scroll away. Below 800 logical px wide (only if the OS clamps the window to a small screen) the layout stacks: sidebar above panel, one vertical scroll.

## W-03 SCR-03 Google setup required (replaces the results panel; sidebar stays but Dry run and Run are disabled)

```
+---------------------------------+--------------------------------------------------------------+
| Download settings   (as W-01)   |  Set up Google access                                  (*)   |
| ...                             |                                                              |
|                                 |  This is a one-time step. Google needs to know this app is   |
|                                 |  yours before it can read your mail (read-only).             |
|                                 |                                                              |
|                                 |  1. Open Google Cloud Console and create a project.          |
|                                 |  2. Turn on the Gmail API for that project.                  |
|                                 |  3. Set up the OAuth consent screen: choose External         |
|                                 |     (personal Gmail) or Internal (Workspace), add the app    |
|                                 |     name and your email, and add yourself as a Test user.    |
|                                 |  4. Add one permission only: gmail.readonly.                 |
|                                 |  5. Create credentials: OAuth client ID, type Desktop app.   |
|                                 |  6. Download the JSON file and name it credentials.json.     |
|                                 |  7. Put it in this folder:                                   |
|                                 |     [C:\Users\you\AppData\Local\...\secrets      ]           |
|                                 |     [ Open folder ]  [ Copy path ]                           |
|                                 |  8. Come back here and choose Check again. The first time    |
|                                 |     you run, your browser opens: sign in and choose Allow.   |
|                                 |                                                              |
|                                 |  [ Check again ] [ Open Google Cloud Console ]               |
| [ Dry run ]x [ Run ]x           |  Not found yet: credentials.json                             |
+---------------------------------+--------------------------------------------------------------+
```
`[ Check again ]` is primary; the others are secondary. The step list uses a real ordered list. Same content, in a dialog, is DLG-07 (Help).

## W-04 SCR-04 Dry-run results (regular and wider)

```
+---------------------------------+--------------------------------------------------------------+
| Download settings  (as W-01)    |  Dry run: 8 PDFs would be saved                        (*)   |
|                                 |  2026-01-01 to 2026-01-31, Asia/Kolkata. Nothing was saved.  |
|                                 |                                                              |
|                                 |  [!] Names are planned from message details. PDFs are not    |
|                                 |      opened in a dry run, so a file that is not really a     |
|                                 |      PDF can only be found in a real run.                    |
|                                 |  [!] 2 files in the download history are no longer in the    |
|                                 |      folder. They will not be downloaded again.   (MW-2)     |
|                                 |                                                              |
|                                 |  Would save 6 | Renamed 1 | Already downloaded 1 | Scanned 9 |
|                                 |                                                              |
|                                 |  Result              Planned file name          Email date   |
|                                 |  ------------------- -------------------------- ----------   |
|                                 |  (v) Would save      20260115_Invoice.pdf       2026-01-15   |
|                                 |  (v+) Would save,    20260115_Invoice_1.pdf     2026-01-15   |
|                                 |       renamed                                                |
|                                 |  (-) Already         20260116_Invoice.pdf       2026-01-16   |
|                                 |       downloaded                                             |
|                                 |  ...                                                         |
|                                 |  ------------------------------------------------------------|
|                                 |  Details: original name Invoice.pdf; from billing@example.com|
|                                 |  [ Run with these settings ]                                 |
| [ Dry run ]  [ Run ]            |                                                              |
+---------------------------------+--------------------------------------------------------------+
```
At 1280 and wider the table adds `Original name`, `From` and `Subject` columns; at 800 to 999 only `Result`, `Planned file name`, `Email date` show and the rest is in the Details line under the table (row selected with Up/Down). `[ Run with these settings ]` is primary and starts a real run with the current settings (same as `[ Run ]`).

## W-05 SCR-05 Run in progress (sidebar read-only; Run and Dry run disabled)

```
+---------------------------------+--------------------------------------------------------------+
| Download settings (read-only)   |  Downloading PDFs                                      (*)   |
| Start date  [2026-01-01]        |  Message 412 of 1,000                         00:06:41       |
| ...                             |  [########-----------------------------]  41 %               |
|                                 |  Now: 20260115_Invoice_1.pdf                                 |
|                                 |                                                              |
| (Dry run and Run disabled)      |   Scanned     Saved    Renamed    Skipped    Errors          |
|                                 |    412          301       12         97         2            |
|                                 |                                                              |
|                                 |  [ Cancel ]                                                  |
|                                 |  Cancel is safe: finished files stay, and a later run        |
|                                 |  carries on from where this one stopped.                     |
+---------------------------------+--------------------------------------------------------------+
| Running: 412 of 1,000 messages                                                                 |
+------------------------------------------------------------------------------------------------+
```
While the search is still listing messages the bar is indeterminate and the line reads `Searching Gmail...` (no `of N`). While signing in the panel shows `Waiting for Google sign-in` and DLG-01 is open on top. After Cancel is chosen the heading becomes `Stopping...`, the bar is frozen, `[ Cancel ]` shows `Stopping...` and is disabled.

## W-06 SCR-06 Run summary (variants by outcome)

```
+---------------------------------+--------------------------------------------------------------+
| Download settings (editable     |  Run finished with errors                              (*)   |
| again)                          |  2026-01-01 to 2026-01-31, Asia/Kolkata                      |
|                                 |  [x] 2 PDFs could not be saved. The other 308 were handled.  |
|                                 |  [!] 2 files in the download history are no longer in the    |
|                                 |      folder. They were not downloaded again.       (MW-2)   |
|                                 |                                                              |
|                                 |  Messages scanned  1,000      Total size   412.3 MB          |
|                                 |  PDFs saved          301      Elapsed      00:09:58          |
|                                 |  Renamed              12                                      |
|                                 |  Skipped              97                                      |
|                                 |  Errors                2                                      |
|                                 |                                                              |
|                                 |  [ Open output folder ] [ Open run log ] [ Open CSV report ] |
|                                 |                                                              |
|                                 |  Errors (2)                                                  |
|                                 |  Original name        Email date   What happened            |
|                                 |  Report.pdf           2026-01-20   Could not download it.   |
|                                 |  [ Show details ]  [ Run again ]                             |
| [ Dry run ]  [ Run ]            |                                                              |
+---------------------------------+--------------------------------------------------------------+
```
Banner text and icon per outcome: `Run complete` (success), `Run finished with errors` (danger), `Run cancelled` (warning), `No PDFs found` (info), `Could not sign in` (danger). `[ Run again ]` is secondary and reuses the same settings (already saved files are skipped). `Errors` table appears only when errors > 0.
