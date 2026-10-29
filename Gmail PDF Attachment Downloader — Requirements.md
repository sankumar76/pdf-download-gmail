# Gmail PDF Attachment Downloader — Requirements

Oct 28, 2026 · @Santhosh

## 1. Purpose and scope

Build a local command-line Python tool that downloads every PDF attachment from one Gmail account for a given date range, saves each as `YYYYMMDD_<original name>.pdf`, and never overwrites an existing file. Hand this document to Claude Code as the specification.

**In scope**

- Read-only access to one Gmail account (personal Gmail or Google Workspace).
- PDF attachments only, including PDFs nested inside multipart or forwarded messages.
- Filtering by an inclusive start and end date.
- Date-prefixed file names, numeric suffixes for name collisions, and a run log.

**Out of scope**

- Sending, deleting, labelling, or modifying any email.
- Links to PDFs hosted elsewhere (Google Drive links, download URLs in the body).
- Other file types (.docx, .xlsx, images).
- A graphical interface.

**Tech stack:** Python 3.10+, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`. No other third-party dependencies unless justified.

## 2. Secure Gmail access

Use the Gmail API with OAuth 2.0 and the read-only scope `https://www.googleapis.com/auth/gmail.readonly`. Your Gmail password is never given to Claude Code or stored by the tool; you approve access once in your browser, and you can revoke it at any time.

### 2.1 One-time setup (done by you, not by Claude Code)

1. Go to the Google Cloud Console and create a project, e.g. `gmail-pdf-downloader`.
2. Under **APIs & Services → Library**, enable the **Gmail API**.
3. Under **OAuth consent screen**, choose **External** (personal Gmail) or **Internal** (Workspace), fill in the app name and your email, and add your own Gmail address as a **Test user**.
4. Add the scope `gmail.readonly` only.
5. Under **Credentials → Create credentials → OAuth client ID**, choose application type **Desktop app**.
6. Download the JSON file, rename it `credentials.json`, and place it in the project's `secrets/` folder.
7. On first run, the tool opens a browser window; sign in and click **Allow**. The tool then saves `secrets/token.json` and refreshes it automatically afterwards.

To revoke access later: Google Account → **Security → Third-party apps with account access** → remove the app, then delete `token.json`.

### 2.2 Security requirements for the code

- **SEC-01** Request only `gmail.readonly`. Never request `gmail.modify`, `mail.google.com`, or send scopes.
- **SEC-02** Use `InstalledAppFlow.run_local_server(port=0)` from `google-auth-oauthlib` for the consent flow (loopback redirect on localhost). Do not use the deprecated out-of-band (copy-paste code) flow.
- **SEC-03** Read the credentials path and token path from config or environment variables (`GMAIL_CREDENTIALS_PATH`, `GMAIL_TOKEN_PATH`); default to `./secrets/`.
- **SEC-04** Create `secrets/` with permissions `700` and write `token.json` with `600` on macOS/Linux; on Windows, keep it inside the user profile.
- **SEC-05** Add `secrets/`, `*.json` credentials, `token.json`, `.env`, and the download folder to `.gitignore`. Never commit them.
- **SEC-06** Never print, log, or include in error messages the access token, refresh token, or client secret.
- **SEC-07** If the token is expired, refresh it; if refresh fails (revoked or `invalid_grant`), delete the stale token and re-run the consent flow with a clear message.
- **SEC-08** Claude Code must not read or open `credentials.json` or `token.json` contents during development; it should only reference their paths.
- **SEC-09** Sanitise every attachment file name before writing to disk (see FR-12) to prevent path traversal.

### 2.3 Alternatives (not the default)

| Option | When to use | Drawback |
| --- | --- | --- |
| OAuth 2.0 Desktop app (default) | Personal Gmail or Workspace, one user | One-time browser consent; test-mode tokens may expire after 7 days for External apps in Testing status |
| Service account + domain-wide delegation | Workspace admin pulling from many mailboxes | Needs admin approval; powerful key file that must be guarded |
| IMAP + 16-character App Password | API access blocked by policy | Needs 2-Step Verification; full mailbox access, no read-only scope; Workspace admins often disable it |

If the 7-day expiry is a problem, publish the consent screen to **In production** (unverified apps still work for your own account after a warning screen).

## 3. Inputs and configuration

The tool runs as `python gmail_pdf_downloader.py --start 2026-01-01 --end 2026-03-31`. Command-line flags override values in an optional `config.yaml` or `.env`.

