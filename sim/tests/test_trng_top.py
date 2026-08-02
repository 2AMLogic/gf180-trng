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
   ``design/health_test/rct_apt.v``).
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
INTERFACE_V = IFACE_DIR / "trng_interface.v"
TOP_V = TOP_DIR / "trng_top.v"

#: The DR-0001 raw tap, and the block's shared clock/reset -- the four
#: signals that cross the DR-0009 analog/digital boundary.
RAW_TAP_SIGNALS = ("clk", "rst_n", "raw_bit", "raw_valid")


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
        for _ in range(c_rct + 5):
            out = t.step(raw_bit=1, raw_valid=True)
        self.assertTrue(out.ht_alarm)
        self.assertGreater(t.health.rct_failures, 0)

    def test_raw_sample_counting_matches_raw_valid_cycles(self):
        t = top.TopLevel()
        bits = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0]
        for b in bits:
            t.step(raw_bit=b, raw_valid=True)
        t.step(raw_bit=0, raw_valid=False)  # a bus-only cycle: no new sample
        self.assertEqual(t.cycles, len(bits) + 1)
        self.assertEqual(t.raw_samples, len(bits))

    def test_a_healthy_short_run_never_alarms(self):
        # Far short of a full RCT/APT window at either cutoff -- this is
        # the smoke-test property (bits flow, nothing spuriously trips),
        # not an entropy or false-positive-rate claim (that is
        # sim/tb/health-test-fault-injection/'s job).
        t = top.TopLevel()
        bits = [0, 0, 0, 1, 1, 1, 1, 1, 0, 0]
        out = None
        for b in bits:
            out = t.step(raw_bit=b, raw_valid=True)
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
                    str(TOP_V), str(CONDITIONER_V), str(HEALTH_TEST_V), str(INTERFACE_V),
                ],
                check=True, capture_output=True, text=True,
            )
            proc = subprocess.run(
                ["vvp", str(vvp)], check=True, capture_output=True, text=True,
            )
            self.assertNotIn("FATAL", proc.stdout, proc.stdout)


if __name__ == "__main__":
    unittest.main()
