"""Shared conformance corpus for the SPICE `+`-continuation readers.

The tree keeps several readers that fold `+` continuation lines, with
different return contracts (text, line lists, `(first line, text)` pairs,
header source indexes). The same defect -- a full-line `*` comment between a
card and its continuation swallowing the continued tokens -- was fixed in
three separate rounds (#1036, #1043, #1063), each found by a tree sweep.
This module feeds one set of small decks through every reader and pins each
reader's expected output explicitly, so the next divergence fails
`npm test` and names both the reader and the fixture.

Expected values are written out per reader, never derived from another
reader. A new folder added to the tree is not discovered automatically; wire
it in here. Offline: no ngspice, PDK or klt.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, ROOT / "sim", ROOT / "design"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from harness import pdk_models, testbench  # noqa: E402
from layout.floorplan import floorplan  # noqa: E402
from sim.tools import pex_dut  # noqa: E402
from sim.tools.pathload import load_module_from_path  # noqa: E402
from spice_text import join_spice_continuations  # noqa: E402

netlist = load_module_from_path("_conf_design_netlist", ROOT / "design" / "netlist.py")
pex_build = load_module_from_path("_conf_pex_build", ROOT / "layout" / "pex" / "build.py")


def norm(line: str) -> str:
    """Whitespace-only differences are not contract differences."""
    return " ".join(line.split())


def _text(text: str) -> list[str]:
    return [norm(x) for x in join_spice_continuations(text).split("\n")]


def _export(text: str) -> list[str]:
    return [norm(x) for x in netlist._join_continuations(text.split("\n"))]


def _pex_dut(text: str) -> list[str]:
    return [norm(x) for x in pex_dut.logical_lines(text)]


def _bench(text: str) -> list[tuple[int, str]]:
    return [(n, norm(x)) for n, x in testbench._logical_lines(text)]


def _pdk(text: str) -> list[tuple[int, str]]:
    return [(n, norm(x)) for n, x in pdk_models._logical_lines(text)]


def _header(text: str):
    toks, idx = pex_build._subckt_header(text, "dut")
    return toks, idx


def _floorplan(text: str) -> dict[str, list[str]]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "deck.spice"
        path.write_text(text)
        return {k: [norm(x) for x in v] for k, v in floorplan.read_subckts(path).items()}


# Deck from #1069: two comments between the card and its continuations.
DECK = ".subckt dut a\n* first\n* second\n+ b\n+ c\n.ends dut\n"
# Unsplit control.
CONTROL = ".subckt dut a\n+ b\n.ends dut\n"
# Blank line before the continuation.
BLANK = ".subckt dut a\n\n+ b\n.ends dut\n"
# Continuation with only comments before it (nothing to continue).
ORPHAN = "* c1\n* c2\n+ b\n.subckt dut a\n.ends dut\n"
# Indented comment and continuation markers.
INDENT = ".subckt dut a\n  * c\n  + b\n.ends dut\n"

# Each entry: reader -> (callable, expected). Lists are positional, so the
# header card's location is part of the expectation (index / first line).
READERS = {
    "join_spice_continuations": _text,
    "netlist._join_continuations": _export,
    "pex_dut.logical_lines": _pex_dut,
    "testbench._logical_lines": _bench,
    "pdk_models._logical_lines": _pdk,
}

EXPECTED = {
    "multi-comment": (DECK, {
        "join_spice_continuations": [".subckt dut a b c", "* first", "* second", ".ends dut", ""],
        "netlist._join_continuations": [".subckt dut a b c", "* first", "* second", ".ends dut", ""],
        "pex_dut.logical_lines": [".subckt dut a b c", "* first", "* second", ".ends dut"],
        "testbench._logical_lines": [(1, ".subckt dut a b c"), (6, ".ends dut")],
        "pdk_models._logical_lines": [
            (1, ".subckt dut a b c"), (2, "* first"), (3, "* second"), (6, ".ends dut"),
        ],
    }),
    "control": (CONTROL, {
        "join_spice_continuations": [".subckt dut a b", ".ends dut", ""],
        "netlist._join_continuations": [".subckt dut a b", ".ends dut", ""],
        "pex_dut.logical_lines": [".subckt dut a b", ".ends dut"],
        "testbench._logical_lines": [(1, ".subckt dut a b"), (3, ".ends dut")],
        "pdk_models._logical_lines": [(1, ".subckt dut a b"), (3, ".ends dut")],
    }),
    # A blank is a card for most readers (the `+` attaches to the blank, the
    # header stays `a`); the testbench reader skips blanks, so it folds.
    "blank-before-continuation": (BLANK, {
        "join_spice_continuations": [".subckt dut a", "b", ".ends dut", ""],
        "netlist._join_continuations": [".subckt dut a", "b", ".ends dut", ""],
        "pex_dut.logical_lines": [".subckt dut a", "b", ".ends dut"],
        "testbench._logical_lines": [(1, ".subckt dut a b"), (4, ".ends dut")],
        "pdk_models._logical_lines": [(1, ".subckt dut a"), (2, "b"), (4, ".ends dut")],
    }),
    # Nothing to continue: the `+` line survives as its own entry.
    "orphan-continuation": (ORPHAN, {
        "join_spice_continuations": ["* c1", "* c2", "+ b", ".subckt dut a", ".ends dut", ""],
        "netlist._join_continuations": ["* c1", "* c2", "+ b", ".subckt dut a", ".ends dut", ""],
        "pex_dut.logical_lines": ["* c1", "* c2", "+ b", ".subckt dut a", ".ends dut"],
        "testbench._logical_lines": [(3, "+ b"), (4, ".subckt dut a"), (5, ".ends dut")],
        "pdk_models._logical_lines": [
            (1, "* c1"), (2, "* c2"), (3, "+ b"), (4, ".subckt dut a"), (5, ".ends dut"),
        ],
    }),
    # Export and harness readers accept indented markers; the shared text
    # helper and the PEX reader only recognise column one.
    "indented-markers": (INDENT, {
        "join_spice_continuations": [".subckt dut a", "* c", "+ b", ".ends dut", ""],
        "netlist._join_continuations": [".subckt dut a b", "* c", ".ends dut", ""],
        "pex_dut.logical_lines": [".subckt dut a", "* c", "+ b", ".ends dut"],
        "testbench._logical_lines": [(1, ".subckt dut a b"), (4, ".ends dut")],
        "pdk_models._logical_lines": [(1, ".subckt dut a b"), (2, "* c"), (4, ".ends dut")],
    }),
}

# `layout.pex.build._subckt_header`: (port tokens, source line indexes).
# A blank line or a card ends the header; indented markers do not continue it.
HEADER_EXPECTED = {
    "multi-comment": (DECK, (["a", "b", "c"], [0, 3, 4])),
    "control": (CONTROL, (["a", "b"], [0, 1])),
    "blank-before-continuation": (BLANK, (["a"], [0])),
    "indented-markers": (INDENT, (["a"], [0])),
}

# `floorplan.read_subckts`: body lines (comments dropped), continuations joined.
FLOORPLAN_EXPECTED = {
    "multi-comment": (DECK, {"dut": ["a b c"]}),
    "control": (CONTROL, {"dut": ["a b"]}),
    "blank-before-continuation": (BLANK, {"dut": ["a", "b"]}),
    "indented-markers": (INDENT, {"dut": ["a", "+ b"]}),
}


class SpiceContinuationCorpusTests(unittest.TestCase):
    def test_line_readers(self):
        for fixture, (text, per_reader) in EXPECTED.items():
            for reader, expected in per_reader.items():
                with self.subTest(reader=reader, fixture=fixture):
                    self.assertEqual(READERS[reader](text), expected)

    def test_pex_header_scan(self):
        for fixture, (text, expected) in HEADER_EXPECTED.items():
            with self.subTest(reader="pex.build._subckt_header", fixture=fixture):
                self.assertEqual(_header(text), expected)

    def test_floorplan_inventory(self):
        for fixture, (text, expected) in FLOORPLAN_EXPECTED.items():
            with self.subTest(reader="floorplan.read_subckts", fixture=fixture):
                self.assertEqual(_floorplan(text), expected)

    def test_multi_comment_header_card_is_identified_first(self):
        """The header tokens are asserted on the card, located before tokenizing."""
        cards = {
            "join_spice_continuations": _text(DECK)[0],
            "netlist._join_continuations": _export(DECK)[0],
            "pex_dut.logical_lines": _pex_dut(DECK)[0],
            "testbench._logical_lines": _bench(DECK)[0][1],
            "pdk_models._logical_lines": _pdk(DECK)[0][1],
        }
        for reader, card in cards.items():
            with self.subTest(reader=reader, fixture="multi-comment"):
                self.assertTrue(card.startswith(".subckt dut"))
                self.assertEqual(card.split()[2:], ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
