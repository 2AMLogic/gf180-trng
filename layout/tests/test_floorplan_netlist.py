#!/usr/bin/env python3
"""Unit tests for `design/floorplan_netlist.py` -- issue #221's own required
Python-only self-check, exercised directly (no `klt`, no PDK, no network:
everything here is a plain-text read of the four regions' own committed
reference `.spice` files, already in this checkout).

Two things this suite has to prove, per #221's own acceptance criteria:

1. `INTER_REGION_NETS` (the committed declaration) actually validates clean
   against the four regions' own committed reference netlists -- the same
   check `layout/floorplan/floorplan.py`'s own `main()` now runs on every
   invocation, gating this file's own consistency.
2. The mechanical self-check *works*, not just that the committed data
   happens to pass it: a deliberately broken declaration (a typo'd pin name,
   a merged supply net, a missing `spans_regions` flag) has to be caught,
   not silently accepted. Without this half, a future edit that widens the
   check too far -- or a typo in the check itself -- could turn the
   acceptance criterion into a no-op the same way #148's stale-field
   comparison could (`layout/tests/test_verify.py`'s own module docstring
   makes the same point about its own suite).
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# `design/floorplan_netlist.py` is a flat module (see its own docstring on
# why it lives under `design/`, not as a package member of anything) --
# loaded from its own file path, the same way `layout/tests/test_verify.py`
# loads `layout/verify.py`, so a second, unrelated module of the same name
# elsewhere can never shadow it via `sys.modules`.
_SPEC = importlib.util.spec_from_file_location(
    "layout_tests_floorplan_netlist_module",
    REPO_ROOT / "design" / "floorplan_netlist.py",
)
fn = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(fn)


class ValidateInterRegionNetsTests(unittest.TestCase):
    """`validate_inter_region_nets()` against the real, committed data."""

    def test_committed_declaration_is_clean(self) -> None:
        problems = fn.validate_inter_region_nets()
        self.assertEqual(problems, [], msg="\n".join(problems))

    def test_reference_top_pins_reads_every_region(self) -> None:
        for rid, (path, top) in fn.REGION_REFERENCES.items():
            pins = fn.reference_top_pins(path, top)
            self.assertGreater(
                len(pins), 0, msg=f"region {rid!r} resolved zero pins from {path}"
            )

    def test_four_supply_nets_are_declared_and_distinct(self) -> None:
        supply_nets = [n for n in fn.INTER_REGION_NETS if n["role"] == "supply"]
        names = sorted(n["name"] for n in supply_nets)
        self.assertEqual(names, ["vdd", "vddd", "vddr1", "vddr2"])
        # No two supply nets may share an endpoint region -- the star-point
        # separation invariant the module docstring makes explicit.
        regions_seen: set[str] = set()
        for net in supply_nets:
            regions = {rid for rid, _ in net.get("endpoints", ())}
            regions |= {rid for rid, _ in net.get("implicit_regions", ())}
            self.assertTrue(
                regions.isdisjoint(regions_seen),
                msg=f"net {net['name']!r} shares a region with an earlier "
                "supply net",
            )
            regions_seen |= regions

    def test_ro1_flags_the_long_haul_route_over_ring2(self) -> None:
        (ro1,) = [n for n in fn.INTER_REGION_NETS if n["name"] == "ro1"]
        self.assertEqual(ro1.get("spans_regions"), ["ring2"])
        self.assertIn(("ring1", "ro"), ro1["endpoints"])
        self.assertIn(("combiner_sampler", "rn1"), ro1["endpoints"])

    def test_ring_bit_name_mismatch_is_resolved_not_hidden(self) -> None:
        """`combiner_sampler`'s own `ring_bit1`/`ring_bit2` and `digital`'s
        own `ring_bit[0]`/`ring_bit[1]` name the same two nets under two
        different committed spellings -- the declaration has to bridge that,
        not silently rename either committed reference.
        """
        by_name = {n["name"]: n for n in fn.INTER_REGION_NETS}
        self.assertEqual(
            sorted(by_name["ring_bit1"]["endpoints"]),
            sorted([("combiner_sampler", "ring_bit1"), ("digital", "ring_bit[0]")]),
        )
        self.assertEqual(
            sorted(by_name["ring_bit2"]["endpoints"]),
            sorted([("combiner_sampler", "ring_bit2"), ("digital", "ring_bit[1]")]),
        )

    def test_vddd_and_vss_reach_digital_only_implicitly(self) -> None:
        by_name = {n["name"]: n for n in fn.INTER_REGION_NETS}
        vddd = by_name["vddd"]
        self.assertEqual(vddd["endpoints"], [])
        self.assertEqual(vddd["implicit_regions"], [("digital", "vddd")])
        vss = by_name["vss"]
        self.assertIn(("digital", "vss"), vss["implicit_regions"])
        self.assertNotIn(
            "digital", {rid for rid, _ in vss["endpoints"]},
            msg="digital's own reference has no .SUBCKT vss pin to claim",
        )


class ValidateInterRegionNetsCatchesBreakageTests(unittest.TestCase):
    """The mechanical self-check must actually fail on a broken declaration
    -- proven by mutating a deep copy of the real data, one way at a time,
    and confirming each mutation is caught.
    """

    def setUp(self) -> None:
        self._original_nets = fn.INTER_REGION_NETS
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        fn.INTER_REGION_NETS = self._original_nets

    def _install(self, nets: list[dict]) -> list[str]:
        fn.INTER_REGION_NETS = nets
        return fn.validate_inter_region_nets()

    def test_typo_d_pin_name_is_caught(self) -> None:
        nets = copy.deepcopy(self._original_nets)
        for net in nets:
            if net["name"] == "en1":
                net["endpoints"] = [("ring1", "enn")]  # typo: real pin is "en"
        problems = self._install(nets)
        self.assertTrue(
            any("enn" in problem for problem in problems), msg=problems
        )

    def test_unknown_region_id_is_caught(self) -> None:
        nets = copy.deepcopy(self._original_nets)
        for net in nets:
            if net["name"] == "en2":
                net["endpoints"] = [("ring3", "en")]  # no such region
        problems = self._install(nets)
        self.assertTrue(
            any("ring3" in problem for problem in problems), msg=problems
        )

    def test_merging_two_supply_nets_onto_the_same_region_is_caught(self) -> None:
        """The acceptance criterion this repeats most directly: vddr1 must
        never be reachable through the same region as vdd/vddd/vddr2."""
        nets = copy.deepcopy(self._original_nets)
        for net in nets:
            if net["name"] == "vddr2":
                # Wrongly point vddr2 at combiner_sampler's own vdd pin,
                # simulating an accidental merge of the two star branches.
                net["endpoints"] = [("combiner_sampler", "vdd")]
        problems = self._install(nets)
        self.assertTrue(
            any("supply net" in problem for problem in problems), msg=problems
        )

    def test_missing_ro1_span_flag_is_caught(self) -> None:
        nets = copy.deepcopy(self._original_nets)
        for net in nets:
            if net["name"] == "ro1":
                net["spans_regions"] = []
        problems = self._install(nets)
        self.assertTrue(
            any("ro1" in problem and "spans_regions" in problem for problem in problems),
            msg=problems,
        )

    def test_duplicate_net_name_is_caught(self) -> None:
        nets = copy.deepcopy(self._original_nets)
        dup = copy.deepcopy(nets[0])
        nets.append(dup)
        problems = self._install(nets)
        self.assertTrue(
            any("declared more than once" in problem for problem in problems),
            msg=problems,
        )

    def test_two_nets_claiming_the_same_pin_is_caught(self) -> None:
        nets = copy.deepcopy(self._original_nets)
        for net in nets:
            if net["name"] == "en2":
                # en2 wrongly also claims ring1's own "en" pin, already
                # claimed by en1.
                net["endpoints"] = [("ring1", "en")]
        problems = self._install(nets)
        self.assertTrue(
            any("claimed by two different nets" in problem for problem in problems),
            msg=problems,
        )

    def test_bad_implicit_region_specialnet_is_caught(self) -> None:
        nets = copy.deepcopy(self._original_nets)
        for net in nets:
            if net["name"] == "vddd":
                net["implicit_regions"] = [("digital", "vccc")]  # not a real specialnet
        problems = self._install(nets)
        self.assertTrue(
            any("vccc" in problem for problem in problems), msg=problems
        )


class GenerateLvsReferenceTests(unittest.TestCase):
    """`generate_lvs_reference()` -- the composed netlist text itself."""

    def test_generated_text_matches_the_committed_file(self) -> None:
        """Guards against the generator and the committed artefact drifting
        apart -- the same freshness contract `layout/floorplan/floorplan.py`
        already enforces for its own `reports/*.json` artefacts."""
        generated = fn.generate_lvs_reference()
        self.assertTrue(
            fn.LVS_REFERENCE_PATH.is_file(),
            msg=(
                f"{fn.LVS_REFERENCE_PATH} is missing -- run `python3 "
                "design/floorplan_netlist.py --write`"
            ),
        )
        committed = fn.LVS_REFERENCE_PATH.read_text()
        self.assertEqual(
            committed,
            generated,
            msg=(
                f"{fn.LVS_REFERENCE_PATH} does not match this declaration -- "
                "run `python3 design/floorplan_netlist.py --write` to refresh it"
            ),
        )

    def test_includes_every_region_reference_and_top_subckt(self) -> None:
        text = fn.generate_lvs_reference()
        self.assertIn(f".SUBCKT {fn.TOP_CELL} ", text)
        self.assertIn(f".ENDS {fn.TOP_CELL}", text)
        for rid, (_path, top) in fn.REGION_REFERENCES.items():
            self.assertIn(
                f" {top}\n", text, msg=f"no X-card instantiating {top!r} ({rid})"
            )

    def test_vddr_branches_stay_four_distinct_net_names_in_the_composed_text(
        self,
    ) -> None:
        text = fn.generate_lvs_reference()
        header_line = next(
            line for line in text.splitlines() if line.startswith(f".SUBCKT {fn.TOP_CELL} ")
        )
        pins = header_line.split()[2:]
        for name in ("vddr1", "vddr2", "vdd", "vddd"):
            self.assertEqual(
                pins.count(name), 1, msg=f"{name!r} should appear exactly once in "
                f"the composed header, found {pins.count(name)} times"
            )

    def test_generation_fails_on_a_broken_declaration(self) -> None:
        original = fn.INTER_REGION_NETS
        try:
            broken = copy.deepcopy(original)
            for net in broken:
                if net["name"] == "en1":
                    net["endpoints"] = [("ring1", "not_a_real_pin")]
            fn.INTER_REGION_NETS = broken
            with self.assertRaises(fn.FloorplanNetlistError):
                fn.generate_lvs_reference()
        finally:
            fn.INTER_REGION_NETS = original


if __name__ == "__main__":
    unittest.main()
