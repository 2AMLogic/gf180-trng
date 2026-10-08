#!/usr/bin/env python3
"""Hold sim/characterization-analog-summary.md to the tools it quotes (#313).

That document is the analog partition's T1 item-8 aggregate, and
signoff/evidence/characterization-analog.generic.json pins its sha256. The
pin proves the document has not changed since it was cited, but it says
nothing about whether the document still agrees with the evidence. This test
covers that second question: every row-level figure the summary quotes from
``power_rollup.py``, ``time_to_first_valid.py``, ``worst_corner_entropy.py``
or ``layout/floorplan/reports/area.json`` must still be what that source
reports today.

Each check is a pair: a snippet that must appear in the summary, and a
pattern that must appear in the tool output it was copied from. If a record
family moves (a digital rebuild, a re-run array family), the tool output
moves, this test fails, and the summary has to be re-read and re-pinned in
the same change. Needs no PDK and no ngspice. The tools read committed
records only.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
SUMMARY = SIM_DIR / "characterization-analog-summary.md"
AREA = REPO_ROOT / "layout" / "floorplan" / "reports" / "area.json"
TOOLS = SIM_DIR / "tools"

RUNS = {
    "power": ["power_rollup.py"],
    "power_analog": ["power_rollup.py", "--no-digital"],
    # --check prints the same report plus its own OK verdict line, and exits
    # non-zero if the records stop supporting the stated corner or floor.
    "ttfv": ["time_to_first_valid.py", "--check"],
    "entropy": ["worst_corner_entropy.py", "--check"],
}

#: (snippet in the summary, tool run, regex over that run's stdout)
QUOTED = [
    # Power, active
    ("entropy source **393.2 µW**", "power", r"entropy source \(measured\)\s*:\s*393\.2 uW"),
    ("sampler **16.88 µW**", "power", r"\| ff/-40/3\.63\s*\|[^|]*\|[^|]*\|\s*16\.88 uW"),
    ("**410 µW = 82.0 %**", "power_analog", r"Worst active corner: ff/-40/3\.63\s*-> 410 uW\s*= 82\.0%"),
    ("**758.2 µW = 151.6 %**", "power", r"Worst active corner: ff/-40/3\.63\s*-> 758\.2 uW\s*= 151\.6%"),
    ("digital term is 348.2 µW", "power", r"digital \(MEASURED-at-gate-level\): 348\.2 uW"),
    ("`ff_125C_3v60`/`rc-max`", "power", r"active binds ff_125C_3v60/rc-max"),
    ("106.8 µW headroom", "power", r"headroom left by the entropy source: 106\.8 uW"),
    # Power, idle
    ("**32.77 nA**", "power", r"analog, whole sampler_core \(measured\):\s*32\.77 nA"),
    ("**2.211 µA = 221 %**", "power", r"Worst idle corner: ff/125/3\.63\s*-> 2\.211 uA\s*= 221%"),
    ("digital leakage at 2.178 µA", "power", r"digital leakage \(MEASURED-at-gate-level\): 2\.178 uA"),
    # Time-to-first-valid and the rate-binding period
    ("**1.281 ms**, binding at `ss`/125 °C/2.97 V", "ttfv", r"Binding corner \(longest total\): ss/125/2\.97"),
    ("**1.281 ms**", "ttfv", r"TIME-TO-FIRST-VALID\s*: 1\.281 ms"),
    ("**12.41 ns**, 0.001 %", "ttfv", r"oscillator start-up\s*: 12\.41 ns"),
    ("0.001 % of the total", "ttfv", r"oscillator share of that total : 0\.001%"),
    ("all 27 corners converged", "ttfv", r"OK: 27 corners converged"),
    ("**12.3 ns** pre-layout", "ttfv", r"\| ss/125/2\.97\s*\|\s*12\.3 ns"),
    # Entropy source
    ("**`ss`/125 °C/3.63 V** at every jitter-energy constant", "entropy",
     r"OK: ss/125/3\.63 minimizes Q over all 27 covered grid points at every constant"),
    ("**678.1 bps**", "entropy", r"ss/125/3\.63\s+8\.1376e-03\s+1\.36x\s+678\.1"),
    ("**4458 bps**", "entropy", r"ss/125/3\.63\s+5\.3501e-02\s+8\.92x\s+4458"),
    ("**9412 bps**", "entropy", r"ss/125/3\.63\s+1\.1294e-01\s+18\.82x\s+9412"),
    ("1.356× (pre-layout)", "entropy", r"ss/125/3\.63\s+8\.1376e-03\s+1\.36x"),
    # Health-test bias ceiling
    ("`p_major` = 0.5078", "entropy", r"at ss/-40/3\.63\): p_major = 0\.5078"),
    ("RCT false-alarm probability at 2.842e-24", "entropy", r"RCT: Pr\(81 identical consecutive samples\) = 2\.842e-24"),
    ("APT at 1.395e-86", "entropy", r"APT: Pr\(X >= 824\) .* = 1\.395e-86"),
    # Monte Carlo
    ("mean 1.0691 (sd 0.0018)", "entropy", r"mean 1\.0691\s+sd 0\.0018"),
    ("1.0726 (sd 0.0013)", "entropy", r"mean 1\.0726\s+sd 0\.0013"),
    ("−265.2 mV (nominal)", "entropy", r"offset from ideal mid-supply 1\.650 V: -265\.2 mV"),
    ("−274.8 mV (`ss`/125 °C/3.63 V)", "entropy", r"systematic offset -274\.8 mV"),
    ("14.78 mV and 15.02 mV sd", "entropy", r"mismatch sd 15\.02 mV vs nominal-corner 14\.78 mV"),
]


class AnalogSummaryAgreesWithItsTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = SUMMARY.read_text()
        cls.out: dict[str, str] = {}
        for key, argv in RUNS.items():
            proc = subprocess.run(
                [sys.executable, str(TOOLS / argv[0]), *argv[1:]],
                capture_output=True, text=True, cwd=REPO_ROOT, check=False,
            )
            if proc.returncode != 0:
                raise AssertionError(f"{argv} exited {proc.returncode}:\n{proc.stderr}")
            cls.out[key] = proc.stdout

    def test_every_quoted_figure_is_what_the_tool_prints(self) -> None:
        for snippet, run, pattern in QUOTED:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, self.summary, "summary no longer quotes this figure")
                self.assertRegex(self.out[run], pattern,
                                 f"{RUNS[run]} no longer prints what the summary quotes")

    def test_one_mbps_shortfall_is_the_ratio_of_the_tool_rates(self) -> None:
        # Q is proportional to the sample period, so the 1 Mbps shortfall is
        # 1e6 / R_max at each constant -- arithmetic on the tool's own R_max.
        rates = [float(m) for m in re.findall(
            r"^ss/125/3\.63\s+\S+\s+\S+x\s+(\S+)$", self.out["entropy"], re.M)]
        self.assertEqual(len(rates), 3, "expected one ss/125/3.63 row per constant")
        shortfalls = [round(1e6 / r) for r in rates]
        self.assertIn(
            f"about {shortfalls[0]}×, {shortfalls[1]}× and {shortfalls[2]}×", self.summary)
        self.assertIn(
            f"{shortfalls[2]}× to {shortfalls[0]}× below 1 Mbps", self.summary)

    def test_extracted_idle_substitution_arithmetic(self) -> None:
        sys.path.insert(0, str(TOOLS))
        import power_rollup  # noqa: PLC0415

        digital_a = power_rollup.digital_measured(1e6)["leakage_a"]
        total_ua = (digital_a + 127.04e-9) * 1e6
        self.assertIn(f"about {total_ua:.3f} µA", self.summary)

    def test_analog_area_share(self) -> None:
        analog = json.loads(AREA.read_text())["rollup"]["subtotals"]["analog"]
        area = f"{analog['area_um2']:,.1f}".replace(",", " ")
        self.assertIn(f"**{area} µm² = {analog['share_of_budget_pct']:.2f} %**", self.summary)
        self.assertEqual(sorted(analog["regions"]), ["combiner_sampler", "ring1", "ring2"])


if __name__ == "__main__":
    unittest.main()
