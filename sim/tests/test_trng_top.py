#!/usr/bin/env python3
"""Unit tests for the top-level integration (#27).

Three groups:

1. **Pinout cross-check.** The one thing this issue's own curation flagged
   as the likeliest failure mode ("an OUT_MODE or health-alarm signal wired
   backwards") is checked mechanically here: the raw tap's signal names on
   the transistor-level side (``design/trng_top.spice``'s exported
   ``.subckt`` signature, which wraps ``design/sampler_core.spice``
   unchanged) must be exactly the names the digital blocks' own RTL ports
   declare (``design/conditioner/crc32_conditioner.v``,
   ``design/health_test/rct_apt.v``). The DR-0016 per-ring liveness taps
   cross the same boundary and are checked the same way -- including the
   scalar-pin-to-vector-index mapping, which no waveform would reveal.
2. **Behavioural wiring (`trng_top.TopLevel`).** The three real block models
   wired together produce the same cross-block behaviour
   ``sim/tb/interface-regfile/run_demo.py``'s stand-in health-test counter
   already demonstrated for the conditioner/interface pair, now with the
   real ``rct_apt.HealthTest`` closing the ``startup_req`` loop.
3. **RTL wiring (`trng_top.v`).** Compiles and elaborates against the three
   real RTL modules under Icarus Verilog. Skipped (not failed) when
   ``iverilog``/``vvp`` are not installed, the same way
   ``sim/tests/test_interface.py`` does it.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
DESIGN_DIR = REPO_ROOT / "design"
TOP_DIR = DESIGN_DIR / "trng_top"
IFACE_DIR = DESIGN_DIR / "interface"

sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(TOP_DIR))
sys.path.insert(0, str(DESIGN_DIR / "conditioner"))
sys.path.insert(0, str(DESIGN_DIR / "health_test"))
sys.path.insert(0, str(IFACE_DIR))

import regmap  # noqa: E402
import rct_apt as ht  # noqa: E402
import trng_top as top  # noqa: E402

TRNG_TOP_SPICE = DESIGN_DIR / "trng_top.spice"
SAMPLER_CORE_SPICE = DESIGN_DIR / "sampler_core.spice"
CONDITIONER_V = DESIGN_DIR / "conditioner" / "crc32_conditioner.v"
HEALTH_TEST_V = DESIGN_DIR / "health_test" / "rct_apt.v"
RING_LIVENESS_V = DESIGN_DIR / "health_test" / "ring_liveness.v"
INTERFACE_V = IFACE_DIR / "trng_interface.v"
TOP_V = TOP_DIR / "trng_top.v"

#: The DR-0001 raw tap, and the block's shared clock/reset -- the four
#: signals that cross the DR-0009 analog/digital boundary.
RAW_TAP_SIGNALS = ("clk", "rst_n", "raw_bit", "raw_valid")

#: The DR-0016 per-ring liveness taps, which cross the same boundary: one
#: already-digitized sample per ring. ``design/xschem/sampler_core.sch``
#: names them per-ring (scalar pins, 1-based like ro1/ro2); the RTL carries
#: them as one ``ring_bit[N_RINGS-1:0]`` vector because ``ring_liveness.v``
#: is parameterised in N_RINGS. The mapping between the two is
#: ``ring_bit<i+1>`` -> ``ring_bit[i]``.
RING_TAP_PINS = ("ring_bit1", "ring_bit2")


def bit(word: int, register: regmap.Register, name: str) -> int:
    """One STATUS/CTRL field out of a register value, by name."""
    f = next(f for f in register.fields if f.name == name)
    return (word >> f.lsb) & ((1 << f.width) - 1)


def _subckt_ports(spice_path: Path, name: str) -> list[str]:
    """The port list of ``.subckt <name> ...`` in a generated netlist.

    Netlists are re-wrapped at a fixed column by ``design/netlist.py`` and
    may continue the ``.subckt`` line onto ``+`` lines, so this joins
    continuations the same way ``netlist.py`` itself does before parsing.
    """
    joined: list[str] = []
    for line in spice_path.read_text().splitlines():
        stripped = line.lstrip()
        if stripped.startswith("+") and joined:
            joined[-1] = f"{joined[-1]} {stripped[1:].strip()}"
        else:
            joined.append(line)
    for line in joined:
        m = re.match(rf"^\.subckt\s+{re.escape(name)}\s+(.*)$", line.strip())
        if m:
            return m.group(1).split()
    raise AssertionError(f"no '.subckt {name}' line found in {spice_path}")


def _verilog_module_ports(v_path: Path, module: str) -> set[str]:
    """The port names declared in ``module <module> #(...) ( ... );``.

    A small, deliberately permissive regex (this repo's RTL is
    hand-written, not a stress test for a Verilog parser): comments are
    stripped first (they routinely contain parens, e.g. "(IEEE 802.3)",
    which would otherwise unbalance the paren walk below), then every
    ``input``/``output``/``inout`` declaration is collected from
    ``module <module>`` up to the ``);`` that ends its (optional
    parameter list followed by) port list -- two separate paren groups
    for a parameterised module, which is why reaching depth 0 does not
    stop the walk on its own: it only stops once the next non-space
    character is not another ``(``.
    """
    text = re.sub(r"//[^\n]*", "", v_path.read_text())
    start = text.index(f"module {module}")
    i = text.index("(", start)
    depth = 0
    j = i
    while True:
        c = text[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                k = j + 1
                while k < len(text) and text[k].isspace():
                    k += 1
                if k < len(text) and text[k] == "(":
                    j = k
                    continue
                break
        j += 1
    port_block = text[i : j + 1]
    return set(re.findall(r"(?:input|output|inout)\s+(?:reg|wire)?\s*(?:\[[^\]]*\]\s*)?(\w+)", port_block))


class PinoutCrossCheckTests(unittest.TestCase):
    """The pinout-mismatch class of bug DR-0009 leaves no mixed-signal
    co-simulation to catch (see design/trng_top/README.md), so it is
    checked by name here instead."""

    def test_trng_top_wraps_sampler_core_unchanged(self):
        top_ports = _subckt_ports(TRNG_TOP_SPICE, "trng_top")
        sampler_ports = _subckt_ports(SAMPLER_CORE_SPICE, "sampler_core")
        self.assertEqual(
            top_ports, sampler_ports,
            "design/xschem/trng_top.sch's own pin order must track "
            "sampler_core's .subckt signature exactly -- see the "
            "description on sampler_core.sym",
        )

    def test_raw_tap_signals_are_on_the_transistor_level_boundary(self):
        top_ports = set(_subckt_ports(TRNG_TOP_SPICE, "trng_top"))
        for sig in RAW_TAP_SIGNALS:
            self.assertIn(sig, top_ports)

    def test_raw_tap_signals_match_the_conditioner_rtl(self):
        ports = _verilog_module_ports(CONDITIONER_V, "trng_conditioner_crc32")
        for sig in RAW_TAP_SIGNALS:
            self.assertIn(sig, ports, f"{sig} missing from trng_conditioner_crc32's ports")

    def test_raw_tap_signals_match_the_health_test_rtl(self):
        ports = _verilog_module_ports(HEALTH_TEST_V, "trng_health_test")
        for sig in RAW_TAP_SIGNALS:
            self.assertIn(sig, ports, f"{sig} missing from trng_health_test's ports")

    def test_raw_bit_raw_valid_match_the_interface_rtl(self):
        # clk/rst_n are shared by the whole sampler-clock domain; raw_bit/
        # raw_valid are the two signals every one of the three digital
        # blocks consumes directly from the raw tap.
        ports = _verilog_module_ports(INTERFACE_V, "trng_interface")
        for sig in ("clk", "rst_n", "raw_bit", "raw_valid"):
            self.assertIn(sig, ports, f"{sig} missing from trng_interface's ports")

    def test_health_test_and_interface_agree_on_the_startup_req_name(self):
        # The signal design/interface/README.md's block diagram draws as
        # `ht_fail_* --> latch --> ht_alarm, gate --> startup_req`: the one
        # feedback path across the three digital blocks, and exactly the
        # kind of connection a rename on one side would silently break.
        health_ports = _verilog_module_ports(HEALTH_TEST_V, "trng_health_test")
        iface_ports = _verilog_module_ports(INTERFACE_V, "trng_interface")
        for sig in ("startup_req", "ht_fail_rct", "ht_fail_apt", "ht_startup_pass"):
            self.assertIn(sig, health_ports, sig)
            self.assertIn(sig, iface_ports, sig)


class RingLivenessPinoutTests(unittest.TestCase):
    """DR-0016's taps cross the same analog/digital boundary the raw tap
    does, so they get the same by-name check -- plus one the raw tap does not
    need, because two scalar schematic pins meet one RTL vector here."""

    def test_the_ring_taps_leave_the_transistor_level_side(self):
        top_ports = _subckt_ports(TRNG_TOP_SPICE, "trng_top")
        sampler_ports = _subckt_ports(SAMPLER_CORE_SPICE, "sampler_core")
        for pin in RING_TAP_PINS:
            self.assertIn(pin, top_ports, f"{pin} missing from trng_top.spice")
            self.assertIn(pin, sampler_ports, f"{pin} missing from sampler_core.spice")

    def test_there_is_one_ring_tap_pin_per_ring_in_the_rtl_vector(self):
        """A schematic that digitizes two rings and RTL that monitors three
        (or one) is exactly the mismatch a picture cannot catch."""
        top_ports = _subckt_ports(TRNG_TOP_SPICE, "trng_top")
        pins = [p for p in top_ports if re.fullmatch(r"ring_bit\d+", p)]
        self.assertEqual(sorted(pins), sorted(RING_TAP_PINS))
        text = re.sub(r"//[^\n]*", "", TOP_V.read_text())
        m = re.search(r"parameter\s+integer\s+N_RINGS\s*=\s*(\d+)", text)
        self.assertIsNotNone(m, "trng_top.v declares no N_RINGS parameter")
        self.assertEqual(int(m.group(1)), len(pins))

    def test_the_ring_tap_pins_are_numbered_from_one_like_the_ring_nodes(self):
        """`ring_bit1` is ring 1 (`ro1`), and `trng_top.v` documents the
        off-by-one to `ring_bit[0]`. Locking the schematic-side numbering
        here is what makes that documented mapping checkable."""
        core_ports = _subckt_ports(TRNG_TOP_SPICE, "ro_array_core")
        for i, pin in enumerate(RING_TAP_PINS, start=1):
            self.assertEqual(pin, f"ring_bit{i}")
            self.assertIn(f"ro{i}", core_ports, f"ro{i} missing from ro_array_core")

    def test_the_ring_digitizers_are_the_raw_taps_own_cell(self):
        """DR-0016 "Digitization": the per-ring digitizer is `sampler_dff`,
        unmodified -- no new analog cell was designed for the monitor. In the
        netlist that is literally four instances of one subcircuit."""
        text = SAMPLER_CORE_SPICE.read_text()
        body = text.split(".subckt sampler_core", 1)[1].split(".ends", 1)[0]
        instances = [ln.split() for ln in body.splitlines() if ln.startswith("x")]
        dffs = [ln for ln in instances if ln[-1] == "sampler_dff"]
        self.assertEqual(len(dffs), 2 + len(RING_TAP_PINS))
        driven = {ln[4] for ln in dffs}
        for pin in RING_TAP_PINS:
            self.assertIn(pin, driven)

    def test_the_liveness_monitor_and_the_interface_agree_on_the_alarm_path(self):
        """DR-0016 "Failure behavior": ring_stuck_any is a third source of
        DR-0002's latch. That is one connection, and a rename on either side
        would break it silently."""
        rl_ports = _verilog_module_ports(RING_LIVENESS_V, "trng_ring_liveness")
        iface_ports = _verilog_module_ports(INTERFACE_V, "trng_interface")
        self.assertIn("ring_stuck_any", rl_ports)
        self.assertIn("ht_fail_ring", iface_ports)
        top = re.sub(r"//[^\n]*", "", TOP_V.read_text())
        self.assertRegex(top, r"\.ht_fail_ring\s*\(\s*ring_stuck_any\s*\)")


class TopLevelBehaviouralTests(unittest.TestCase):
    """trng_top.TopLevel: the three real block models, wired."""

    def test_construction_uses_the_draft_h0_default(self):
        t = top.TopLevel()
        self.assertEqual(t.health.c_rct, ht.c_rct(ht.H0))
        self.assertEqual(t.health.c_apt, ht.c_apt(ht.H0))

    def test_a_stuck_raw_source_latches_the_alarm_and_gates_data(self):
        # C_RCT samples of the same value trips the RCT, which (per
        # design/interface/README.md's contract) latches HT_ALARM and gates
        # the conditioned path -- the cross-block behaviour this assembly
        # exists to demonstrate, now with the real health test instead of
        # interface-regfile/run_demo.py's stand-in counter.
        t = top.TopLevel()
        c_rct = t.health.c_rct
        out = None
        for i in range(c_rct + 5):
            # Both rings kept alive on purpose, so this test still isolates
            # the combined-tap RCT failure now that a stuck ring is a second
            # way into the same alarm (DR-0016).
            out = t.step(raw_bit=1, raw_valid=True, ring_bit=(i % 2, (i + 1) % 2))
        self.assertTrue(out.ht_alarm)
        self.assertGreater(t.health.rct_failures, 0)
        self.assertEqual(bit(t.iface.status_value(), top.STATUS, "HT_FAIL_RING"), 0)

    def test_raw_sample_counting_matches_raw_valid_cycles(self):
        t = top.TopLevel()
        bits = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0]
        for b in bits:
            t.step(raw_bit=b, raw_valid=True)
        t.step(raw_bit=0, raw_valid=False)  # a bus-only cycle: no new sample
        self.assertEqual(t.cycles, len(bits) + 1)
        self.assertEqual(t.raw_samples, len(bits))

    def test_a_dead_ring_latches_the_alarm_the_combined_tap_cannot_see(self):
        """The whole point of DR-0016, end to end through the assembly: ring
        1 freezes while the raw tap keeps producing a plausible stream (the
        surviving ring still drives the XOR), so RCT/APT stay silent -- and
        HT_ALARM still fires, from HT_FAIL_RING alone."""
        t = top.TopLevel()
        bits = [0, 1, 1, 0, 1, 0, 0, 1] * 40      # never a run near C_RCT
        out = None
        for i in range(t.liveness.c_live + 5):
            out = t.step(
                raw_bit=bits[i % len(bits)], raw_valid=True,
                # ring 1 stuck at 1; ring 2 alive and toggling.
                ring_bit=(1, i % 2),
            )
        self.assertEqual(t.health.rct_failures, 0)
        self.assertEqual(t.health.apt_failures, 0)
        self.assertTrue(out.ht_alarm)
        status = t.iface.status_value()
        self.assertEqual(bit(status, top.STATUS, "HT_FAIL_RING"), 1)
        self.assertEqual(bit(status, top.STATUS, "HT_FAIL_RCT"), 0)
        self.assertEqual(bit(status, top.STATUS, "HT_FAIL_APT"), 0)
        self.assertEqual(t.liveness.stuck_events[1], [])

    def test_the_dead_ring_gate_leaves_the_raw_path_alone(self):
        """DR-0016 inherits DR-0001 §5 verbatim: the raw tap is how an
        integrator diagnoses the dead ring, so the gate must not take it."""
        t = top.TopLevel()
        for i in range(t.liveness.c_live + 40):
            t.step(raw_bit=i % 2, raw_valid=True, ring_bit=(0, 0))
        self.assertTrue(t.iface.alarm)
        self.assertGreater(len(t.iface.raw_fifo), 0)

    def test_both_rings_alive_never_trips_the_liveness_monitor(self):
        t = top.TopLevel()
        out = None
        for i in range(t.liveness.c_live * 3):
            out = t.step(raw_bit=i % 2, raw_valid=True, ring_bit=(i % 2, (i // 3) % 2))
        self.assertFalse(out.ht_alarm)
        self.assertEqual(t.liveness.stuck_events, [[], []])

    def test_omitting_ring_bit_holds_every_ring_at_zero(self):
        """The default is documented as "an unwired caller sees all-zero,
        which is what a dead ring looks like" -- so it must actually alarm
        rather than quietly never firing."""
        t = top.TopLevel()
        for _ in range(t.liveness.c_live):
            t.step(raw_bit=1, raw_valid=False)
        self.assertEqual([len(e) for e in t.liveness.stuck_events], [1, 1])

    def test_a_healthy_short_run_never_alarms(self):
        # Far short of a full RCT/APT window at either cutoff -- this is
        # the smoke-test property (bits flow, nothing spuriously trips),
        # not an entropy or false-positive-rate claim (that is
        # sim/tb/health-test-fault-injection/'s job).
        t = top.TopLevel()
        bits = [0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
        out = None
        for i, b in enumerate(bits):
            out = t.step(raw_bit=b, raw_valid=True, ring_bit=(i % 2, (i + 1) % 2))
        self.assertFalse(out.ht_alarm)
        self.assertEqual(t.health.rct_failures, 0)
        self.assertEqual(t.health.apt_failures, 0)


@unittest.skipUnless(
    shutil.which("iverilog") and shutil.which("vvp"),
    "Icarus Verilog not installed -- trng_top.v is not compile-checked here",
)
class RtlWiringTests(unittest.TestCase):
    """trng_top.v elaborates against the three real synthesisable modules,
    with no unresolved port or width mismatch."""

    def test_trng_top_compiles_and_elaborates(self):
        with tempfile.TemporaryDirectory() as tmp:
            vvp = Path(tmp) / "trng_top.vvp"
            subprocess.run(
                [
                    "iverilog", "-g2012", "-I", str(IFACE_DIR),
                    "-o", str(vvp),
                    str(TOP_V), str(CONDITIONER_V), str(HEALTH_TEST_V),
                    str(RING_LIVENESS_V), str(INTERFACE_V),
                ],
                check=True, capture_output=True, text=True,
            )
            proc = subprocess.run(
                ["vvp", str(vvp)], check=True, capture_output=True, text=True,
            )
            self.assertNotIn("FATAL", proc.stdout, proc.stdout)


if __name__ == "__main__":
    unittest.main()
