#!/usr/bin/env python3
"""Unit tests for the pure DEF/GDS/netlist checks in `layout/digital/build.py`.

`test_digital_reports.py` covers only the two `*_committed_view` functions.
The checks here decide whether the place-and-route output is trustworthy, so
each gets the two-halves contract `test_verify.py` and
`test_floorplan_netlist.py` use: the real check accepts good input and
rejects deliberately broken input. A check that silently passed everything
(say a regex that stopped matching after a DEF format change) would
otherwise go unnoticed until someone read the committed reports by hand.

No openroad, `klt` or PDK: the DEF text is synthetic, the GDS is written
with the repo's own `layout/testcells/gdsii.py` writer, and the one `klt
stats` call inside `_gds_extent_um` is replaced by a stand-in that reports
the bounding box of the rectangles that were written.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolves annotations via sys.modules
    spec.loader.exec_module(module)
    return module


build = _load("layout_digital_build_checks", LAYOUT_DIR / "digital" / "build.py")
gdsii = _load("layout_gdsii_build_checks", LAYOUT_DIR / "testcells" / "gdsii.py")

LIB = build.CELL_LIBRARY
TAP = f"{LIB}__filltie"
INV = f"{LIB}__inv_1"
NAND = f"{LIB}__nand2_1"


def make_def(
    *,
    die=(0, 0, 200000, 100000),
    dbu=2000,
    components=(("u1", INV), ("u2", NAND), ("tap1", TAP)),
    components_count=None,
    special_nets=("vddd", "vss"),
) -> str:
    """A minimal DEF; `special_nets=None` omits the section, and
    `components=None` omits `COMPONENTS`."""
    lines = [
        "VERSION 5.8 ;",
        "DESIGN trng_top ;",
        f"UNITS DISTANCE MICRONS {dbu} ;",
        "DIEAREA ( {} {} ) ( {} {} ) ;".format(*die),
        "",
    ]
    if components is not None:
        n = len(components) if components_count is None else components_count
        lines.append(f"COMPONENTS {n} ;")
        lines += [f"    - {name} {master} + PLACED ( 0 0 ) N ;" for name, master in components]
        lines += ["END COMPONENTS", ""]
    # A plain NETS section opens its entries the same way SPECIALNETS does;
    # it must never be mistaken for one.
    lines += ["NETS 1 ;", "    - clk ( PIN clk ) ;", "END NETS", ""]
    if special_nets is not None:
        lines.append(f"SPECIALNETS {len(special_nets)} ;")
        lines += [f"    - {net} ( * {net} ) + USE POWER ;" for net in special_nets]
        lines += ["END SPECIALNETS", ""]
    lines.append("END DESIGN")
    return "\n" + "\n".join(lines) + "\n"


class DefFixtureMixin:
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def write_def(self, text: str, name: str = "t.def") -> Path:
        path = self.tmp / name
        path.write_text(text)
        return path


class DefSectionTests(unittest.TestCase):
    def test_returns_body_of_named_section(self):
        body = build._def_section(make_def(), "SPECIALNETS")
        self.assertIn("vddd", body)
        self.assertNotIn("clk", body)

    def test_missing_section_is_none(self):
        self.assertIsNone(build._def_section(make_def(special_nets=None), "SPECIALNETS"))

    def test_unterminated_section_is_none(self):
        text = make_def().replace("END SPECIALNETS", "")
        self.assertIsNone(build._def_section(text, "SPECIALNETS"))


class SpecialNetNamesTests(unittest.TestCase):
    def test_names_sorted_and_deduplicated(self):
        text = make_def(special_nets=("vss", "vddd", "vss"))
        self.assertEqual(build._specialnet_names(text), ["vddd", "vss"])

    def test_plain_nets_are_not_special_nets(self):
        self.assertNotIn("clk", build._specialnet_names(make_def()))

    def test_no_section_gives_empty_list(self):
        self.assertEqual(build._specialnet_names(make_def(special_nets=None)), [])


class DefSummaryTests(DefFixtureMixin, unittest.TestCase):
    def test_reads_header_fields(self):
        s = build._def_summary(self.write_def(make_def()))
        self.assertEqual(s["database_units_per_um"], 2000)
        self.assertEqual(s["component_count"], 3)
        self.assertEqual(s["die_width_um"], 100.0)
        self.assertEqual(s["die_height_um"], 50.0)
        self.assertTrue(s["special_nets"])

    def test_no_components_section_is_reported_cleanly(self):
        s = build._def_summary(self.write_def(make_def(components=None)))
        self.assertIsNone(s["component_count"])
        self.assertEqual(s["die_width_um"], 100.0)

    def test_missing_units_leaves_die_unknown(self):
        text = make_def().replace("UNITS DISTANCE MICRONS 2000 ;", "")
        s = build._def_summary(self.write_def(text))
        self.assertIsNone(s["database_units_per_um"])
        self.assertIsNone(s["die_width_um"])
        self.assertIsNone(s["die_height_um"])

    def test_no_specialnets_flag_false(self):
        s = build._def_summary(self.write_def(make_def(special_nets=None)))
        self.assertFalse(s["special_nets"])


class PowerIsolationTests(DefFixtureMixin, unittest.TestCase):
    def check(self, **kw):
        path = self.write_def(make_def(**kw))
        return build._power_isolation_check(path, build._def_summary(path))

    def test_exactly_own_supplies_is_ok(self):
        r = self.check(special_nets=("vddd", "vss"))
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["found_nets"], ["vddd", "vss"])
        self.assertEqual(r["entropy_supply_nets_present"], [])

    def test_entropy_supply_in_specialnets_fails(self):
        r = self.check(special_nets=("vddd", "vss", "vddr1"))
        self.assertEqual(r["status"], "mismatch")
        self.assertEqual(r["entropy_supply_nets_present"], ["vddr1"])

    def test_shorted_net_name_fails(self):
        # Digital supply replaced by the combiner/sampler supply.
        r = self.check(special_nets=("vdd", "vss"))
        self.assertEqual(r["status"], "mismatch")
        self.assertEqual(r["entropy_supply_nets_present"], ["vdd"])

    def test_own_supply_missing_fails(self):
        r = self.check(special_nets=("vss",))
        self.assertEqual(r["status"], "mismatch")
        self.assertEqual(r["found_nets"], ["vss"])

    def test_no_specialnets_section_is_skipped_not_ok(self):
        r = self.check(special_nets=None)
        self.assertEqual(r["status"], "skipped")

    def test_header_without_readable_body_is_skipped(self):
        path = self.write_def("\nSPECIALNETS 1 ;\n")
        r = build._power_isolation_check(path, build._def_summary(path))
        self.assertEqual(r["status"], "skipped")


class GdsGeometryTests(DefFixtureMixin, unittest.TestCase):
    def gds_check(self, width_um, height_um, def_text=None):
        """Write a real GDS of the given extent, then check it against a DEF."""
        gds = self.tmp / "top.gds"
        rects = [gdsii.Rect(1, 0, 0.0, 0.0, width_um, height_um)]
        gdsii.write_gds(str(gds), "lib", [("top", rects, [])])
        def_path = self.write_def(def_text or make_def())

        def fake_klt(args, timeout_s=None):
            self.assertEqual(args[0], "stats")
            return {"bbox_um": {"width": width_um, "height": height_um}}

        with mock.patch.object(build, "REPO_ROOT", self.tmp), mock.patch.object(
            build, "_run_klt", fake_klt
        ):
            return build._gds_geometry_check(gds, build._def_summary(def_path))

    def test_extent_reads_klt_bbox(self):
        gds = self.tmp / "top.gds"
        gds.write_bytes(b"")
        with mock.patch.object(build, "REPO_ROOT", self.tmp), mock.patch.object(
            build, "_run_klt", lambda *a, **k: {"bbox_um": {"width": 3.5, "height": 4.5}}
        ):
            self.assertEqual(build._gds_extent_um(gds), (3.5, 4.5))

    def test_matching_extent_is_ok(self):
        r = self.gds_check(100.0, 50.0)
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["def_die_um"], [100.0, 50.0])

    def test_extent_within_well_overhang_is_ok(self):
        self.assertEqual(self.gds_check(100.86, 50.86)["status"], "ok")

    def test_extent_disagreeing_with_die_fails(self):
        # The defect this check exists for: a merge that rescales by 2x.
        r = self.gds_check(200.0, 100.0)
        self.assertEqual(r["status"], "mismatch")
        self.assertEqual(r["gds_over_def_ratio"], [2.0, 2.0])

    def test_one_axis_disagreeing_fails(self):
        self.assertEqual(self.gds_check(100.0, 80.0)["status"], "mismatch")

    def test_def_without_diearea_is_skipped(self):
        text = make_def().replace("DIEAREA", "XDIEAREA")
        r = self.gds_check(100.0, 50.0, def_text=text)
        self.assertEqual(r["status"], "skipped")


class NetlistInstanceCountTests(DefFixtureMixin, unittest.TestCase):
    def test_counts_cell_instantiations_only(self):
        path = self.write_def(
            "module top (a, y);\n  input a;\n  output y;\n"
            f"  {INV} u1 (.I(a), .ZN(n1));\n"
            f"  {NAND} u2 (.A1(n1), .A2(a), .ZN(y));\n"
            "endmodule\n",
            "n.v",
        )
        self.assertEqual(build._netlist_instance_count(path), 2)

    def test_netlist_without_instances_counts_zero(self):
        path = self.write_def("module top ();\nendmodule\n", "n.v")
        self.assertEqual(build._netlist_instance_count(path), 0)

    def test_missing_netlist_is_none(self):
        self.assertIsNone(build._netlist_instance_count(self.tmp / "absent.v"))


class ComponentCountsByMasterTests(unittest.TestCase):
    def test_counts_only_requested_masters(self):
        text = make_def(components=(("a", TAP), ("b", TAP), ("c", INV)))
        self.assertEqual(
            build._def_component_counts_by_master(text, (TAP, f"{LIB}__fill_1")),
            {TAP: 2, f"{LIB}__fill_1": 0},
        )

    def test_no_components_section_gives_empty(self):
        text = make_def(components=None)
        self.assertEqual(build._def_component_counts_by_master(text, (TAP,)), {})

    def test_no_masters_gives_empty(self):
        self.assertEqual(build._def_component_counts_by_master(make_def(), ()), {})


class ComponentCheckTests(DefFixtureMixin, unittest.TestCase):
    def check(self, netlist_instances, masters=(TAP,), **def_kw):
        net = self.tmp / "pnr.v"
        net.write_text("".join(f"  {INV} u{i} (.I(a));\n" for i in range(netlist_instances)))
        path = self.write_def(make_def(**def_kw))
        with mock.patch.object(build, "PNR_NETLIST_PATH", net), mock.patch.object(
            build, "REPO_ROOT", self.tmp  # no synth report -> synthesized is None
        ):
            return build._component_check(path, build._def_summary(path), masters)

    def test_counts_agree_after_subtracting_physical_only(self):
        # 3 DEF components, one of them a tap cell -> 2 logical == netlist 2.
        r = self.check(2)
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["physical_only_instance_count"], 1)
        self.assertEqual(r["logical_placed"], 2)
        self.assertIsNone(r["delta_vs_synthesized"])

    def test_count_differing_from_netlist_fails(self):
        self.assertEqual(self.check(5)["status"], "mismatch")

    def test_unsubtracted_physical_cells_fail(self):
        # Without naming the tap master, the DEF has 3 vs netlist 2.
        self.assertEqual(self.check(2, masters=())["status"], "mismatch")

    def test_def_without_components_is_skipped_cleanly(self):
        r = self.check(2, components=None)
        self.assertEqual(r["status"], "skipped")
        self.assertIsNone(r["placed"])
        self.assertEqual(r["as_built_netlist"], 2)

    def test_missing_netlist_is_skipped_cleanly(self):
        path = self.write_def(make_def())
        with mock.patch.object(build, "PNR_NETLIST_PATH", self.tmp / "none.v"), mock.patch.object(
            build, "REPO_ROOT", self.tmp
        ):
            r = build._component_check(path, build._def_summary(path), (TAP,))
        self.assertEqual(r["status"], "skipped")
        self.assertIsNone(r["as_built_netlist"])


if __name__ == "__main__":
    unittest.main()