| Parameter | Flag | Required | Default | Rule |
| --- | --- | --- | --- | --- |
| Start date | `--start` | Yes | — | `YYYY-MM-DD`, inclusive (from 00:00:00) |
| End date | `--end` | Yes | — | `YYYY-MM-DD`, inclusive (to 23:59:59) |
| Output folder | `--out` | No | `./downloads` | Created if missing |
| Time zone | `--tz` | No | System local zone | IANA name, e.g. `Asia/Kolkata`; used for the range and the file-name date |
| Extra Gmail query | `--query` | No | empty | Appended to the search, e.g. `from:billing@vendor.com` |
| Include Spam/Trash | `--include-spam-trash` | No | false | Passes `includeSpamTrash` to the API |
| Dry run | `--dry-run` | No | false | Lists what would be saved; writes nothing |
| Credentials path | `--credentials` / `GMAIL_CREDENTIALS_PATH` | No | `./secrets/credentials.json` |  |
| Token path | `--token` / `GMAIL_TOKEN_PATH` | No | `./secrets/token.json` |  |
| Log level | `--log-level` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

**Validation**

- Reject the run if `--start` is after `--end`, or if either date is malformed, with a one-line error and exit code 2.
- Warn (but continue) if `--end` is in the future.
- If `credentials.json` is missing, print the setup steps from section 2.1 and exit with code 3.

## 4. Functional requirements

### 4.1 Finding emails

- **FR-01** Convert the start date at 00:00:00 and the day after the end date at 00:00:00 in the chosen time zone to Unix epoch seconds.
- **FR-02** Search with `users.messages.list` using the query `has:attachment filename:pdf after:<start_epoch> before:<end_plus_1_epoch>` plus any `--query` text. Epoch seconds are used instead of `YYYY/MM/DD` because Gmail interprets calendar dates in Pacific time.
- **FR-03** Follow `nextPageToken` until all pages are read (`maxResults=500`).
- **FR-04** After fetching each message, re-check its `internalDate` against the range and skip any outside it (guards against search-index edge cases).
- **FR-05** Process messages oldest first by `internalDate`, then attachments in MIME part order, so suffix numbering is the same on every run.

### 4.2 Extracting PDFs

- **FR-06** Fetch each message with `users.messages.get(format="full")` and walk the MIME tree recursively, including nested `multipart/*` and attached `message/rfc822` (forwarded emails).
- **FR-07** Treat a part as a PDF if its `mimeType` is `application/pdf`, or its file name ends in `.pdf` (case-insensitive) with `mimeType` `application/octet-stream`.
- **FR-08** If the part has `body.attachmentId`, download it with `users.messages.attachments.get`; if it has inline `body.data`, use that. Decode with URL-safe base64.
- **FR-09** Confirm the decoded bytes start with `%PDF-`. If not, skip the part and log it as `NOT_A_PDF`.
- **FR-10** A PDF with no file name gets the name `attachment.pdf`.

### 4.3 File naming

- **FR-11** Name each file `YYYYMMDD_<original file name>`, where `YYYYMMDD` is the email's `internalDate` (the time Gmail received it) converted to the chosen time zone. Fall back to the `Date` header only if `internalDate` is missing.
- **FR-12** Sanitise the original name before adding the prefix: strip any folder path, replace `<>:"/\|?*` and control characters with `_`, collapse repeated spaces, trim leading/trailing dots and spaces, decode RFC 2047/2231-encoded names (e.g. `=?UTF-8?B?...?=`), keep Unicode letters, and force the extension to lower-case `.pdf`.
- **FR-13** Keep the full name within 200 characters by shortening the stem, never the date prefix, suffix, or extension.

### 4.4 Duplicate handling

