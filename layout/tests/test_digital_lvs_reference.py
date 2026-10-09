#!/usr/bin/env python3
"""Unit tests for the reference-netlist helpers in `layout/digital/lvs.py`
(issue #382).

`lvs.py` turns the as-built gate-level netlist (via Yosys JSON) and the
layout side's own extracted cell interfaces into the SPICE reference that
`klt lvs` compares the digital section against. The helpers covered here
decide which nets get which names, which pins each cell type has, which
instances exist, and what the top-level interface is. A regression in any of
them surfaces as a false LVS mismatch at best, and at worst as a reference
that agrees with a wrong layout. Before this module, only `_committed_view`
had a direct test (`test_digital_reports.py`).

Closed issue #186 is the motivating case: the reference once derived a cell
type's interface from the pins its instances happened to connect rather than
from the library, so a CTS clock-load dummy (an `inv_8` with its `ZN` output
left unconnected) came out with a 3-pin interface against the layout's real
4-pin one. `CellInstancesTests.test_unconnected_library_pin_is_kept` pins
that behaviour.

Inputs are small synthetic Yosys-JSON dicts, SPICE snippets and DEF
fragments written to a temporary directory. No `klt`, no `yosys`, no PDK and
no network; the whole module runs in well under a second. These tests check
the helpers' own data handling only. They are not evidence that the digital
section is LVS-clean -- that is re-answered by running `lvs.py` itself.

Helpers covered: `_join_spice_continuations`, `_bit_names`,
`_library_cell_pins`, `_top_pins`, `_cell_instances` and
`_def_physical_only_instances`.
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

DIGITAL_DIR = LAYOUT_DIR / "digital"


def _load(name: str, path: Path):
    """Load a flat `layout/digital/*.py` driver as a module.

    Same `importlib.util.spec_from_file_location` pattern as
    `test_digital_reports.py`: these are scripts run by path, not package
    members, so there is no import path to reach them by.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


lvs = _load("layout_digital_lvs", DIGITAL_DIR / "lvs.py")

# Cell-type names, restated here rather than read back from the module.
PREFIX = "gf180mcu_fd_sc_mcu9t5v0__"
INV_1 = PREFIX + "inv_1"
INV_8 = PREFIX + "inv_8"
NAND2_1 = PREFIX + "nand2_1"
FILLTIE = PREFIX + "filltie"
ENDCAP = PREFIX + "endcap"
FILL_1 = PREFIX + "fill_1"


