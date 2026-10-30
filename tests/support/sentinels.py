"""Obviously fake secret values used to prove nothing leaks (NFR-012, NFR-015, test-strategy 6).

None of these is a real credential. They are unique and greppable so one assertion can prove
"0 occurrences" on any text surface.
"""

from __future__ import annotations

CLIENT_SECRET = "SENTINEL-CLIENT-SECRET-0001"
REFRESH_TOKEN = "SENTINEL-REFRESH-0001"
ACCESS_TOKEN = "ya29.SENTINEL0001"
# Matches a defence-in-depth pattern, never registered.
UNREGISTERED_GOCSPX = "GOCSPX-SENTINEL0001"
UNREGISTERED_REFRESH_SHAPE = "1//SENTINEL-REFRESH-SHAPE-0001"

# What the application registers when it loads credentials (architecture 8.4, item 1).
REGISTERED = (CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN)
# Every value the matrix must never see on any surface.
ALL = (*REGISTERED, UNREGISTERED_GOCSPX, UNREGISTERED_REFRESH_SHAPE)


def leaked(text: str) -> list[str]:
    """The sentinels that occur in ``text`` (empty when the surface is clean)."""
    return [value for value in ALL if value in text]
