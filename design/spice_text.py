"""Plain-text readers for SPICE netlists: the single home of the
`+`-continuation joiner and the `.SUBCKT` header matcher.

Stdlib-only, so any tool (`design/floorplan_netlist.py`,
`layout/floorplan/floorplan.py`, `layout/digital/lvs.py`) can import it
without pulling in the rest of the design tree.
"""

from __future__ import annotations

import re

#: Matches a `.SUBCKT <name> <pins...>` header line. SPICE keywords are
#: case-insensitive, so this is too; compare names with `.lower()` or exactly,
#: as the caller needs.
SUBCKT_HEADER_RE = re.compile(r"^\.subckt\s+(\S+)\s+(.*)$", re.MULTILINE | re.IGNORECASE)


def join_spice_continuations(text: str) -> str:
    """Fold every SPICE `+`-prefixed continuation line into its card.

    A continuation attaches to the last non-comment line, so `*` comment
    lines between a card and its `+` line are left in place and do not
    swallow the continued tokens (HSPICE-style). A blank line is not a
    comment: a `+` after one attaches to the blank line. A `+` with no
    earlier non-comment line (start of file, or only comments before it)
    has nothing to continue and is passed through unchanged.
    """
    joined: list[str] = []
    card: int | None = None  # index in `joined` of the last non-comment line
    for line in text.split("\n"):
        if line.startswith("+") and card is not None:
            joined[card] = f"{joined[card]} {line[1:].strip()}"
            continue
        joined.append(line)
        if not line.startswith("*"):
            card = len(joined) - 1
    return "\n".join(joined)


def subckt_pins(text: str, top: str) -> list[str] | None:
    """The pin list off `text`'s `.SUBCKT <top> ...` header (name matched
    case-insensitively, continuations joined first), or None if absent."""
    for name, pins in SUBCKT_HEADER_RE.findall(join_spice_continuations(text)):
        if name.lower() == top.lower():
            return pins.split()
    return None