class _TempRepoMixin:
    """Write fixture files to a temp directory treated as the repo root.

    The helpers that read a file name it in their error message relative to
    `lvs.REPO_ROOT`. Patching that to the temp directory keeps the fixtures
    out of the real worktree while still exercising the error path as
    production reaches it (production paths always sit under the repo).
    """

    def setUp(self):
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        patcher = mock.patch.object(lvs, "REPO_ROOT", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.write_text(text)
        return path


class JoinSpiceContinuationsTests(unittest.TestCase):
    def test_folds_continuation_into_previous_line(self):
        text = ".SUBCKT top A B\n+ C D\n+ E\n.ENDS top"
        self.assertEqual(
            lvs._join_spice_continuations(text),
            ".SUBCKT top A B C D E\n.ENDS top",
        )

    def test_strips_whitespace_around_continuation_body(self):
        text = ".SUBCKT top A\n+    B   \n"
        self.assertEqual(
            lvs._join_spice_continuations(text), ".SUBCKT top A B\n"
        )

    def test_text_without_continuations_is_unchanged(self):
        text = "* comment\n.SUBCKT a A Z\n.ENDS a\n"
        self.assertEqual(lvs._join_spice_continuations(text), text)

    def test_comment_line_does_not_swallow_following_card(self):
        """A comment followed by an ordinary (non-`+`) line stays its own line."""
        text = ".SUBCKT a A\n* pin note\n.ENDS a"
        self.assertEqual(lvs._join_spice_continuations(text), text)

    def test_continuation_after_comment_continues_the_card(self):
        """SPICE dialects (HSPICE explicitly) allow a comment line between a
        card and its `+` continuation; the continuation still belongs to the
        card. The helper currently folds it into the comment instead, so the
        continued pins vanish. Latent today -- `klt extract` does not emit an
        interleaved comment -- (#387).
        """
        text = ".SUBCKT a A\n* note\n+ B C\n.ENDS a"
        self.assertEqual(
            lvs._join_spice_continuations(text),
            ".SUBCKT a A B C\n* note\n.ENDS a",
        )

    def test_leading_continuation_with_no_predecessor_is_kept(self):
        """Malformed input: a `+` on the very first line has nothing to join
        onto, so it is passed through rather than dropped or raising."""
        text = "+ orphan\n.SUBCKT a A\n"
        self.assertEqual(lvs._join_spice_continuations(text), text)

    def test_multiple_comments_between_card_and_continuation(self):
        text = ".SUBCKT a A\n* one\n* two\n+ B\n+ C\n.ENDS a"
        self.assertEqual(
            lvs._join_spice_continuations(text),
            ".SUBCKT a A B C\n* one\n* two\n.ENDS a",
        )

    def test_blank_line_is_not_a_comment(self):
        """A blank line is a (empty) card, so a `+` after it attaches there
        and the header is not extended."""
        text = ".SUBCKT a A\n\n+ B\n.ENDS a"
        self.assertEqual(
            lvs._join_spice_continuations(text), ".SUBCKT a A\n B\n.ENDS a"
        )

    def test_continuation_with_only_comments_before_is_kept(self):
        text = "* c\n+ orphan\n.SUBCKT a A"
        self.assertEqual(lvs._join_spice_continuations(text), text)

    def test_empty_text(self):
        self.assertEqual(lvs._join_spice_continuations(""), "")


class BitNamesTests(unittest.TestCase):
    def test_scalar_and_multibit_ports(self):
        module = {
            "ports": {
                "clk": {"direction": "input", "bits": [2]},
                "reg_addr": {"direction": "input", "bits": [3, 4, 5]},
            },
            "netnames": {},
        }
        self.assertEqual(
            lvs._bit_names(module),
            {2: "clk", 3: "reg_addr[0]", 4: "reg_addr[1]", 5: "reg_addr[2]"},
        )

    def test_one_bit_port_is_bare_not_indexed(self):
        module = {"ports": {"rst_n": {"bits": [7]}}, "netnames": {}}
        self.assertEqual(lvs._bit_names(module), {7: "rst_n"})

    def test_multibit_netname_is_indexed(self):
        module = {
            "ports": {},
            "netnames": {"u_core/state": {"bits": [10, 11]}},
        }
        self.assertEqual(
            lvs._bit_names(module),
            {10: "u_core/state[0]", 11: "u_core/state[1]"},
        )

    def test_port_name_wins_over_internal_alias(self):
        module = {
            "ports": {"dout": {"bits": [8, 9]}},
            "netnames": {
                "dout": {"bits": [8, 9]},
                "a": {"bits": [8]},
            },
        }
        names = lvs._bit_names(module)
        self.assertEqual(names[8], "dout[0]")
        self.assertEqual(names[9], "dout[1]")

    def test_shortest_then_lexicographic_alias_is_chosen(self):
        module = {
            "ports": {},
            "netnames": {
                "u_x/long_alias": {"bits": [20]},
                "zz": {"bits": [20]},
                "ab": {"bits": [20]},
                "n": {"bits": [21]},
                "bus": {"bits": [22, 21]},
            },
        }
        names = lvs._bit_names(module)
        self.assertEqual(names[20], "ab")
        # "n" (1 char) beats "bus[1]" (6 chars) for bit 21.
        self.assertEqual(names[21], "n")
        self.assertEqual(names[22], "bus[0]")

    def test_choice_does_not_depend_on_dict_order(self):
        netnames = {"b": {"bits": [5]}, "a": {"bits": [5]}}
        reordered = dict(reversed(list(netnames.items())))
        first = lvs._bit_names({"ports": {}, "netnames": netnames})
        second = lvs._bit_names({"ports": {}, "netnames": reordered})
        self.assertEqual(first, second)
        self.assertEqual(first[5], "a")

    def test_missing_ports_key_raises(self):
        """Malformed input: a module dict without `ports` is not a Yosys
        module; the helper fails loudly rather than returning a partial map."""
        with self.assertRaises(KeyError):
            lvs._bit_names({"netnames": {}})

    def test_port_without_bits_raises(self):
        with self.assertRaises(KeyError):
            lvs._bit_names({"ports": {"clk": {}}, "netnames": {}})

    def test_unnamed_bit_is_absent_not_invented(self):
        """A bit no port or netname covers gets no invented name; the
        failure surfaces in `_cell_instances` as an `LvsFlowError`."""
        module = {"ports": {}, "netnames": {}}
        self.assertNotIn(42, lvs._bit_names(module))

    def test_cell_instances_names_instance_port_and_bit_for_unnamed_bit(self):
        module = {
            "cells": {"u0": {"type": INV_1, "connections": {"I": [42]}}},
        }
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._cell_instances(module, {}, {INV_1: ["I", "VDD", "VSS", "ZN"]})
        msg = str(ctx.exception)
        for token in ("u0", "'I'", "42"):
            self.assertIn(token, msg)


class LibraryCellPinsTests(_TempRepoMixin, unittest.TestCase):
    EXTRACTED = (
        "* extracted by klt\n"
        f".SUBCKT {INV_1} I VDD VSS ZN\n"
        f".ENDS {INV_1}\n"
        f".SUBCKT {NAND2_1} A1 A2\n"
        "+ VDD VSS\n"
        "+ ZN\n"
        f".ENDS {NAND2_1}\n"
        f".SUBCKT {INV_8} I VDD VSS ZN\n"
        f".ENDS {INV_8}\n"
        ".SUBCKT trng_top clk rst_n\n"
        "+ vddd vss\n"
        ".ENDS trng_top\n"
    )

    def test_reads_requested_cell_interfaces(self):
        path = self.write("extracted.spice", self.EXTRACTED)
        found = lvs._library_cell_pins(path, {INV_1, NAND2_1})
        self.assertEqual(
            found,
            {
                INV_1: ["I", "VDD", "VSS", "ZN"],
                NAND2_1: ["A1", "A2", "VDD", "VSS", "ZN"],
            },
        )

    def test_unrequested_subckts_are_ignored(self):
        path = self.write("extracted.spice", self.EXTRACTED)
        found = lvs._library_cell_pins(path, {INV_8})
        self.assertEqual(set(found), {INV_8})
        self.assertNotIn("trng_top", found)

    def test_pin_order_is_the_files_not_sorted(self):
        path = self.write(
            "extracted.spice", f".SUBCKT {INV_1} ZN VSS VDD I\n.ENDS\n"
        )
        self.assertEqual(
            lvs._library_cell_pins(path, {INV_1})[INV_1],
            ["ZN", "VSS", "VDD", "I"],
        )

    def test_empty_request_reads_nothing_and_returns_empty(self):
        path = self.write("extracted.spice", self.EXTRACTED)
        self.assertEqual(lvs._library_cell_pins(path, set()), {})

    def test_missing_cell_type_raises_naming_it(self):
        path = self.write("extracted.spice", self.EXTRACTED)
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._library_cell_pins(path, {INV_1, FILL_1})
        self.assertIn(FILL_1, str(ctx.exception))
        self.assertNotIn(INV_1 + ",", str(ctx.exception))

    def test_lowercase_subckt_header_is_not_recognised(self):
        """Malformed (for this reader) input: the header regex is
        upper-case-only by design, matching `klt extract`'s own writer, so a
        lower-case `.subckt` is reported as missing rather than half-read."""
        path = self.write("extracted.spice", f".subckt {INV_1} I ZN\n.ends\n")
        with self.assertRaises(lvs.LvsFlowError):
            lvs._library_cell_pins(path, {INV_1})


class TopPinsTests(unittest.TestCase):
    MODULE = {
        "ports": {
            "rst_n": {"bits": [2]},
            "reg_addr": {"bits": [3, 4]},
            "clk": {"bits": [5]},
            "dout": {"bits": [6, 7, 8]},
        }
    }

    def test_sorted_with_multibit_expansion(self):
        self.assertEqual(
            lvs._top_pins(self.MODULE),
            [
                "clk",
                "dout[0]",
                "dout[1]",
                "dout[2]",
                "reg_addr[0]",
                "reg_addr[1]",
                "rst_n",
            ],
        )

    def test_extra_pins_are_included_exactly_once(self):
        pins = lvs._top_pins(self.MODULE, extra=("vss", "vddd"))
        self.assertEqual(pins.count("vddd"), 1)
        self.assertEqual(pins.count("vss"), 1)
        self.assertEqual(len(pins), 7 + 2)
        self.assertEqual(pins, sorted(pins))

    def test_order_is_independent_of_port_and_extra_order(self):
        reordered = {"ports": dict(reversed(list(self.MODULE["ports"].items())))}
        self.assertEqual(
            lvs._top_pins(self.MODULE, extra=("vddd", "vss")),
            lvs._top_pins(reordered, extra=("vss", "vddd")),
        )

    def test_does_not_mutate_inputs(self):
        extra = ("vddd", "vss")
        before = {k: dict(v) for k, v in self.MODULE["ports"].items()}
        lvs._top_pins(self.MODULE, extra=extra)
        self.assertEqual(self.MODULE["ports"], before)
        self.assertEqual(extra, ("vddd", "vss"))

    def test_extra_colliding_with_a_port_raises(self):
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._top_pins(self.MODULE, extra=("clk", "vss"))
        self.assertIn("clk", str(ctx.exception))

    def test_extra_colliding_with_an_expanded_bit_raises(self):
        with self.assertRaises(lvs.LvsFlowError):
            lvs._top_pins(self.MODULE, extra=("dout[1]",))

    def test_missing_ports_key_raises(self):
        with self.assertRaises(KeyError):
            lvs._top_pins({})


def _cell(cell_type: str, **connections: list) -> dict:
    return {"type": cell_type, "connections": dict(connections)}


class CellInstancesTests(unittest.TestCase):
    LIBRARY = {
        INV_1: ["I", "VDD", "VSS", "ZN"],
        INV_8: ["I", "VDD", "VSS", "ZN"],
        NAND2_1: ["A1", "A2", "VDD", "VSS", "ZN"],
    }
    BIT_NAMES = {2: "clk", 3: "n1", 4: "n2", 5: "n3"}

    def test_transcribes_connections_sorted_by_instance(self):
        module = {
            "cells": {
                "u_b": _cell(NAND2_1, A1=[2], A2=[3], ZN=[4]),
                "u_a": _cell(INV_1, I=[4], ZN=[5]),
            }
        }
        pins_by_type, instances = lvs._cell_instances(
            module, self.BIT_NAMES, self.LIBRARY
        )
        self.assertEqual(
            instances,
            [
                (INV_1, "u_a", {"I": "n2", "ZN": "n3"}),
                (NAND2_1, "u_b", {"A1": "clk", "A2": "n1", "ZN": "n2"}),
            ],
        )
        self.assertEqual(list(pins_by_type), sorted(pins_by_type))
        self.assertEqual(
            pins_by_type,
            {INV_1: self.LIBRARY[INV_1], NAND2_1: self.LIBRARY[NAND2_1]},
        )

    def test_unconnected_library_pin_is_kept(self):
        """#186: the only instance of `inv_8` leaves `ZN` unconnected (a CTS
        clock-load dummy). The type's reference interface must still be the
        library's full 4-pin list, not the 1 pin this instance connects."""
        module = {"cells": {"clkload13": _cell(INV_8, I=[2])}}
        pins_by_type, instances = lvs._cell_instances(
            module, self.BIT_NAMES, self.LIBRARY
        )
        self.assertEqual(pins_by_type[INV_8], ["I", "VDD", "VSS", "ZN"])
        self.assertEqual(instances, [(INV_8, "clkload13", {"I": "clk"})])

    def test_only_instantiated_types_are_reported(self):
        module = {"cells": {"u0": _cell(INV_1, I=[2], ZN=[3])}}
        pins_by_type, _ = lvs._cell_instances(
            module, self.BIT_NAMES, self.LIBRARY
        )
        self.assertEqual(set(pins_by_type), {INV_1})

    def test_physical_only_masters_are_not_instances(self):
        """Tapcells/endcaps/fillers come from the DEF, never the netlist: a
        netlist with none yields no physical-only entries, and the library
        map carrying their names does not conjure instances of them."""
        library = dict(self.LIBRARY, **{FILLTIE: ["VDD", "VSS"]})
        module = {"cells": {"u0": _cell(INV_1, I=[2], ZN=[3])}}
        pins_by_type, instances = lvs._cell_instances(
            module, self.BIT_NAMES, library
        )
        self.assertNotIn(FILLTIE, pins_by_type)
        self.assertEqual([entry[0] for entry in instances], [INV_1])

    def test_empty_netlist(self):
        self.assertEqual(
            lvs._cell_instances({"cells": {}}, self.BIT_NAMES, self.LIBRARY),
            ({}, []),
        )

    def test_foreign_library_cell_raises(self):
        module = {"cells": {"u0": _cell("sky130_fd_sc_hd__inv_1", A=[2])}}
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._cell_instances(module, self.BIT_NAMES, self.LIBRARY)
        self.assertIn("u0", str(ctx.exception))

    def test_multibit_cell_port_raises(self):
        module = {"cells": {"u0": _cell(INV_1, I=[2, 3])}}
        with self.assertRaises(lvs.LvsFlowError):
            lvs._cell_instances(module, self.BIT_NAMES, self.LIBRARY)

    def test_constant_tied_port_raises(self):
        module = {"cells": {"u0": _cell(INV_1, I=["1"], ZN=[3])}}
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._cell_instances(module, self.BIT_NAMES, self.LIBRARY)
        self.assertIn("constant", str(ctx.exception))

    def test_type_without_resolved_interface_raises(self):
        module = {"cells": {"u0": _cell(PREFIX + "xor2_1", A1=[2])}}
        with self.assertRaises(lvs.LvsFlowError):
            lvs._cell_instances(module, self.BIT_NAMES, self.LIBRARY)

    def test_port_absent_from_library_interface_raises(self):
        module = {"cells": {"u0": _cell(INV_1, I=[2], EN=[3])}}
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._cell_instances(module, self.BIT_NAMES, self.LIBRARY)
        self.assertIn("EN", str(ctx.exception))


class DefPhysicalOnlyInstancesTests(_TempRepoMixin, unittest.TestCase):
    DEF = (
        "VERSION 5.8 ;\n"
        "DESIGN trng_top ;\n"
        "COMPONENTS 6 ;\n"
        f"    - u_logic {INV_1} + PLACED ( 0 0 ) N ;\n"
        f"    - TAP_2 {FILLTIE} + PLACED ( 10 0 ) N ;\n"
        f"    - PHY_EDGE_1 {ENDCAP} + PLACED ( 20 0 ) N ;\n"
        f"    - FILLER_0 {FILL_1} + SOURCE DIST + PLACED ( 30 0 ) N ;\n"
        f"    - TAP_1 {FILLTIE} + PLACED ( 40 0 ) N ;\n"
        f"    - u_other {NAND2_1} + PLACED ( 50 0 ) N ;\n"
        "END COMPONENTS\n"
        "NETS 1 ;\n"
        f"    - {FILLTIE} ( u_logic I ) ;\n"
        "END NETS\n"
        "END DESIGN\n"
    )
    MASTERS = (FILLTIE, ENDCAP, FILL_1)

    def test_selects_physical_only_masters_sorted_by_instance(self):
        path = self.write("design.def", self.DEF)
        self.assertEqual(
            lvs._def_physical_only_instances(path, self.MASTERS),
            [
                (FILL_1, "FILLER_0"),
                (ENDCAP, "PHY_EDGE_1"),
                (FILLTIE, "TAP_1"),
                (FILLTIE, "TAP_2"),
            ],
        )

    def test_logic_instances_and_entries_outside_components_excluded(self):
        """Only `COMPONENTS` is scanned: the `NETS` entry whose name happens
        to equal a master is not mistaken for an instance."""
        path = self.write("design.def", self.DEF)
        found = lvs._def_physical_only_instances(path, (FILLTIE,))
        self.assertEqual(found, [(FILLTIE, "TAP_1"), (FILLTIE, "TAP_2")])
        names = {instance for _, instance in found}
        self.assertNotIn("u_logic", names)
        self.assertNotIn("u_other", names)

    def test_no_masters_returns_empty_without_reading(self):
        missing = self.root / "does-not-exist.def"
        self.assertEqual(lvs._def_physical_only_instances(missing, ()), [])

    def test_missing_components_section_raises(self):
        path = self.write("design.def", "VERSION 5.8 ;\nDESIGN x ;\nEND DESIGN\n")
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._def_physical_only_instances(path, self.MASTERS)
        self.assertIn("COMPONENTS", str(ctx.exception))

    def test_unterminated_components_section_raises(self):
        path = self.write(
            "design.def",
            f"DESIGN x ;\nCOMPONENTS 1 ;\n    - TAP_1 {FILLTIE} ;\nEND DESIGN\n",
        )
        with self.assertRaises(lvs.LvsFlowError):
            lvs._def_physical_only_instances(path, self.MASTERS)

    def test_none_of_the_masters_present_raises(self):
        path = self.write("design.def", self.DEF)
        with self.assertRaises(lvs.LvsFlowError) as ctx:
            lvs._def_physical_only_instances(path, (PREFIX + "fill_64",))
        self.assertIn("fill_64", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
