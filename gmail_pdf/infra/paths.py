"""Private folders and files for secret-bearing data, and the token-location notice.

Implements the file-protection rules of architecture 8.2 and ADR-003 decision 1:

* On POSIX the secrets folder is ``0700`` and every file written here is ``0600``.
* On Windows no ACL call is made: the folder inherits the ACL of the user profile it lives in,
  and a token path outside the profile only produces a ``TOKEN_OUTSIDE_PROFILE`` warning.
* ``write_private_text`` replaces the target atomically (temp file in the same folder, then
  ``os.replace``). That is the one permitted use of ``os.replace`` for the token file
  (coding-standards 10, decision D-32): the token is app-owned state, not a user-visible file.

All OS-specific branching in this story is in this module (NFR-020).
"""

from __future__ import annotations

import logging
import os
import secrets
from pathlib import Path

from gmail_pdf.domain import events
from gmail_pdf.domain.errors import PrivateFileError

logger = logging.getLogger(__name__)

DIR_MODE = 0o700
FILE_MODE = 0o600

# Mode bits mean nothing on Windows; there the profile ACL is the protection (no ACL calls).
_APPLY_POSIX_MODES = os.name == "posix"

# Windows opens file descriptors in text mode unless told otherwise; 0 elsewhere.
_O_BINARY = getattr(os, "O_BINARY", 0)

_TEMP_TOKEN_BYTES = 8

_DIR_ERROR = "The private folder could not be created or protected."
_WRITE_ERROR = "The private file could not be written; the previous file was left unchanged."
_ENCODE_ERROR = "The private file text could not be encoded as UTF-8."


def ensure_private_dir(path: Path) -> Path:
    """Create ``path`` (and missing parents) if needed and make it owner-only on POSIX.

    The mode is re-asserted even when the folder already exists, so a folder created earlier
    with a wider mode is tightened. Missing parent folders keep the default mode.

    Args:
        path: The folder to create, for example ``<root>/secrets``.

    Returns:
        ``path``, for chaining.

    Raises:
        PrivateFileError: The folder could not be created or its mode could not be set.
    """
    try:
        path.mkdir(mode=DIR_MODE, parents=True, exist_ok=True)
        if _APPLY_POSIX_MODES:
            os.chmod(path, DIR_MODE)
    except OSError as exc:
        raise PrivateFileError(_DIR_ERROR) from exc
    return path


def write_private_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` as UTF-8, owner-only, replacing any existing file atomically.

    The text goes to a uniquely named temp file in the same folder (created exclusively with
    mode ``0600``), is flushed to disk, and then moved over ``path`` with ``os.replace``. If any
    step fails, ``path`` keeps its previous content and the temp file is removed on a best-effort
    basis. The parent folder must already exist (see ``ensure_private_dir``).

    For app-owned state only (the token; the manifest snapshot in its own module). Never use it
    for a user-visible file: those use the no-clobber move or exclusive create, because the
    standards forbid overwriting them (coding-standards 10, decision D-32).

    Args:
        path: The target file, for example ``<root>/secrets/token.json``.
        text: The file content. It is never included in an error message.

    Raises:
        PrivateFileError: The text could not be encoded, or the file could not be written.
    """
    try:
        data = text.encode("utf-8")
    except UnicodeEncodeError:
        # ``from None``: the chained error would quote the offending part of the text.
        raise PrivateFileError(_ENCODE_ERROR) from None

    temp = path.with_name(f".{path.name}.{secrets.token_hex(_TEMP_TOKEN_BYTES)}.tmp")
    try:
        _write_temp_file(temp, data)
        if _APPLY_POSIX_MODES:
            os.chmod(temp, FILE_MODE)
        os.replace(temp, path)
    except OSError as exc:
        _discard(temp)
        raise PrivateFileError(_WRITE_ERROR) from exc


def token_location_warning(path: Path, home: Path) -> events.Warning | None:
    """Return a ``TOKEN_OUTSIDE_PROFILE`` warning if ``path`` is not inside ``home``.

    Both paths are resolved first, so ``..`` segments and symlinks are followed, and the
    comparison uses the platform's own path rules (case-insensitive on Windows). This is a
    notice only: it never raises and the caller never blocks on it (decision D-23). A path that
    cannot be judged at all (for example one with an embedded NUL character) is reported as
    outside the profile, so the user is told rather than the program failing.

    Args:
        path: The token file location in use.
        home: The user's profile folder, normally ``Path.home()``.

    Returns:
        ``None`` when ``path`` is inside ``home``; otherwise the warning event.
    """
    try:
        inside = _resolved(path).is_relative_to(_resolved(home))
    except (ValueError, OSError, RuntimeError):
        # Unclassifiable input (NUL character, unusable component): fail safe by warning.
        inside = False
    if inside:
        return None
    return events.Warning(events.WarningCode.TOKEN_OUTSIDE_PROFILE)


def _write_temp_file(temp: Path, data: bytes) -> None:
    """Create ``temp`` exclusively with mode ``0600``, write ``data`` and flush it to disk."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | _O_BINARY
    descriptor = os.open(temp, flags, FILE_MODE)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def _discard(temp: Path) -> None:
    """Remove a leftover temp file; a failure is logged (path only) and never masks the cause."""
    try:
        temp.unlink(missing_ok=True)
    except OSError:
        logger.warning("Could not remove temporary file %s", temp)


def _resolved(path: Path) -> Path:
    """Absolute path with ``..`` and symlinks resolved, falling back to a purely lexical form."""
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        # Unreadable component or a symlink loop: the lexical form is the best that is left.
        return Path(os.path.abspath(path))
