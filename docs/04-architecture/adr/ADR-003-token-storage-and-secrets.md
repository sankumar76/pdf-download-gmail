# ADR-003: OAuth token storage, default paths and the single redaction path

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-10-29 |
| Deciders | solution-architect |
| Related | SEC-01..09, FR-001..007, FR-061, NFR-011..013, NFR-015, RISK-003, RISK-005, RISK-009, PQ-03, ux-spec §0 (UA-02, UA-05) |

## Context
The RD specifies a `token.json` file (path from `--token`, `GMAIL_TOKEN_PATH`, default `./secrets/`), `0700`/`0600` on POSIX and "inside the user profile" on Windows. The token file written by `google.oauth2.credentials.Credentials.to_json()` contains the refresh token and the client secret (Restricted). The GUI is launched by double-click, so working-directory-relative defaults are unpredictable. RISK-005 demands one redacting error path for CLI and GUI.

## Decision Drivers
- RD contract (SEC-03/04), NFR-013 test-ability
- Least dependency (NFR-023)
- Zero leakage on every surface (FR-005, NFR-012)
- Same behaviour in CLI and GUI (FR-064)

## Considered Options
### Option A — Plain `token.json` protected by OS permissions (chosen)
- Pros: exactly the RD; works with `google-auth` file helpers; trivial to delete on `invalid_grant` or sign-out; testable.
- Cons: plaintext at rest; protection relies on the OS account.
### Option B — OS keyring (Windows Credential Manager via `keyring`)
- Pros: encrypted by the OS.
- Cons: new dependency with platform back-ends; conflicts with the RD's token path option and env var; harder to test in CI. Rejected.
### Option C — `token.json` encrypted with Windows DPAPI (`CryptProtectData` via `ctypes`)
- Pros: no dependency; encrypted per user on Windows.
- Cons: Windows-only branch; file no longer readable by `google-auth` helpers; POSIX still needs another approach. **Deferred** as tech-debt TD-01 (GitHub issue).

## Decision
1. **Storage:** Option A. Write via temp file + `os.replace` (the app owns this file). POSIX: directory `0700`, file opened with `os.open(path, O_WRONLY|O_CREAT|O_TRUNC, 0o600)`, then `chmod` re-asserted. Windows: default under the profile; if the resolved path is outside `Path.home()` → `Warning(TOKEN_OUTSIDE_PROFILE)`, not a block.
2. **Default paths:** CLI keeps RD defaults (`./secrets/credentials.json`, `./secrets/token.json`, `./downloads`). GUI uses `%LOCALAPPDATA%\GmailPdfDownloader\secrets\` (and XDG/Application Support equivalents) and `<Downloads known folder>\Gmail PDFs` (ux-spec UA-02). Precedence everywhere: explicit option/field > env var > default (`infra/paths.py`, one function).
3. **Scope:** a single constant `SCOPES = ("https://www.googleapis.com/auth/gmail.readonly",)`; a loaded token whose recorded scopes differ is discarded and consent re-run.
4. **Client file check (UA-05):** the app parses `credentials.json` structurally (JSON object with an `installed` key) before starting the flow; otherwise `BAD_CLIENT_FILE` with a fixed message. Contents are never logged or displayed.
5. **Refresh failure:** `google.auth.exceptions.RefreshError` → delete token, fixed reason text (revoked, or 7-day Testing expiry — RISK-003), restart consent (FR-003).
6. **Redaction (one path):** `gmail_pdf/redaction.py` — secret registry (values registered on load/refresh), token patterns as defence in depth, `logging.Filter` on every handler, `safe_message(exc)` for every user-visible error, `sys.excepthook`/`threading.excepthook`/Qt message handler. Third-party loggers capped at `WARNING`. No module may format a `Credentials` object, HTTP headers or request URIs.
7. **Sign-out (R3, FR-007):** delete the token file and show revoke steps; no call to the revocation endpoint (PD-04).

## Consequences
- Positive: RD-compatible, dependency-free, single tested redaction choke point.
- Negative: token plaintext at rest (TD-01). CLI and GUI use different default token locations; users who want one sign-in set the env vars (UX-I-04).
- Follow-up: developer implements `redaction.py` in W1 before any logging (release plan); qa-engineer owns the sentinel matrix.

## Verification
Sentinel-secret matrix over every error path and surface (test-strategy §6); POSIX permission test; Windows path test; `.gitignore` pattern test; gitleaks on every PR.
