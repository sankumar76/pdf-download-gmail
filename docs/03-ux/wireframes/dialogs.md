# Wireframes — Dialogs (DLG-01..08)

Companion to [../ux-spec.md](../ux-spec.md). All dialogs are modal, centred over the main window, 480 logical px wide (shrinks to window width minus `space.6` when the window is narrower), grow in height with content, and use the same frame: title (Subheading), body (Body), button group at the bottom right. Buttons are the shared AppButton. Esc closes a dialog with its safe action (named per dialog). Focus goes to the first button listed in each wireframe unless stated. Placeholders only.

## DLG-01 Waiting for Google sign-in (blocking; no close box)
```
+--------------------------------------------------+
| Sign in with Google                              |
|                                                  |
| Your browser has opened. Sign in and choose      |
| Allow so this app can read your Gmail            |
| (read-only). It cannot send, delete or change    |
| mail.                                            |
|                                                  |
| Waiting for Google...  [progress, indeterminate] |
|                                                  |
|                                       [ Cancel ]|  secondary
+--------------------------------------------------+
```
Esc = Cancel. On cancel: dialog closes, view returns to SCR-02 with notice `Sign-in cancelled. Nothing was downloaded.` On denied or failed: replaced by DLG-02 variant `denied`.

## DLG-02 Sign-in needed again (token expired, revoked, or consent denied)
```
+--------------------------------------------------+
| Sign in to Google again                          |
|                                                  |
| Your saved Google sign-in has expired or was     |
| revoked, so the app cannot read your Gmail yet.  |
| Sign in again to continue. Nothing was changed.  |
|                                                  |
| Tip: if this happens about every 7 days, see the |
| README section on the consent screen status.     |
|                                                  |
|                     [ Sign in ]  [ Not now ]     |  primary, secondary
+--------------------------------------------------+
```
Variant `denied` (user chose Deny or closed Google's page): title `Sign-in was not completed`; body `Google did not give this app access, so nothing was downloaded. You can try again whenever you are ready.`; buttons `[ Try again ]` `[ Close ]`. The stale token is removed by the app before this dialog opens (FR-003). Esc = Not now / Close.

## DLG-03 Download history cannot be read (blocks the run or dry run)
```
+--------------------------------------------------+
| Download history cannot be read                  |
|                                                  |
| .manifest.json in your output folder cannot be   |
| read. To protect your saved files, nothing was   |
| downloaded and the file was not changed.         |
|                                                  |
| What to do: restore it from a backup, or choose  |
| a new output folder. If you move or delete the   |
| file instead, every PDF in this folder is        |
| downloaded again with _1, _2 ... endings.        |
| See the README section "Download history".       |
|                                                  |
| Folder: C:\Users\you\Downloads\Gmail PDFs        |
|                                                  |
|        [ Open output folder ]  [ Show details ]  |  both secondary
|                                       [ Close ]  |  primary
+--------------------------------------------------+
```
Esc = Close. Focus starts on `Close`.

## DLG-04 Folder already has PDFs but no download history (confirm, real run only)
```
+--------------------------------------------------+
| This folder already has PDFs                     |
|                                                  |
| The output folder contains 42 PDFs saved by date |
| but has no download history file. If you       |
| continue, every PDF is saved again, and names    |
| that match get a _1, _2 ... ending. Existing     |
| files are never replaced. To avoid this, choose  |
| a new output folder.                             |
|                                                  |
| [ Choose another folder ] [ Continue ] [ Cancel ]|  primary, secondary, secondary
+--------------------------------------------------+
```
`Choose another folder` is the primary (safe) action and takes initial focus; it closes the dialog and focuses the Output folder field's `Browse...` button. `Continue` starts the run. Esc = Cancel (nothing starts). On a dry run this is not a dialog: it is notice MW-1 in SCR-04.

## DLG-05 Error details (opened from `Show details`)
```
+--------------------------------------------------+
| Details                                          |
| +----------------------------------------------+ |
| | Run 20260115_101500, version 0.0             | |
| | Step: download attachment                    | |
| | Message: Gmail returned an error (HTTP 503)  | |
| | after 6 attempts.                            | |
| +----------------------------------------------+ |
| This text contains no passwords or tokens, so    |
| it is safe to share.                             |
|                                                  |
|                     [ Copy details ]  [ Close ]  |  secondary, primary
+--------------------------------------------------+
```
Text box is read-only, selectable and focusable (scrolls with arrow keys). Content passes the same redaction as the log (FR-005). Esc = Close. After Copy the button label becomes `Copied` for 2 s and a status-bar message is announced.

## DLG-06 Close while a run is in progress
```
+--------------------------------------------------+
| Stop the run and close?                          |
|                                                  |
| A run is still in progress. If you close now,    |
| the app finishes the current file, saves your    |
| progress and then closes. A later run carries on |
| from here.                                       |
|                                                  |
|                [ Keep running ] [ Stop and close ]|  primary, secondary
+--------------------------------------------------+
```
Esc = Keep running. After `Stop and close` the window shows `Stopping...` and closes when the run has ended (NFR-004: within 5 s).

## DLG-07 Google setup help (from Help button or F1)
Same content and layout as W-03's step list (shared component `SetupSteps`), in a scrollable dialog 560 wide, title `Set up Google access`, buttons `[ Open Google Cloud Console ]` (secondary) `[ Close ]` (primary). Also contains, below the steps, the subheading `Remove access later` with: `In your Google Account, open Security, then Third-party apps with account access, and remove this app. Then delete the token file in the folder above.` (RD 2.1). Esc = Close.

## DLG-08 (R3) Sign out
```
+--------------------------------------------------+
| Sign out of Google?                              |
|                                                  |
| This removes the saved sign-in from this         |
| computer. Your downloaded files are not touched. |
| To also remove the app's access, open your Google|
| Account, then Security, then Third-party apps    |
| with account access, and remove this app.        |
|                                                  |
|                  [ Sign out ]  [ Cancel ]        |  destructive, secondary
+--------------------------------------------------+
```
The destructive variant appears only here and in the R3 flow; Esc = Cancel; focus starts on `Cancel`.

## SCR-07 (R3) Advanced settings (dialog, from header `Advanced` menu entry)
```
+------------------------------------------------------+
| Advanced settings                                    |
| Credentials file                                     |
| [C:\Users\you\...\credentials.json   ] [Browse...]   |
| Token file                                           |
| [C:\Users\you\...\token.json         ] [Browse...]   |
| Log level   [INFO                                  v]|
| These settings match the CLI options and environment |
| variables of the same name.                          |
|                              [ Save ]  [ Cancel ]    |
+------------------------------------------------------+
```
Fields: credentials path (must be an existing file: `Choose a file that exists.`), token path (parent folder must exist: `Choose a folder that exists.`), log level (DEBUG, INFO, WARNING, ERROR; default INFO). Specified at outline level only; the full state table is added when R3 is planned (FR-061).
