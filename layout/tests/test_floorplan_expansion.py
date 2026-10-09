#!/usr/bin/env python3
"""Unit tests for the SPICE hierarchy-expansion helpers in
`layout/floorplan/floorplan.py` -- stdlib only, no `klt`, no `ngspice`, no PDK.

These helpers turn the hand-written subcircuit hierarchy into the cell
inventory and starve-device geometry that feed the floorplan report. An
off-by-a-factor mistake there would still produce a plausible-looking report,
so each helper is pinned here against small synthetic netlists written to a
temp directory, plus one cross-check against the committed
`design/ro_array_core.spice`.

Behaviour pinned here is what the helpers actually do today: they count named
`CELL_MODEL` leaf cells (not transistors), they do not apply the `m`
multiplier, and they do not evaluate subcircuit-header parameter defaults.
Deliberately skipped input (primitive device cards, unknown children) is
tested as skipped, not as an error.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))

from layout._klt import FlowError  # noqa: E402
from layout.floorplan import floorplan  # noqa: E402

RO_ARRAY_CORE = REPO_ROOT / "design" / "ro_array_core.spice"

# Two levels of hierarchy over `CELL_MODEL` leaves, with a comment, a blank
# line, a `+` continuation, a primitive device card and an unknown child.
SYNTHETIC = """\
* synthetic fixture
.subckt leafwrap a y w=1u
xs a y ro_stage w=w
.ends

.subckt mid a y z=1u
* a comment line that must be dropped
xa a n1 leafwrap w=z
xb n1 n2 leafwrap w=z
xc n2 y ro_nand2
Rload y 0 1k
xu y y mystery_cell
.ends

