#!/usr/bin/env python3
"""Unit tests for design/netlist.py's normalization. No PDK, no ngspice, no
xschem required -- these cover the pure text transforms only.

    python3 -m unittest discover -s sim/tests -v

Why these exist: ``design/netlist.py --check`` is the guard that ties every
``netlist.sha`` in ``sim/records/`` to the schematic it claims to come from.
That guard is only useful if it fires on circuit changes and *only* on
circuit changes. xschem's own continuation-line wrapping moved between 3.4.4
and 3.4.7, which made the guard fire on a byte difference that no SPICE
parser can even see, so the exporter now owns the wrapping. The invariant
worth testing is therefore: re-wrapping never changes the token stream.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "design"))

import netlist  # noqa: E402


DEVICE_LINE = (
    "XMpiA an a vdd vdd pfet_03v3 L=0.28u W=0.44u nf=1 "
    "ad='int((nf+1)/2) * W/nf * 0.18u' as='int((nf+2)/2) * W/nf * 0.18u' "
    "pd='2*int((nf+1)/2) * (W/nf + 0.18u)' ps='2*int((nf+2)/2) * (W/nf + 0.18u)' "
    "nrd='0.18u / W' nrs='0.18u / W' sa=0 sb=0 sd=0 m=1"
)


class TokenizerTests(unittest.TestCase):
    def test_quoted_expression_stays_one_token(self):
        """A quoted expression contains spaces; splitting inside it would
        emit a netlist that no longer parses."""
        tokens = netlist._tokens("XM d g s b nfet L=0.28u ad='int((nf+1)/2) * W/nf'")
        self.assertIn("ad='int((nf+1)/2) * W/nf'", tokens)
        self.assertEqual(tokens[0], "XM")
        self.assertEqual(len(tokens), 8)

    def test_plain_line_splits_on_whitespace(self):
        self.assertEqual(
            netlist._tokens("  .subckt   ro_stage a y  vddr vss "),
            [".subckt", "ro_stage", "a", "y", "vddr", "vss"],
        )

    def test_empty_line_has_no_tokens(self):
        self.assertEqual(netlist._tokens("   "), [])


class RewrapTests(unittest.TestCase):
    def test_rewrap_preserves_the_token_stream(self):
        """The property the staleness guard depends on: wrapping is
        cosmetic, so unwrapping a re-wrapped line must give the tokens
        back exactly."""
        wrapped = netlist._rewrap(DEVICE_LINE)
        self.assertGreater(len(wrapped), 1, "this line is long enough to wrap")
        rejoined = netlist._join_continuations(wrapped)
        self.assertEqual(len(rejoined), 1)
        self.assertEqual(netlist._tokens(rejoined[0]), netlist._tokens(DEVICE_LINE))

    def test_rewrap_respects_the_wrap_column(self):
        for line in netlist._rewrap(DEVICE_LINE):
            self.assertLessEqual(len(line), netlist.WRAP_COLUMN)

    def test_continuation_lines_carry_the_plus_marker(self):
        wrapped = netlist._rewrap(DEVICE_LINE)
        self.assertFalse(wrapped[0].startswith("+"))
        for line in wrapped[1:]:
            self.assertTrue(line.startswith("+ "))

    def test_short_line_is_left_alone(self):
        self.assertEqual(netlist._rewrap("xa1 ro1 ro2 xo vdd vss xor2"),
                         ["xa1 ro1 ro2 xo vdd vss xor2"])

    def test_oversized_token_is_not_split(self):
        """A single token longer than the column goes on its own line: the
        alternative is emitting a netlist that does not parse."""
        long_token = "ad='" + "1+" * 200 + "1'"
        wrapped = netlist._rewrap(f"XM d g s b nfet {long_token}")
        self.assertIn(f"+ {long_token}", wrapped)
        self.assertEqual(
            netlist._tokens(netlist._join_continuations(wrapped)[0]),
            netlist._tokens(f"XM d g s b nfet {long_token}"),
        )

    def test_wrapping_is_idempotent(self):
        once = netlist._rewrap(DEVICE_LINE)
        twice = netlist._rewrap(netlist._join_continuations(once)[0])
        self.assertEqual(once, twice)


class JoinContinuationTests(unittest.TestCase):
    def test_multiple_continuations_collapse_to_one_line(self):
        joined = netlist._join_continuations(
            ["XM d g s b nfet L=0.28u", "+ W=0.22u", "+ m=1", "Cld y vss 1f"]
        )
        self.assertEqual(joined, ["XM d g s b nfet L=0.28u W=0.22u m=1", "Cld y vss 1f"])

    def test_leading_continuation_without_a_predecessor_is_kept(self):
        self.assertEqual(netlist._join_continuations(["+ orphan"]), ["+ orphan"])


class NormalizeTests(unittest.TestCase):
    def test_top_subckt_wrapper_is_restored(self):
        out = netlist._normalize("**.subckt foo a b\nxa a b bar\n**.ends\n.end\n")
        self.assertIn(".subckt foo a b", out)
        self.assertIn(".ends", out)
        self.assertNotIn("**.subckt", out)
        self.assertNotIn("\n.end\n", out)

    def test_top_parameters_are_restored_on_the_subckt_line(self):
        """xschem drops a top schematic's own G {...} block, which would
        leave a parameterised top cell referencing undeclared names."""
        out = netlist._normalize(
            "**.subckt ro_meta_tap xin mo vddm vss\n"
            "xarb pa pb mq mqn vddm vss meta_arb cld=cld\n"
            "**.ends\n",
            "cta=2f ctb=2f cld=0.5f",
        )
        self.assertIn(".subckt ro_meta_tap xin mo vddm vss cta=2f ctb=2f cld=0.5f", out)

    def test_comments_are_not_rewrapped(self):
        comment = "* " + "x" * (netlist.WRAP_COLUMN + 40)
        out = netlist._normalize(comment + "\n")
        self.assertEqual(out.strip(), comment)


class SchematicParamsTests(unittest.TestCase):
    def test_reads_the_g_block_of_a_real_schematic(self):
        params = netlist._schematic_params(netlist.SCHEMATIC_DIR / "ro_meta_tap.sch")
        self.assertEqual(params, "cta=2f ctb=2f cld=0.5f")

    def test_empty_g_block_yields_no_parameters(self):
        params = netlist._schematic_params(netlist.SCHEMATIC_DIR / "ro_array_core.sch")
        self.assertEqual(params, "")


class TopCellTests(unittest.TestCase):
    def test_every_top_cell_has_a_schematic_and_a_committed_netlist(self):
        for top in netlist.TOP_CELLS:
            with self.subTest(top=top):
                self.assertTrue((netlist.SCHEMATIC_DIR / f"{top}.sch").is_file())
                self.assertTrue((netlist.DESIGN_DIR / f"{top}.spice").is_file())

    def test_committed_netlists_are_wrapped_to_the_canonical_column(self):
        """Cheap stand-in for `--check` on a machine with no xschem: a
        committed netlist that is not canonically wrapped cannot have come
        from the current exporter."""
        for top in netlist.TOP_CELLS:
            text = (netlist.DESIGN_DIR / f"{top}.spice").read_text()
            for lineno, line in enumerate(text.splitlines(), start=1):
                if line.startswith("*"):
                    continue
                with self.subTest(top=top, line=lineno):
                    self.assertLessEqual(len(line), netlist.WRAP_COLUMN)


if __name__ == "__main__":
    unittest.main()
