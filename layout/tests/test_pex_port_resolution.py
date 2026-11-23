#!/usr/bin/env python3
"""Unit tests for `layout/pex/build.py`'s port-resolution and tap-position
helpers (issue #390).

`layout/pex/build.py` turns raw `klt extract` output into the routed and
noise-tapped `.SUBCKT` decks the post-layout re-sims consume. The helpers
tested here decide *which* extracted pin becomes *which* named port. A mistake
in any of them does not crash -- it silently simulates a different circuit --
so each test below pins either a correct resolution or a refusal to guess:

1. `_match_positional` -- picks exactly one same-named net by drawn label
   position (within `_POS_TOL_UM`), and raises `FlowError` on zero or several
   matches.
2. `_tap_positions` -- returns exactly eleven tappable header positions after
   skipping the ring's four non-signal ports, else raises.
3. `_gate_nodes` -- returns each `nfet_03v3`/`pfet_03v3` card's gate node, and
   raises on a short card, a foreign model, or no cards at all.
4. `_positional_args` / `_ntap_port_order` -- identified positions keep their
   names, the rest get `n1, n2, ...`; in the tapped port order `ro` is listed
   once (only its `__rx` partner, since `ro` is already a base port) while
   every other tapped net appears with its `__rx` partner.

All inputs are synthetic payload dicts and netlist text: no `klt`, no PDK, no
committed artefact is read or written. `test_pex_noise_tap.py` and
`test_pex_fullchip.py` cover the rest of the module.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent

sys.path.insert(0, str(REPO_ROOT))

from layout.pex.build import (  # noqa: E402
    FlowError,
    _gate_nodes,
    _noise_tapped,
    _subckt_header,
    _match_positional,
    _ntap_port_order,
    _positional_args,
    _tap_positions,
)

#: Kept literal rather than imported from `layout/pex/build.py`, the same
#: convention `test_pex_noise_tap.py` follows: importing the module's own
#: constants would let a change to them pass unnoticed here.
POS_TOL_UM = 0.02
TAP_COUNT = 11
NON_SIGNAL_PORTS = ("en", "vddr", "vss")


def _net(pin_index: int, name: str, **labels: tuple[float, float]) -> dict:
    """One `nets[]` entry as `klt extract` reports it, reduced to the fields
    `_match_positional` reads."""
    return {
        "pin_index": pin_index,
        "name": name,
        "label_positions_um": [
            {"text": text, "x_um": x, "y_um": y} for text, (x, y) in labels.items()
        ],
    }


class MatchPositionalTests(unittest.TestCase):
    """`_match_positional`: positive identification among same-named nets."""

    def test_single_match_returns_its_pin_index(self):
        groups = {"a|y": [_net(7, "a|y", a=(1.0, 2.0), y=(30.0, 2.0))]}
        self.assertEqual(
            _match_positional(groups, "a|y", {"a": (1.0, 2.0), "y": (30.0, 2.0)}), 7
        )

    def test_same_named_nets_resolve_by_label_position(self):
        groups = {
            "q": [
                _net(3, "q", q=(10.0, 5.0)),
                _net(9, "q", q=(40.0, 5.0)),
            ]
        }
        self.assertEqual(_match_positional(groups, "q", {"q": (10.0, 5.0)}), 3)
        self.assertEqual(_match_positional(groups, "q", {"q": (40.0, 5.0)}), 9)

    def test_every_expected_label_must_match(self):
        # Same `a` position on both; only `y` tells them apart.
        groups = {
            "a|y": [
                _net(1, "a|y", a=(1.0, 2.0), y=(20.0, 2.0)),
                _net(2, "a|y", a=(1.0, 2.0), y=(30.0, 2.0)),
            ]
        }
        self.assertEqual(
            _match_positional(groups, "a|y", {"a": (1.0, 2.0), "y": (30.0, 2.0)}), 2
        )

    def test_zero_matches_raises(self):
        groups = {"q": [_net(3, "q", q=(10.0, 5.0))]}
        with self.assertRaises(FlowError):
            _match_positional(groups, "q", {"q": (99.0, 5.0)})

    def test_unknown_name_raises(self):
        with self.assertRaises(FlowError):
            _match_positional({}, "q", {"q": (10.0, 5.0)})

    def test_two_matches_raise(self):
        groups = {
            "q": [
                _net(3, "q", q=(10.0, 5.0)),
                _net(9, "q", q=(10.0, 5.0)),
            ]
        }
        with self.assertRaises(FlowError):
            _match_positional(groups, "q", {"q": (10.0, 5.0)})

    def test_position_within_tolerance_matches(self):
        groups = {"q": [_net(3, "q", q=(10.0 + POS_TOL_UM / 2, 5.0 - POS_TOL_UM / 2))]}
        self.assertEqual(_match_positional(groups, "q", {"q": (10.0, 5.0)}), 3)

    def test_position_beyond_tolerance_does_not_match(self):
        off = 1.5 * POS_TOL_UM
        for dx, dy in ((off, 0.0), (0.0, off), (-off, 0.0), (0.0, -off)):
            with self.subTest(dx=dx, dy=dy):
                groups = {"q": [_net(3, "q", q=(10.0 + dx, 5.0 + dy))]}
                with self.assertRaises(FlowError):
                    _match_positional(groups, "q", {"q": (10.0, 5.0)})

    def test_missing_expected_label_does_not_match(self):
        groups = {"a|y": [_net(1, "a|y", a=(1.0, 2.0))]}
        with self.assertRaises(FlowError):
            _match_positional(groups, "a|y", {"a": (1.0, 2.0), "y": (30.0, 2.0)})


def _ring_port_map(pin_count: int = 14) -> dict[int, str]:
    """A resolved ring port map with the three non-signal ports and `ro`
    scattered through the header, the way flat extraction orders them."""
    return {0: "en", 3: "ro", 6: "vddr", 10: "vss"}


class TapPositionsTests(unittest.TestCase):
    """`_tap_positions`: eleven ring nets, non-signal ports skipped."""

    def test_fourteen_pins_yield_eleven_positions(self):
        port_map = _ring_port_map(14)
        positions = _tap_positions(14, port_map)
        self.assertEqual(len(positions), TAP_COUNT)
        self.assertEqual(positions, [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13])

    def test_non_signal_ports_are_skipped_and_ro_is_kept(self):
        port_map = _ring_port_map(14)
        positions = _tap_positions(14, port_map)
        for idx, name in port_map.items():
            with self.subTest(name=name):
                if name in NON_SIGNAL_PORTS:
                    self.assertNotIn(idx, positions)
                else:
                    self.assertIn(idx, positions)

    def test_wrong_pin_count_raises(self):
        for pin_count in (13, 15):
            with self.subTest(pin_count=pin_count), self.assertRaises(FlowError):
                _tap_positions(pin_count, _ring_port_map(pin_count))


class GateNodesTests(unittest.TestCase):
    """`_gate_nodes`: field 2 of every `nfet_03v3`/`pfet_03v3` card."""

    NETLIST = "\n".join(
        [
            "* extracted by klt extract",
            ".SUBCKT ring en ro vddr vss",
            "X0 n1 en vss vss nfet_03v3 L=0.28U W=1U",
            "X1 n1 ro vddr vddr pfet_03v3 L=0.28U W=2U",
            "x2 n2 n1 vss vss nfet_03v3 L=0.28U W=1U",
            "R0 n1 n1_1 12.5",
            "C0 n1 vss 1.5f",
            ".ENDS ring",
        ]
    )

    def test_returns_gate_field_of_each_device_card(self):
        self.assertEqual(_gate_nodes(self.NETLIST, "ring"), {"en", "ro", "n1"})

    def test_three_node_card_raises(self):
        text = self.NETLIST + "\nX3 n2 n1 vss nfet_03v3\n"
        with self.assertRaises(FlowError):
            _gate_nodes(text, "ring")

    def test_foreign_model_raises(self):
        text = self.NETLIST + "\nX3 n2 n1 vss vss nfet_06v0 L=0.7U W=1U\n"
        with self.assertRaises(FlowError):
            _gate_nodes(text, "ring")

    def test_card_free_text_raises(self):
        text = "\n".join(
            [".SUBCKT ring en ro", "R0 en ro 1.0", "C0 ro 0 1f", ".ENDS ring"]
        )
        with self.assertRaises(FlowError):
            _gate_nodes(text, "ring")


class PortOrderTests(unittest.TestCase):
    """`_positional_args` and `_ntap_port_order`."""

    def test_identified_positions_keep_names_others_numbered(self):
        args = _positional_args(6, {1: "en", 4: "ro"}, "n")
        self.assertEqual(args, ["n1", "en", "n2", "n3", "ro", "n4"])

    def test_prefix_is_applied_to_fillers(self):
        self.assertEqual(_positional_args(3, {2: "vss"}, "c"), ["c1", "c2", "vss"])

    def test_no_identified_positions(self):
        self.assertEqual(_positional_args(3, {}, "n"), ["n1", "n2", "n3"])

    def test_ntap_port_order_lists_ro_once(self):
        port_map = _ring_port_map(14)
        positions = _tap_positions(14, port_map)
        order = _ntap_port_order(14, port_map, positions).split()

        # Header: en n1 n2 ro n3 n4 vddr n5 n6 n7 vss n8 n9 n10
        expected = []
        for label in ["n1", "n2", "ro", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10"]:
            if label != "ro":
                expected.append(label)
            expected.append(f"{label}__rx")
        self.assertEqual(order, expected)

        self.assertEqual(order.count("ro__rx"), 1)
        self.assertNotIn("ro", order)  # already in the base `en ro vddr vss`
        for k in range(1, 11):
            with self.subTest(net=f"n{k}"):
                self.assertEqual(order.count(f"n{k}"), 1)
                self.assertEqual(order.count(f"n{k}__rx"), 1)
                self.assertEqual(order.index(f"n{k}__rx"), order.index(f"n{k}") + 1)
        for name in NON_SIGNAL_PORTS:
            self.assertNotIn(name, order)
            self.assertNotIn(f"{name}__rx", order)
        self.assertEqual(len(order), 2 * TAP_COUNT - 1)


class CommentSplitHeaderTests(unittest.TestCase):
    """A full-line `*` comment inside a `.SUBCKT` header (#1063)."""

    BODY = "X1 dd g ss bb nfet_03v3\nR1 g c 1\nR2 dd c 1\n.ENDS dut\n"
    PLAIN = ".SUBCKT dut a b\n+ c d\n" + BODY
    SPLIT = ".SUBCKT dut a b\n* note\n+ c d\n" + BODY

    def test_comment_is_skipped_and_not_indexed(self):
        self.assertEqual(
            _subckt_header(self.SPLIT, "dut"), (["a", "b", "c", "d"], [0, 2])
        )

    def test_several_comments_and_continuations_keep_order(self):
        text = ".SUBCKT dut a\n* x\n+ b\n* y\n* z\n+ c d\n" + self.BODY
        self.assertEqual(
            _subckt_header(text, "dut"), (["a", "b", "c", "d"], [0, 2, 5])
        )

    def test_blank_line_or_new_card_ends_header(self):
        self.assertEqual(
            _subckt_header(".SUBCKT dut a b\n\n+ c\n", "dut"), (["a", "b"], [0])
        )
        text = ".SUBCKT dut a b\n* note\nR1 a b 1\n+ c d\n"
        self.assertEqual(_subckt_header(text, "dut"), (["a", "b"], [0]))

    def test_noise_tap_matches_comment_free_control(self):
        control = _noise_tapped(self.PLAIN, "dut", [2])
        got = _noise_tapped(self.SPLIT, "dut", [2])
        self.assertEqual(got, control.replace("\n", "\n* note\n", 1))
        self.assertEqual(got.count("* note"), 1)
        self.assertEqual(got.count("+ c d"), 0)
        self.assertIn(".SUBCKT dut_ntap a b c d rx0\n", got)
        self.assertIn("R1 g rx0 1", got)
        self.assertIn("R2 dd c 1", got)


if __name__ == "__main__":
    unittest.main()
