#!/usr/bin/env python3
"""Unit tests for `design/spice_text.py` -- the one shared SPICE
continuation joiner and `.SUBCKT` pin-list reader, plus a check that every
reader built on it (`floorplan_netlist`, `floorplan`, `digital/lvs`) agrees
on a header with an interleaved `*` comment."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
for sub in ("", "design"):
    path = str(REPO_ROOT / sub) if sub else str(REPO_ROOT)
    if path not in sys.path:
        sys.path.insert(0, path)

from spice_text import join_spice_continuations, subckt_pins  # noqa: E402


class JoinSpiceContinuationsTests(unittest.TestCase):
    def test_folds_continuation_into_previous_line(self):
        text = ".SUBCKT top A B\n+ C D\n+ E\n.ENDS top"
        self.assertEqual(
            join_spice_continuations(text),
            ".SUBCKT top A B C D E\n.ENDS top",
        )

    def test_strips_whitespace_around_continuation_body(self):
        text = ".SUBCKT top A\n+    B   \n"
        self.assertEqual(
            join_spice_continuations(text), ".SUBCKT top A B\n"
        )

    def test_text_without_continuations_is_unchanged(self):
        text = "* comment\n.SUBCKT a A Z\n.ENDS a\n"
        self.assertEqual(join_spice_continuations(text), text)

    def test_comment_line_does_not_swallow_following_card(self):
        """A comment followed by an ordinary (non-`+`) line stays its own line."""
        text = ".SUBCKT a A\n* pin note\n.ENDS a"
        self.assertEqual(join_spice_continuations(text), text)

    def test_continuation_after_comment_continues_the_card(self):
        """SPICE dialects (HSPICE explicitly) allow a comment line between a
        card and its `+` continuation; the continuation still belongs to the
        card. The helper currently folds it into the comment instead, so the
        continued pins vanish. Latent today -- `klt extract` does not emit an
        interleaved comment -- (#387).
        """
        text = ".SUBCKT a A\n* note\n+ B C\n.ENDS a"
        self.assertEqual(
            join_spice_continuations(text),
            ".SUBCKT a A B C\n* note\n.ENDS a",
        )

    def test_leading_continuation_with_no_predecessor_is_kept(self):
        """Malformed input: a `+` on the very first line has nothing to join
        onto, so it is passed through rather than dropped or raising."""
        text = "+ orphan\n.SUBCKT a A\n"
        self.assertEqual(join_spice_continuations(text), text)

    def test_multiple_comments_between_card_and_continuation(self):
        text = ".SUBCKT a A\n* one\n* two\n+ B\n+ C\n.ENDS a"
        self.assertEqual(
            join_spice_continuations(text),
            ".SUBCKT a A B C\n* one\n* two\n.ENDS a",
        )

    def test_blank_line_is_not_a_comment(self):
        """A blank line is a (empty) card, so a `+` after it attaches there
        and the header is not extended."""
        text = ".SUBCKT a A\n\n+ B\n.ENDS a"
        self.assertEqual(
            join_spice_continuations(text), ".SUBCKT a A\n B\n.ENDS a"
        )

    def test_continuation_with_only_comments_before_is_kept(self):
        text = "* c\n+ orphan\n.SUBCKT a A"
        self.assertEqual(join_spice_continuations(text), text)

    def test_empty_text(self):
        self.assertEqual(join_spice_continuations(""), "")


class SubcktPinsTests(unittest.TestCase):
    def test_name_is_case_insensitive(self):
        self.assertEqual(subckt_pins(".subckt Top A B\n", "TOP"), ["A", "B"])

    def test_missing_header_is_none(self):
        self.assertIsNone(subckt_pins(".SUBCKT a A\n", "b"))

    def test_interleaved_comment_does_not_drop_pins(self):
        text = ".SUBCKT top A\n* note\n+ B C\n.ENDS top"
        self.assertEqual(subckt_pins(text, "top"), ["A", "B", "C"])


class ReadersAgreeTests(unittest.TestCase):
    def test_every_reader_agrees_on_interleaved_comment(self):
        import floorplan_netlist
        from layout.digital import lvs
        from layout.floorplan import floorplan

        text = ".SUBCKT top A\n* note\n+ B C\n.ENDS top\n"
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp) / "ref.spice"
            ref.write_text(text)
            expected = ["A", "B", "C"]
            self.assertEqual(subckt_pins(text, "top"), expected)
            # `relative_to(REPO_ROOT)` is only evaluated on error paths.
            self.assertEqual(floorplan_netlist.reference_top_pins(ref, "top"), expected)
            self.assertEqual(floorplan._reference_top_pins(ref, "top"), expected)
            self.assertEqual(lvs._library_cell_pins(ref, {"top"}), {"top": expected})


if __name__ == "__main__":
    unittest.main()
