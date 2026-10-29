# Coding Standards

> **Customise this file for your company.** It is the rule-book reviewer-standards
> enforces and the developer follows. Keep the section headings; replace or extend the
> rules. Language-specific sections marked `<<...>>` should be completed per stack.

## 1. General Principles
- Readability over cleverness. Code is read far more often than it is written.
- Single Responsibility: a function does one thing; a module has one reason to change.
- Small units: functions ≤ 40 lines, files ≤ 400 lines, cyclomatic complexity ≤ 10 (justify exceptions inline).
- DRY, but prefer duplication over the wrong abstraction (rule of three).
- Fail fast and loudly at boundaries; never swallow exceptions silently.
- No magic numbers or strings — use named constants or configuration.

## 2. Naming
- Names reveal intent; avoid abbreviations except widely known ones (`id`, `url`, `http`).
- Booleans read as predicates: `isActive`, `hasAccess`, `shouldRetry`.
- Functions are verbs (`calculateTotal`), classes/types are nouns (`InvoiceRepository`).
- <<Casing conventions per language, e.g. camelCase for TS variables, PascalCase for types, snake_case for Python, kebab-case for file names>>

## 3. Structure & Architecture
- Follow the layering and source tree defined in `docs/04-architecture/architecture.md`.
- Dependencies point inward (domain must not import infrastructure/UI).
- No business logic in controllers/handlers or UI components.
- Cross-cutting concerns (logging, auth, validation) use the shared modules — do not re-implement.

## 4. Error Handling & Logging
- Use the project's error types; include actionable context, never sensitive data.
- Log at the right level: `error` (needs action), `warn` (degraded), `info` (business events), `debug` (diagnostics).
- Structured logs with correlation/request IDs. Never log secrets, tokens, passwords or PII.

## 5. Security (baseline — OWASP ASVS L1 minimum)
- Validate and sanitise all external input at the boundary; use allow-lists.
- Parameterised queries only; no string-built SQL/NoSQL/shell commands.
- Encode output for its context (HTML, URL, JS, SQL).
- AuthN/AuthZ checks on every protected operation; deny by default.
- Secrets come from the secrets manager / environment — never committed.
- Dependencies: no new library without architect approval (licence + vulnerability check).

## 6. Testing
- Test pyramid: many unit, fewer integration, few end-to-end.
- Tests are deterministic, isolated, and fast; no network calls in unit tests.
- Arrange–Act–Assert structure; one behaviour per test; descriptive names
  (`should_reject_expired_token_when_validating`).
- Test data via builders/factories; no real personal data.
- Coverage thresholds (industry default, e.g. SonarQube "Sonar way" gate): ≥ 80% on changed code
  in every PR, and ≥ 80% for the whole package.

## 7. Performance
- Avoid N+1 queries; batch and paginate; index columns used in filters/joins.
- No unbounded loops/collections over external data; stream large payloads.
- Cache only with a defined invalidation strategy and TTL.

## 8. Documentation
- Public functions/classes have doc comments describing purpose, params, returns, errors.
- Comments explain *why*, not *what*.
- ADR for every significant or hard-to-reverse technical decision.

## 9. Version Control
- Branch: `feat/<story-id>-short-name`, `fix/<defect-id>-short-name`.
- Commits: Conventional Commits (`feat(auth): add token refresh [STORY-02.04]`).
- One logical change per commit; no generated artefacts or secrets committed.

## 10. Language-Specific Rules
### Python 3.12 (min 3.10)
- Type hints on every function and return value; `mypy --strict` clean; no `Any` or `# type: ignore` without an inline justification
- Use `pathlib.Path` for all paths, never string concatenation; `zoneinfo.ZoneInfo` for time zones, never naive `datetime`
- Prefer `@dataclass(frozen=True)` for records (e.g. attachment metadata); no mutable default arguments
- Use `logging` (module-level `logger = logging.getLogger(__name__)`), never `print`, except the final console summary
- Catch specific exceptions only (`HttpError`, `OSError`, `binascii.Error`); no bare `except:`; never swallow errors silently
- Small pure functions for naming, sanitising and date logic so they are unit-testable without the Gmail API
- Docstrings on public functions (Google style); max line length 100; f-strings for formatting
### Gmail API
- Request only the `gmail.readonly` scope; never call modify, delete, send or label endpoints
- Build the client once and reuse it; wrap every API call in the shared retry/backoff helper (429 and 5xx)
- Always follow `nextPageToken`; use `messageId` + `partId` as attachment identity, never `attachmentId`
- Mock the API in tests (no live Gmail calls in CI); keep sample MIME payloads in `tests/fixtures/`
### Files and secrets
- Never read, print or log the contents of `secrets/`; log token *paths* only
- Never overwrite an existing file. If the target name already exists, save as `<name>_1.pdf`,
  `<name>_2.pdf`, … (first free number), using a no-clobber move so this holds even if a file
  appears during the run. `os.replace` is allowed only for the app's own state files (manifest, token)
- Sanitise every external file name before it touches the file system; reject anything that resolves outside the output folder
- `secrets/`, `downloads/`, `.env` and `token.json` must be in `.gitignore`

## 11. Tooling (must pass in CI)
- Formatter: ruff format (`ruff format --check .`)
- Linter: ruff (`ruff check .`, rule sets E, F, I, B, UP, S, SIM) — zero errors, warnings justified
- Type checker: mypy (`mypy gmail_pdf --strict`)
- Security scan: pip-audit (dependency CVEs) + bandit (`bandit -r gmail_pdf`) for code issues; gitleaks to block committed secrets
