"""build_dut.py: extraction_port_map refusal branches and source audits, offline.

Synthetic extracted netlists only; no klt, ngspice or PDK.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "build_dut", ROOT / "sim" / "tb" / "ro-ring11-pex" / "build_dut.py"
)
bd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bd)

RING = [f"a|y{'' if i == 0 else '$' + str(i)}" for i in range(11)]
NAMED = ["en", "vddr", "vss", "vsubs"]


def gate_line(name, gate, x):
    return [
        f"* device instance ${name} r0 nfet {x},0.0 nfet",
        f"X{name} dd {gate} ss bb nfet_03v3",
    ]


def netlist(header=None, gates=None, resistors=(), header_text=None):
    """Header ports default to RING + NAMED; gates is a list of (net, x)."""
    if header_text is None:
        header_text = ".SUBCKT ro_ring11 " + " ".join(header or RING + NAMED)
    lines = [header_text]
    for i, (net, x) in enumerate(gates or []):
        lines += gate_line(i, net, x)
    for i, (a, b) in enumerate(resistors):
        lines.append(f"R{i} {a} {b} 1.5")
    lines.append(".ENDS")
    return "\n".join(lines) + "\n"


def ring_gates(order):
    """Port RING[k] drives the gate at leftmost position order[k]."""
    return [(RING[k], 100.0 * pos + 5) for k, pos in enumerate(order)]


class WellFormed(unittest.TestCase):
    def test_ring_ports_map_in_leftmost_gate_order(self):
        order = [3, 0, 10, 5, 1, 9, 2, 8, 4, 7, 6]
        got = bd.extraction_port_map(netlist(gates=ring_gates(order)))
        want = [bd.RING_NODES[pos] for pos in order] + NAMED
        self.assertEqual(got, want)
        self.assertEqual(len(got), 15)

    def test_named_ports_unchanged_wherever_they_sit(self):
        header = ["vss", RING[0], "en", *RING[1:6], "vsubs", *RING[6:], "vddr"]
        gates = [(RING[k], 100.0 * k) for k in range(11)]
        got = bd.extraction_port_map(netlist(header=header, gates=gates))
        self.assertEqual(
            got,
            ["vss", "ro", "en", "n1", "n2", "n3", "n4", "n5", "vsubs",
             "n6", "n7", "n8", "n9", "n10", "vddr"],
        )

    def test_leftmost_of_several_gates_decides(self):
        gates = [(RING[k], 100.0 * k + 50) for k in range(11)]
        gates.append((RING[10], 1.0))  # port 10 also drives a far-left gate
        got = bd.extraction_port_map(netlist(gates=gates))
        self.assertEqual(got[10], "ro")
        self.assertEqual(got[0], "n1")

    def test_resistor_chain_resolves_to_gate_cluster(self):
        # Port 4's gate sits behind a three-resistor chain; the chain is
        # written in mixed orientation so union order matters.
        gates = [(RING[k], 100.0 * k) for k in range(11) if k != 4]
        gates.append(("gnet", 400.0))
        res = [("m2", "gnet"), (RING[4], "m1"), ("m2", "m1")]
        got = bd.extraction_port_map(netlist(gates=gates, resistors=res))
        self.assertEqual(got[:11], bd.RING_NODES)

    def test_plus_continuation_on_header_is_joined(self):
        header = ".SUBCKT ro_ring11 " + " ".join(RING[:6]) + "\n+ " + " ".join(RING[6:] + NAMED)
        gates = [(RING[k], 100.0 * k) for k in range(11)]
        got = bd.extraction_port_map(netlist(header_text=header, gates=gates))
        self.assertEqual(got, bd.RING_NODES + NAMED)


class Refusals(unittest.TestCase):
    def assertRefuses(self, text, fragment):
        with self.assertRaises(bd.BuildError) as cm:
            bd.extraction_port_map(text)
        self.assertIn(fragment, str(cm.exception))

    def test_no_subckt(self):
        self.assertRefuses(
            netlist(header_text=".SUBCKT other a b"), "declares no .SUBCKT ro_ring11"
        )

    def test_named_port_missing(self):
        header = RING + ["en", "vddr", "vss"]
        self.assertRefuses(
            netlist(header=header, gates=ring_gates(range(11))),
            "names 'vsubs' 0 times",
        )

    def test_named_port_repeated(self):
        header = RING + NAMED + ["en"]
        self.assertRefuses(
            netlist(header=header, gates=ring_gates(range(11))),
            "names 'en' 2 times",
        )

    def test_wrong_ring_port_count(self):
        header = RING[:10] + NAMED
        self.assertRefuses(
            netlist(header=header, gates=ring_gates(range(10))),
            "expected 11 ring-node ports, extraction has 10",
        )

    def test_ring_port_drives_no_gate(self):
        gates = ring_gates(range(11))[:-1]
        self.assertRefuses(netlist(gates=gates), f"ring port {RING[10]!r} drives no device gate")

    def test_resistor_to_unrelated_net_does_not_supply_a_gate(self):
        gates = ring_gates(range(11))[:-1]
        self.assertRefuses(
            netlist(gates=gates, resistors=[(RING[10], "floating")]), "drives no device gate"
        )

    def test_two_ports_tie_on_leftmost_x(self):
        gates = ring_gates(range(11))
        gates[7] = (RING[7], gates[2][1])
        self.assertRefuses(netlist(gates=gates), "two ring ports tie on leftmost gate x")


DESIGN = """\
* header comment
.subckt ro_ring11 en ro vddr vss wstv=0.5u lstv=1u cld=1f
xg en ro n1 vddr vss ro_nand2
x1 n1 n2 vddr vss ro_stage
.ends
.subckt ro_nand2 a b y vdd vss
m1 y a vss vss nfet
.ends
.subckt ro_stage a y vdd vss
m1 y a vss vss nfet
.ends
xr1 en ro vddr vss ro_ring11 wstv=0.220u lstv=2u
+ cld=0.5f
xr2 en ro2 vddr vss ro_ring11 wstv=1u lstv=1u cld=1f
"""


class SourceAudits(unittest.TestCase):
    def test_audit_accepts_matching_params_across_continuation(self):
        bd.audit_ring1_params(DESIGN)

    def test_audit_rejects_drifted_sizing(self):
        with self.assertRaises(bd.BuildError) as cm:
            bd.audit_ring1_params(DESIGN.replace("lstv=2u", "lstv=3u"))
        self.assertIn("disagrees with xr1", str(cm.exception))

    def test_audit_rejects_missing_instance(self):
        with self.assertRaises(bd.BuildError) as cm:
            bd.audit_ring1_params(DESIGN.replace("xr1 ", "xq1 "))
        self.assertIn("no xr1 ro_ring11 instance", str(cm.exception))

    def test_render_refuses_drifted_sizing(self):
        with self.assertRaises(bd.BuildError):
            bd.render_dut(bd.RING_NODES, DESIGN.replace("cld=0.5f", "cld=9f"))

    def test_committed_dut_matches_committed_source(self):
        self.assertIsNone(bd.dut_source_problem())

    def test_round_trip_dut_is_clean(self):
        header = ["en", "ro", "vddr", "vss"]
        dut = bd.render_dut(header, DESIGN)
        self.assertIsNone(bd.dut_source_problem(dut, DESIGN))

    def test_edited_dut_body_is_reported_with_diff(self):
        dut = bd.render_dut(["en", "ro", "vddr", "vss"], DESIGN)
        problem = bd.dut_source_problem(dut.replace("xg en", "xg vss"), DESIGN)
        self.assertIn("does not match", problem)
        self.assertIn("first differences", problem)

    def test_changed_source_is_reported(self):
        dut = bd.render_dut(["en", "ro", "vddr", "vss"], DESIGN)
        problem = bd.dut_source_problem(dut, DESIGN.replace("m1 y a vss", "m2 y a vss"))
        self.assertIn("does not match", problem)

    def test_dut_without_subckt_is_reported_not_raised(self):
        problem = bd.dut_source_problem("* nothing here\n", DESIGN)
        self.assertIn("no .subckt ro_ring11", problem)

    def test_source_drift_in_params_is_reported_not_raised(self):
        dut = bd.render_dut(["en", "ro", "vddr", "vss"], DESIGN)
        problem = bd.dut_source_problem(dut, DESIGN.replace("lstv=2u", "lstv=3u"))
        self.assertIn("disagrees with xr1", problem)

    def test_unrelated_edits_keep_source_identity(self):
        other = DESIGN.replace("xr2 en ro2", "* note\nxr2 en ro3")
        self.assertEqual(bd.source_identity(DESIGN), bd.source_identity(other))
        self.assertNotEqual(
            bd.source_identity(DESIGN), bd.source_identity(DESIGN.replace("m1 y a", "m9 y a"))
        )


if __name__ == "__main__":
    unittest.main()