- **FR-14** A duplicate is any target name that already exists in the output folder or was already assigned earlier in the same run. Compare case-insensitively, because Windows and macOS file systems are case-insensitive.
- **FR-15** On a duplicate, insert `_1` before `.pdf`; if that also exists, try `_2`, `_3`, and so on until a free name is found. The first file keeps the plain name with no suffix.
- **FR-16** Never overwrite an existing file. Write to a temporary file in the output folder, then rename it atomically into place.
- **FR-17** Keep a manifest (`downloads/.manifest.json`) keyed by Gmail `messageId` + MIME `partId`. On a re-run, skip attachments already in the manifest so the same file is not saved again as `_1`. (Gmail's `attachmentId` changes between requests, so it is not used as the key.)
- **FR-18** Different files with the same name are both kept. Byte-identical PDFs from different emails are also both kept by default; an optional `--skip-identical` flag may skip a file whose SHA-256 already exists in the manifest.

**Example** (output folder starts empty; emails processed oldest first)

| Email received | Attachment name | Saved as | Reason |
| --- | --- | --- | --- |
| 15 Jan 2026 | Invoice.pdf | `20260115_Invoice.pdf` | First occurrence |
| 15 Jan 2026 | Invoice.pdf | `20260115_Invoice_1.pdf` | Same name, same day |
| 15 Jan 2026 | invoice.PDF | `20260115_invoice_2.pdf` | Case-insensitive match; extension lower-cased |
| 16 Jan 2026 | Invoice.pdf | `20260116_Invoice.pdf` | Different date, so no clash |
| 20 Jan 2026 | ../../Report:Q4.pdf | `20260120_Report_Q4.pdf` | Path stripped and `:` replaced |
| 21 Jan 2026 | (no name) | `20260121_attachment.pdf` | Default name |

## 5. Reliability, logging and edge cases

### 5.1 Reliability

- **NFR-01** Retry HTTP 429 and 5xx errors with exponential backoff and jitter (start 1 s, max 64 s, 6 attempts), honouring `Retry-After` when present.
- **NFR-02** One failed message or attachment must not stop the run; log it and continue.
- **NFR-03** Ctrl+C stops cleanly: finish or discard the current temp file, save the manifest, and print the summary.
- **NFR-04** Use batch requests or a small thread pool (max 4 workers) for `messages.get` only if needed for speed; file-name assignment must stay single-threaded so suffixes are deterministic.
- **NFR-05** Keep memory bounded: process one message at a time and stream each PDF to disk; attachments up to Gmail's 25 MB limit must work.

### 5.2 Logging and output

- **LOG-01** Write a log to `downloads/logs/run_<YYYYMMDD_HHMMSS>.log` and a CSV report `downloads/logs/report_<YYYYMMDD_HHMMSS>.csv`.
- **LOG-02** CSV columns: `status`, `saved_file`, `original_name`, `email_date`, `from`, `subject`, `message_id`, `part_id`, `size_bytes`, `sha256`.
- **LOG-03** Status values: `SAVED`, `SAVED_RENAMED` (suffix added), `SKIPPED_ALREADY_DOWNLOADED`, `SKIPPED_IDENTICAL`, `NOT_A_PDF`, `ERROR`.
- **LOG-04** End the run with a console summary: messages scanned, PDFs saved, renamed, skipped, errors, total size, elapsed time.
- **LOG-05** Exit code 0 on success, 1 if any attachment errored, 2 for bad arguments, 3 for missing credentials or failed authentication.

### 5.3 Edge cases to handle

- A message with several PDFs: all are saved.
- The same PDF in several messages of one thread: each message's copy is saved (subject to `--skip-identical`).
- Password-protected or corrupt PDFs: saved as-is; only the `%PDF-` header is checked.
- Google Drive attachments (shown as links, not real attachments): not downloaded, out of scope.
- Emails in Spam or Trash: excluded unless `--include-spam-trash` is set.
- A date range with no matches: exit 0 with "0 PDFs found".
- Very large mailboxes (10,000+ matches): pagination and the manifest must allow a stopped run to resume.

## 6. Deliverables, acceptance criteria and handoff

### 6.1 Deliverables

```
gmail-pdf-downloader/
├── gmail_pdf_downloader.py   # CLI entry point
├── gmail_pdf/
│   ├── auth.py               # OAuth flow, token load/refresh
│   ├── search.py             # query building, pagination
│   ├── extract.py            # MIME walk, PDF detection, decode
│   ├── naming.py             # sanitise, date prefix, suffixes
│   └── manifest.py           # resume / skip logic
├── tests/                    # pytest, Gmail API mocked
├── requirements.txt          # pinned versions
├── config.example.yaml
├── .gitignore                # includes secrets/ and downloads/
└── README.md                 # setup (section 2.1) and usage
```

### 6.2 Acceptance criteria

- [ ] First run opens the browser consent screen requesting read-only Gmail access only; later runs need no browser.
- [ ] Only PDFs from emails received within the inclusive date range (in the chosen time zone) are saved.
- [ ] Every file name starts with the email's date as `YYYYMMDD_`.
- [ ] Name collisions produce `_1`, `_2`, … in sequence, matching the example table in section 4.4; nothing is ever overwritten.
- [ ] Re-running the same range saves 0 new files and reports them as `SKIPPED_ALREADY_DOWNLOADED`.
- [ ] Malicious names such as `../../x.pdf` are written inside the output folder only.
- [ ] No token, secret, or credential appears in logs, console output, or the repository.
- [ ] Unit tests cover naming, sanitising, suffix sequencing, date-range boundaries (23:59 on the end date included, 00:00 the next day excluded), nested MIME parts, and non-PDF rejection; all pass with `pytest`.
- [ ] `--dry-run` lists planned file names and writes no PDFs.

### 6.3 Prompt to give Claude Code

Paste this along with the document (exported as Markdown):

```
Read REQUIREMENTS.md and build the Gmail PDF downloader it specifies.
Work in this order: auth.py, then naming.py with its tests, then search/extract,
then manifest, then the CLI and README. Run pytest after each module.
Do not open or print the contents of anything in secrets/.
When done, show me the exact command to run a dry run for 2026-01-01 to 2026-01-31.
```

**Before the first real run:** complete section 2.1, put `credentials.json` in `secrets/`, and try `--dry-run` on a one-week range.