.subckt top a y
xm1 a n1
+ mid z=2u
xm2 n1 y mid z=3u
xbuf y y2 ro_buf
.ends
"""


def _write(text: str) -> Path:
    tmp = tempfile.TemporaryDirectory()
    path = Path(tmp.name) / "fixture.spice"
    path.write_text(text)
    # keep the directory alive for the test's duration
    _KEEPALIVE.append(tmp)
    return path


_KEEPALIVE: list[tempfile.TemporaryDirectory] = []


def tearDownModule() -> None:
    for tmp in _KEEPALIVE:
        tmp.cleanup()
    _KEEPALIVE.clear()


class ToFloatTest(unittest.TestCase):
    def test_plain_and_scientific(self) -> None:
        self.assertEqual(floorplan._to_float("2", {}), 2.0)
        self.assertEqual(floorplan._to_float("  -1.5 ", {}), -1.5)
        self.assertAlmostEqual(floorplan._to_float("1e-3", {}), 1e-3)
        self.assertAlmostEqual(floorplan._to_float("2.5E+2", {}), 250.0)

    def test_unit_suffixes(self) -> None:
        for token, expected in (
            ("0.22u", 0.22e-6),
            ("5n", 5e-9),
            ("3p", 3e-12),
            ("0.5f", 0.5e-15),
            ("2meg", 2e6),
            ("4k", 4e3),
            ("7m", 7e-3),
        ):
            with self.subTest(token=token):
                self.assertAlmostEqual(floorplan._to_float(token, {}) / expected, 1.0)

    def test_meg_wins_over_milli(self) -> None:
        # "meg" must not be read as "m" followed by junk.
        self.assertAlmostEqual(floorplan._to_float("1meg", {}), 1e6)
        self.assertAlmostEqual(floorplan._to_float("1m", {}), 1e-3)

    def test_environment_lookup(self) -> None:
        self.assertEqual(floorplan._to_float("wstv", {"wstv": 0.5}), 0.5)

    def test_invalid_token_raises(self) -> None:
        for token in ("garbage", "", "u5", "'a+b'"):
            with self.subTest(token=token), self.assertRaises(FlowError):
                floorplan._to_float(token, {})

    def test_unknown_suffix_raises(self) -> None:
        with self.assertRaises(FlowError):
            floorplan._to_float("3q", {})


class ReadSubcktsTest(unittest.TestCase):
    def test_multiple_blocks_comments_blank_lines(self) -> None:
        blocks = floorplan.read_subckts(_write(SYNTHETIC))
        self.assertEqual(set(blocks), {"leafwrap", "mid", "top"})
        # The first body entry is the remainder of the `.subckt` header line
        # (pins and defaults); the real body follows it.
        self.assertEqual(blocks["leafwrap"], ["a y w=1u", "xs a y ro_stage w=w"])
        self.assertFalse(any(line.startswith("*") for line in blocks["mid"]))
        self.assertNotIn("", blocks["mid"])
        self.assertEqual(len(blocks["mid"]), 1 + 5)

    def test_continuation_lines_are_joined(self) -> None:
        blocks = floorplan.read_subckts(_write(SYNTHETIC))
        self.assertEqual(blocks["top"][1], "xm1 a n1 mid z=2u")
        self.assertEqual(len(blocks["top"]), 1 + 3)

    def test_no_blocks_returns_empty_dict(self) -> None:
        self.assertEqual(floorplan.read_subckts(_write("* only a comment\n")), {})


class ParamsTest(unittest.TestCase):
    def test_ignores_positional_and_lowercases_keys(self) -> None:
        out = floorplan._params(["a", "b", "WSTV=0.22u", "LStv=2u"], {})
        self.assertEqual(set(out), {"wstv", "lstv"})
        self.assertAlmostEqual(out["wstv"] / 0.22e-6, 1.0)
        self.assertAlmostEqual(out["lstv"] / 2e-6, 1.0)

    def test_values_resolve_through_environment(self) -> None:
        self.assertEqual(floorplan._params(["w=wstv"], {"wstv": 0.75}), {"w": 0.75})

    def test_no_parameters(self) -> None:
        self.assertEqual(floorplan._params(["a", "b"], {}), {})

    def test_invalid_value_raises(self) -> None:
        with self.assertRaises(FlowError):
            floorplan._params(["w=notanumber"], {})
        with self.assertRaises(FlowError):
            floorplan._params(["w=3q"], {})


class ExpandInstanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.subckts = floorplan.read_subckts(_write(SYNTHETIC))

    def test_known_leaf(self) -> None:
        self.assertEqual(
            floorplan.expand_instance({}, "ro_stage", {}), Counter({"ro_stage": 1})
        )

    def test_nested_repeated_children_are_summed(self) -> None:
        # mid = 2 x leafwrap (1 ro_stage each) + 1 ro_nand2; top = 2 x mid + ro_buf.
        # The primitive `Rload` card and the unknown `mystery_cell` are skipped.
        self.assertEqual(
            floorplan.expand_instance(self.subckts, "mid", {"z": 1e-6}),
            Counter({"ro_stage": 2, "ro_nand2": 1}),
        )
        self.assertEqual(
            floorplan.expand_instance(self.subckts, "top", {}),
            Counter({"ro_stage": 4, "ro_nand2": 2, "ro_buf": 1}),
        )

    def test_unknown_root_is_empty(self) -> None:
        self.assertEqual(floorplan.expand_instance(self.subckts, "nope", {}), Counter())

    def test_instance_parameter_supplies_value_for_next_level(self) -> None:
        # `leafwrap` is instantiated with `w=z`; `z` exists only if the
        # parent's instance parameter (or inherited environment) provides it.
        with self.assertRaises(FlowError):
            floorplan.expand_instance(self.subckts, "mid", {})
        inherited = floorplan.expand_instance(self.subckts, "mid", {"z": 9e-6})
        self.assertEqual(inherited["ro_stage"], 2)
        # `top` never defines `z` itself: the instance parameter `z=2u` on
        # `xm1` is what makes the next level resolvable.
        self.assertEqual(floorplan.expand_instance(self.subckts, "top", {})["ro_stage"], 4)

    def test_child_parameter_overrides_inherited_value(self) -> None:
        subckts = {
            "outer": ["xi a y inner w=bad"],
            "inner": ["xl a y ro_stage w=w"],
        }
        # "bad" is not numeric and not in the environment: it would raise.
        with self.assertRaises(FlowError):
            floorplan.expand_instance(subckts, "outer", {})
        # An explicit numeric instance parameter replaces the inherited one.
        subckts["outer"] = ["xi a y inner w=2u"]
        self.assertEqual(
            floorplan.expand_instance(subckts, "outer", {"w": 123.0}),
            Counter({"ro_stage": 1}),
        )


class InstanceCountsTest(unittest.TestCase):
    def test_selects_exactly_one_instance(self) -> None:
        subckts = floorplan.read_subckts(_write(SYNTHETIC))
        self.assertEqual(
            floorplan.instance_counts(subckts, "top", "xm2"),
            Counter({"ro_stage": 2, "ro_nand2": 1}),
        )
        self.assertEqual(
            floorplan.instance_counts(subckts, "top", "xbuf"), Counter({"ro_buf": 1})
        )

    def test_missing_instance_raises(self) -> None:
        subckts = floorplan.read_subckts(_write(SYNTHETIC))
        with self.assertRaisesRegex(FlowError, "xzz"):
            floorplan.instance_counts(subckts, "top", "xzz")
        with self.assertRaises(FlowError):
            floorplan.instance_counts(subckts, "no_such_parent", "xm1")


class AllInstancesOfTest(unittest.TestCase):
    def test_aggregates_repeated_direct_children(self) -> None:
        subckts = floorplan.read_subckts(_write(SYNTHETIC))
        # `mid` has two `leafwrap` instances; each is expanded with its own
        # instance parameters (`w=z` with z unset would raise, so give them
        # explicit values in a dedicated fixture).
        subckts["pair"] = ["xa a b leafwrap w=1u", "xb b c leafwrap w=2u", "xc c d ro_buf"]
        self.assertEqual(
            floorplan.all_instances_of(subckts, "pair", "leafwrap"),
            Counter({"ro_stage": 2}),
        )
        self.assertEqual(
            floorplan.all_instances_of(subckts, "pair", "ro_buf"), Counter({"ro_buf": 1})
        )

    def test_absent_child_raises(self) -> None:
        subckts = floorplan.read_subckts(_write(SYNTHETIC))
        with self.assertRaisesRegex(FlowError, "no instance of 'ro_buf'"):
            floorplan.all_instances_of(subckts, "mid", "ro_buf")
        with self.assertRaises(FlowError):
            floorplan.all_instances_of(subckts, "no_such_parent", "leafwrap")


class StarveGeometryTest(unittest.TestCase):
    RING = (
        ".subckt arr a b\n"
        "xr1 a b ring wstv=0.220u lstv=2u cld=0.5f\n"
        "xr2 a b ring wstv=0.240u lstv=2u cld=0.5f\n"
        ".ends\n"
    )

    def test_explicit_wstv_lstv_in_micrometres_rounded(self) -> None:
        subckts = floorplan.read_subckts(_write(self.RING))
        self.assertEqual(
            floorplan.starve_geometry(subckts, "arr", "xr1"), {"w_um": 0.22, "l_um": 2.0}
        )
        self.assertEqual(
            floorplan.starve_geometry(subckts, "arr", "xr2"), {"w_um": 0.24, "l_um": 2.0}
        )

    def test_committed_ring_instances(self) -> None:
        subckts = floorplan.read_subckts(RO_ARRAY_CORE)
        self.assertEqual(
            floorplan.starve_geometry(subckts, "ro_array_core", "xr1"),
            {"w_um": 0.220, "l_um": 2.0},
        )
        self.assertEqual(
            floorplan.starve_geometry(subckts, "ro_array_core", "xr2"),
            {"w_um": 0.240, "l_um": 2.0},
        )

    def test_absent_instance_raises(self) -> None:
        subckts = floorplan.read_subckts(_write(self.RING))
        with self.assertRaises(FlowError):
            floorplan.starve_geometry(subckts, "arr", "xr9")


class StdcellAreaTest(unittest.TestCase):
    def test_found_key_returns_area(self) -> None:
        areas = {f"{floorplan.area_estimate.STDCELL_LIB}__inv_1": 12.5}
        self.assertEqual(floorplan.stdcell_area(areas, "inv_1"), 12.5)

    def test_missing_key_raises(self) -> None:
        areas = {f"{floorplan.area_estimate.STDCELL_LIB}__inv_1": 12.5}
        with self.assertRaisesRegex(FlowError, "nand2_1"):
            floorplan.stdcell_area(areas, "nand2_1")
        with self.assertRaises(FlowError):
            floorplan.stdcell_area({}, "inv_1")


class CommittedNetlistInventoryTest(unittest.TestCase):
    def test_ro_array_core_cell_inventory(self) -> None:
        subckts = floorplan.read_subckts(RO_ARRAY_CORE)
        # Hand count from design/ro_array_core.spice: each of the two rings
        # (`xr1`, `xr2`, subckt ro_ring11) is one NAND (`xg`) plus ten
        # stages (`x1`..`x10`) = 2 x 1 ro_nand2 and 2 x 10 ro_stage; one
        # ro_buf per ring (`xb1`, `xb2`); one xor2 (`xa1`). 25 cells total.
        expected = Counter({"ro_nand2": 2, "ro_stage": 20, "ro_buf": 2, "xor2": 1})
        self.assertEqual(floorplan.expand_instance(subckts, "ro_array_core", {}), expected)
        self.assertEqual(sum(expected.values()), 25)
        # Per-ring view agrees with the hand count.
        self.assertEqual(
            floorplan.instance_counts(subckts, "ro_array_core", "xr1"),
            Counter({"ro_nand2": 1, "ro_stage": 10}),
        )
        self.assertEqual(
            floorplan.all_instances_of(subckts, "ro_array_core", "ro_ring11"),
            Counter({"ro_nand2": 2, "ro_stage": 20}),
        )


if __name__ == "__main__":
    unittest.main()
