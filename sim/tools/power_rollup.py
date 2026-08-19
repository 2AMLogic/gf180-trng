#!/usr/bin/env python3
"""Whole-block active and idle power, per PVT corner, against the README rows.

    python3 sim/tools/power_rollup.py                 # per-corner table
    python3 sim/tools/power_rollup.py --check         # assert both README rows
    python3 sim/tools/power_rollup.py --rate 500      # DR-0010's proposed rate
    python3 sim/tools/power_rollup.py --no-digital    # measured silicon only

What the README rows say
------------------------
> **Power** -- < 500 uW active, binding at ``ff`` / +10 % supply; < 1 uA idle,
> binding at ``ff`` / +10 % / +125 C (max leakage). **Neither figure has any
> evidence behind it yet.**

This script is that evidence, assembled from committed records rather than
restated. Every term below names the record family it comes from and whether
it is a transistor-level MEASUREMENT or a [DR-0004] Tier 2 ESTIMATE, and the
two are never silently added into one number without saying so.

Active power, per corner
------------------------
    P_active = P_array + P_sampler + P_digital

- ``P_array`` -- the two rings plus the XOR combiner, MEASURED at each corner
  by ``sim/tb/ro-array-core-pvt-q/`` (27 points) and ``sim/tb/
  ro-array-core-power/`` (3 points), as ``p_total_w``.
- ``P_sampler`` -- the two ``sampler_dff`` instances, assembled from
  ``sim/tb/sampler-dff-active-current/``'s per-event charges and the SAME
  corner's own measured ``xo_trans_per_s``:

      I_sampler = R_xo * (d_open * q_d_open + d_shut * q_d_shut)
                + f_clk * (q_clk_xsv + q_clk_xsb)

  with ``d_open = d_shut = 0.5`` (the real clock's 50 % duty -- the master
  transmission gate is transparent for half of every clock period, and the
  flop therefore burns energy at the ENTROPY node's rate for that half). Note
  which rate multiplies which term: the dominant one is ``R_xo``, hundreds of
  megahertz, not the 1 MHz sample clock. Only ``xsb`` sees a moving D; ``xsv``
  has D tied to vdd and contributes the clock term only.
- ``P_digital`` -- conditioner + health tests + interface, ESTIMATED by
  ``design/digital_power_estimate.py`` from the PDK's own Liberty library
  against an enumerated gate inventory. Not a measurement, and labelled as
  such everywhere it appears. Corner-independent within this script: the
  Liberty corner is chosen once, from the two the README's Power row binds at.

Idle current, per corner
------------------------
    I_idle = I_analog + I_digital_leakage

- ``I_analog`` -- rings clamped, reset released, clock parked, MEASURED across
  the full 45-point grid by ``sim/tb/sampler-core-idle-leakage/`` on the whole
  of ``sampler_core``. The worse of the two clock-park states is used.
- ``I_digital_leakage`` -- the same Liberty inventory's leakage. ESTIMATE.

What this does NOT include
--------------------------
- The metastability-hybrid tap (``ro_array_core_meta``, ~187 uW, [DR-0011]) and
  the DR-0016 per-ring liveness digitizer (~81 uW,
  ``sim/tb/ring-liveness-tap-power/``). Neither is instantiated by the shipped
  ``sampler_core``/``trng_top``, and ``design/README.md`` already states that
  the ratified row is measured against the shipped core. ``--with-taps`` adds
  them so the cost of adopting them is visible rather than forgotten.
- Any I/O, level-shifting, clock-generation or reference circuitry outside
  this block. The block does not contain a clock source at all ([DR-0012]).
- Post-layout parasitics. Nothing here has been laid out (#15/#17).

[DR-0004]: ../../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0011]: ../../spec/decision-records/DR-0011-metastability-hybrid-tap-claims-and-scope.md
[DR-0012]: ../../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _record_parsing import format_corner, parse_corner, parse_values  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"
DIGITAL_SCRIPT = REPO_ROOT / "design" / "digital_power_estimate.py"

# `-[0-9]` and not `-`: the sequence number must follow the slug directly, so
# a record from a *variant* testbench whose slug starts with one of these
# (e.g. ro-array-core-power-BUFFERED, issue #75's unadopted buffer mitigation)
# can never be rolled up as if it were the shipped design.
ARRAY_GLOBS = ("*-ro-array-core-pvt-q-[0-9]*.md", "*-ro-array-core-power-[0-9]*.md")
SAMPLER_ACTIVE_GLOB = "*-sampler-dff-active-current-*.md"
IDLE_GLOB = "*-sampler-core-idle-leakage-*.md"

#: README rows.
ACTIVE_BUDGET_W = 500e-6
IDLE_BUDGET_A = 1e-6

#: DR-0003's ratified raw rate; DR-0010 proposes 500 bps (Proposed, not
#: ratified).
RATIFIED_RAW_RATE_BPS = 1e6

#: Fraction of each clock period in which the sampler's master transmission
#: gate is transparent. The real clock is 50 % duty; the active-current deck's
#: own 10/21 duty is a simulation artefact and deliberately does not appear.
DUTY_OPEN = 0.5

#: Liberty corners for the digital estimate, one per README row half.
DIGITAL_CORNER_ACTIVE = "ff_n40C_3v60"
DIGITAL_CORNER_IDLE = "ff_125C_3v60"

#: Measured costs of the two taps that exist but are not instantiated by the
#: shipped block, for --with-taps. Both are quoted at ff/-40C/3.63 V.
TAP_META_W = 187e-6
TAP_LIVENESS_W = 81.3e-6

#: The ``netlist:`` block of a record's front matter, which names the DUT file
#: and pins its blob SHA. Optional: not every record family has a netlist (the
#: device-level decks, for instance, instantiate a PDK model directly), so a
#: record without one reads back as ``None`` rather than failing to parse.
_NETLIST = re.compile(r"^netlist:\s*\n(?:^[ \t]+.*\n)*?^[ \t]+sha:\s*([0-9a-f]+)", re.M)


class Record:
    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.stem = path.stem
        self.values = parse_values(text)
        self.process, self.temp_c, self.vdd = parse_corner(text, label=self.stem)
        #: Blob SHA of the netlist this record's numbers were measured
        #: against, or ``None`` for a record whose deck names no netlist.
        #: This is what identifies the DUT *revision*: two records of the same
        #: family and the same corner that carry different netlist SHAs
        #: measured two different designs, and a tool that means one of them
        #: specifically (rather than "the newest") has to say which.
        m = _NETLIST.search(text)
        self.netlist_sha = m.group(1) if m else None

    @property
    def corner(self) -> str:
        return format_corner(self.process, self.temp_c, self.vdd)


def load(globs) -> list[Record]:
    if isinstance(globs, str):
        globs = (globs,)
    return [Record(p) for g in globs for p in sorted(RECORDS.glob(g))]


def by_corner(records: list[Record], prefer: str | None = None) -> dict[str, Record]:
    """One record per PVT corner: the latest record of the preferred family wins.

    ``prefer`` is a stem substring (e.g. ``"pvt-q"``) naming the preferred
    family, exactly as ``sim/tools/array_sizing.py``'s own
    ``dedupe_by_corner`` uses it. ``load()`` returns records in sorted
    (chronological + sequence-number) order within each glob, so "later in
    the list" means "newer evidence": a later record of the preferred family
    always wins over an earlier one of that SAME family (#78 re-ran the
    ``ro-array-core-pvt-q`` family under the buffer-adoption design change,
    landing new records under the same slug as the pre-adoption ones -- the
    first case in this repository's history where two generations of the
    same corner, same family, both exist). A later NON-preferred record never
    downgrades an already-preferred one, matching the original intent (full
    covered-grid corners win over the 3-point family that overlaps it).
    """
    out: dict[str, Record] = {}
    for rec in records:
        cur = out.get(rec.corner)
        if cur is None or not (prefer and prefer in cur.stem and prefer not in rec.stem):
            out[rec.corner] = rec
    return out


def digital_estimate(corner: str, rate_bps: float) -> dict:
    """Run design/digital_power_estimate.py and read back its JSON."""
    proc = subprocess.run(
        [sys.executable, str(DIGITAL_SCRIPT), "--corner", corner,
         "--raw-rate", repr(rate_bps), "--json"],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"design/digital_power_estimate.py failed ({proc.returncode}):\n{proc.stderr}"
        )
    import json
    return json.loads(proc.stdout)


def sampler_active(sampler: Record, r_xo: float, f_clk: float) -> dict:
    """Sampler active current at one corner, from per-event charge and rates."""
    q_open = abs(sampler.values["q_d_open_c"])
    q_shut = abs(sampler.values["q_d_shut_c"])
    q_clk = abs(sampler.values["q_clkcyc_xsv_c"])
    vdd = sampler.values.get("vdd_mean_v", sampler.vdd)
    i_data = r_xo * (DUTY_OPEN * q_open + (1.0 - DUTY_OPEN) * q_shut)
    #: xsv and xsb each pay one clock-cycle charge. xsv's is measured directly;
    #: xsb's is bounded by the same figure (see that testbench's caveats), and
    #: at 1 MHz the whole term is five orders of magnitude below i_data.
    i_clk = 2.0 * f_clk * q_clk
    return {
        "i_data_a": i_data,
        "i_clk_a": i_clk,
        "i_total_a": i_data + i_clk,
        "p_total_w": (i_data + i_clk) * vdd,
        "q_open_c": q_open,
        "q_shut_c": q_shut,
        "q_clk_c": q_clk,
        "vdd": vdd,
    }


def _w(x: float) -> str:
    for unit, scale in (("W", 1.0), ("mW", 1e-3), ("uW", 1e-6), ("nW", 1e-9), ("pW", 1e-12)):
        if abs(x) >= scale or scale == 1e-12:
            return f"{x / scale:.4g} {unit}"
    return f"{x:g} W"


def _a(x: float) -> str:
    for unit, scale in (("A", 1.0), ("mA", 1e-3), ("uA", 1e-6), ("nA", 1e-9), ("pA", 1e-12)):
        if abs(x) >= scale or scale == 1e-12:
            return f"{x / scale:.4g} {unit}"
    return f"{x:g} A"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--rate", type=float, default=RATIFIED_RAW_RATE_BPS,
                   help="sample-clock rate in Hz (default 1e6, DR-0003's ratified row)")
    p.add_argument("--no-digital", action="store_true",
                   help="report only the transistor-level measured terms")
    p.add_argument("--require-digital", action="store_true",
                   help="fail instead of degrading if the PDK's Liberty libraries "
                        "(and therefore the digital estimate) are unavailable")
    p.add_argument("--with-taps", action="store_true",
                   help="add the two measured but not-instantiated taps "
                        "(metastability hybrid, ring-liveness digitizer)")
    p.add_argument("--check", action="store_true",
                   help="exit non-zero if a required record family is missing or a "
                        "measured term contradicts the record it came from. Does NOT "
                        "fail on a README row being missed -- a missed row is a spec "
                        "question, routed through spec/, not a tool failure.")
    args = p.parse_args(argv)

    arrays = by_corner(load(ARRAY_GLOBS), prefer="pvt-q")
    samplers = by_corner(load(SAMPLER_ACTIVE_GLOB))
    idles = by_corner(load(IDLE_GLOB))

    missing = [name for name, d in
               (("array", arrays), ("sampler-active", samplers), ("idle", idles)) if not d]
    if missing:
        print(f"ERROR: no records for: {', '.join(missing)}", file=sys.stderr)
        return 2

    dig_active = dig_idle = None
    dig_note = ""
    if not args.no_digital:
        # The digital term needs the PDK's Liberty libraries. The record-only
        # arithmetic does not, and CI's PR-blocking path has no PDK -- so a
        # missing PDK degrades to the measured-silicon-only view with a loud
        # note, rather than failing a check that is about the records.
        try:
            dig_active = digital_estimate(DIGITAL_CORNER_ACTIVE, args.rate)
            dig_idle = digital_estimate(DIGITAL_CORNER_IDLE, args.rate)
        except RuntimeError as exc:
            if args.require_digital:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
            dig_note = str(exc).splitlines()[-1] if str(exc).strip() else "unavailable"

    print(f"sample clock     : {args.rate:g} Hz")
    print(f"array records    : {len(arrays)} corners  {', '.join(ARRAY_GLOBS)}")
    print(f"sampler records  : {len(samplers)} corners  {SAMPLER_ACTIVE_GLOB}")
    print(f"idle records     : {len(idles)} corners  {IDLE_GLOB}")
    if dig_active:
        print(f"digital estimate : {DIGITAL_CORNER_ACTIVE} (active) / "
              f"{DIGITAL_CORNER_IDLE} (idle)  -- DR-0004 Tier 2 ESTIMATE, not measured")
    elif dig_note:
        print("digital estimate : UNAVAILABLE -- no PDK Liberty library on this host.")
        print(f"                   ({dig_note})")
        print("                   Totals below are MEASURED SILICON ONLY and are a "
              "lower bound.")
    else:
        print("digital estimate : EXCLUDED (--no-digital)")
    print()

    # ------------------------------------------------------------------ ACTIVE
    print("ACTIVE POWER  (rings + XOR + sampler measured; digital estimated)")
    hdr = (f"| {'corner':<16} | {'R_xo':>10} | {'P_array':>9} | {'P_sampler':>9} |"
           f" {'P_digital':>9} | {'TOTAL':>9} | {'vs 500uW':>8} |")
    rule = ("|" + "-" * 18 + "|" + "-" * 12 + "|" + "-" * 11 + "|" + "-" * 11
            + "|" + "-" * 11 + "|" + "-" * 11 + "|" + "-" * 10 + "|")
    print(hdr)
    print(rule)

    p_dig = dig_active["shipped_total"]["active_w"] if dig_active else 0.0
    if args.with_taps:
        p_dig += TAP_META_W + TAP_LIVENESS_W

    active_rows = []
    for corner, arec in arrays.items():
        srec = samplers.get(corner)
        if srec is None:
            continue
        r_xo = abs(arec.values["xo_trans_per_s"])
        s = sampler_active(srec, r_xo, args.rate)
        p_array = abs(arec.values["p_total_w"])
        total = p_array + s["p_total_w"] + p_dig
        active_rows.append((total, corner, r_xo, p_array, s, total))
    active_rows.sort(reverse=True)
    for total, corner, r_xo, p_array, s, _t in active_rows:
        print(
            f"| {corner:<16} | {r_xo:>10.3e} | {_w(p_array):>9} | {_w(s['p_total_w']):>9} |"
            f" {_w(p_dig):>9} | {_w(total):>9} | {total / ACTIVE_BUDGET_W:>7.1%} |"
        )
    print(rule)
    print()

    worst_active = active_rows[0]
    print(f"Worst active corner: {worst_active[1]}  -> {_w(worst_active[0])}"
          f"  = {worst_active[0] / ACTIVE_BUDGET_W:.1%} of the < 500 uW row")
    s = worst_active[4]
    print(f"  entropy source (measured)   : {_w(worst_active[3]):>10}"
          f"   {worst_active[3] / ACTIVE_BUDGET_W:6.1%}")
    print(f"  sampler, data term (measured): {_w(s['i_data_a'] * s['vdd']):>10}"
          f"   {s['i_data_a'] * s['vdd'] / ACTIVE_BUDGET_W:6.1%}"
          f"   ({s['q_open_c']:.3e} C/transition x {worst_active[2]:.3e} /s x {DUTY_OPEN})")
    print(f"  sampler, clock term (measured): {_w(s['i_clk_a'] * s['vdd']):>9}"
          f"   {s['i_clk_a'] * s['vdd'] / ACTIVE_BUDGET_W:6.1%}")
    if dig_active:
        print(f"  digital (ESTIMATE)          : {_w(p_dig):>10}"
              f"   {p_dig / ACTIVE_BUDGET_W:6.1%}")
    headroom = ACTIVE_BUDGET_W - worst_active[3]
    non_array = worst_active[0] - worst_active[3]
    print(f"  headroom left by the entropy source: {_w(headroom)}; "
          f"everything else needs {_w(non_array)} ({non_array / headroom:.1%} of it)")
    print()

    # -------------------------------------------------------------------- IDLE
    print("IDLE CURRENT  (rings clamped, reset released, clock parked)")
    hdr = (f"| {'corner':<16} | {'I_analog':>10} | {'I_digital':>10} | {'TOTAL':>10} |"
           f" {'vs 1uA':>8} |")
    rule = ("|" + "-" * 18 + "|" + "-" * 12 + "|" + "-" * 12 + "|" + "-" * 12
            + "|" + "-" * 10 + "|")
    print(hdr)
    print(rule)
    i_dig = dig_idle["shipped_total"]["leakage_a"] if dig_idle else 0.0
    idle_rows = []
    for corner, rec in idles.items():
        i_analog = max(abs(rec.values["i_idle_clklo_a"]), abs(rec.values["i_idle_clkhi_a"]))
        idle_rows.append((i_analog + i_dig, corner, i_analog))
    idle_rows.sort(reverse=True)
    for total, corner, i_analog in idle_rows[:6]:
        print(f"| {corner:<16} | {_a(i_analog):>10} | {_a(i_dig):>10} | {_a(total):>10} |"
              f" {total / IDLE_BUDGET_A:>7.0%} |")
    if len(idle_rows) > 6:
        print(f"| {'... ' + str(len(idle_rows) - 6) + ' quieter corners':<16} |"
              f" {'':>10} | {'':>10} | {'':>10} | {'':>8} |")
    print(rule)
    print()
    worst_idle = idle_rows[0]
    print(f"Worst idle corner: {worst_idle[1]}  -> {_a(worst_idle[0])}"
          f"  = {worst_idle[0] / IDLE_BUDGET_A:.0%} of the < 1 uA row")
    print(f"  analog, whole sampler_core (measured): {_a(worst_idle[2]):>10}"
          f"   {worst_idle[2] / IDLE_BUDGET_A:6.1%}")
    if dig_idle:
        t = dig_idle["shipped_total"]
        print(f"  digital leakage (ESTIMATE)          : {_a(i_dig):>10}"
              f"   {i_dig / IDLE_BUDGET_A:6.1%}"
              f"   [{t['flops']} flops, {t['cells']} cells, no power gating]")
        print(f"    input-state range of that estimate: "
              f"{_a(t['leakage_min_a'])} .. {_a(t['leakage_max_a'])}")
    print()

    if args.check:
        problems = []
        if len(arrays) < 27:
            problems.append(f"only {len(arrays)} array corners (expected >= 27)")
        if len(samplers) < 45:
            problems.append(f"only {len(samplers)} sampler-active corners (expected >= 45)")
        if len(idles) < 45:
            problems.append(f"only {len(idles)} idle corners (expected >= 45)")
        for corner, rec in idles.items():
            a = abs(rec.values["i_idle_clklo_a"])
            b = abs(rec.values["i_idle_clklo_prev_a"])
            if a > 0 and abs(a - b) / a > 0.05:
                problems.append(
                    f"{rec.stem}: idle self-check failed, the two windows disagree "
                    f"({a:.4g} vs {b:.4g} A) -- that state was not static"
                )
        for corner, rec in samplers.items():
            if rec.values.get("qv_post_v", 0) < 0.5 * rec.vdd:
                problems.append(f"{rec.stem}: xsv never captured (qv_post_v too low)")
            if rec.values.get("qb_post_v", 0) < 0.5 * rec.vdd:
                problems.append(f"{rec.stem}: xsb never captured (qb_post_v too low)")
        if problems:
            print("FAIL:", file=sys.stderr)
            for prob in problems:
                print(f"  - {prob}", file=sys.stderr)
            return 1
        print(f"OK: {len(arrays)} array / {len(samplers)} sampler / {len(idles)} idle "
              "corners present; every idle record's two-window self-check agrees to "
              "within 5 %; every sampler record witnesses both flops capturing.")
        print("NOTE: --check deliberately does not fail on a README row being missed. "
              "A missed row is a spec question and goes through spec/, per CLAUDE.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
