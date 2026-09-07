#!/usr/bin/env python3
"""Time-to-first-valid-output, per PVT corner, from committed evidence.

    python3 sim/tools/time_to_first_valid.py              # per-corner table
    python3 sim/tools/time_to_first_valid.py --check      # assert the README row
    python3 sim/tools/time_to_first_valid.py --rate 500   # DR-0010's proposed rate
    python3 sim/tools/time_to_first_valid.py --tolerance 0.005

What the README row says today
------------------------------
> **>= ~1.28 ms** at 1 Mbps -- an arithmetic floor, not a measurement: 1024
> consecutive raw samples for the start-up health test (1.024 ms) plus 256
> samples of conditioner latency (0.256 ms), which do **not** overlap because
> the conditioner is held flushed while gated.

Two things are missing from that, and this script supplies both:

1. **The oscillator does not start instantly.** The floor above begins counting
   at the first raw sample, as if the entropy source were already running.
   ``sim/tb/ro-array-core-startup/`` measures how long the shipped array
   actually takes to reach a stable period after ``en`` asserts, at every point
   of the 27-point covered grid, and this script extracts a start-up time from
   those edge times rather than assuming one.
2. **The two fixed sample counts are counts, not times.** Turning them into a
   time needs a rate. The README uses the ratified 1 Mbps
   ([DR-0003]); [DR-0010] proposes 500 bps and is **Proposed, not ratified**,
   which changes this row by ~2000x. ``--rate`` makes that explicit instead of
   burying one choice in prose.

How the start-up time is extracted
----------------------------------
The testbench records ten successive rising-edge times per ring. Nine
successive period estimates follow. This script walks them and reports the
elapsed time from ``en``'s assertion to the first edge whose period estimate
agrees with the LAST one to within ``--tolerance`` (default 1 %) **and stays
inside it for every later estimate** -- a first-and-thereafter test, so a
period that crosses the band once on its way past does not count as converged.
If no estimate qualifies the corner is reported as NOT CONVERGED rather than
extrapolated; the tolerance lives here, in a tool a reader can re-run at a
different value, and not frozen into the records.

The array's start-up time is the LATER of its two rings': the XOR node carries
both, so the array is not settled until both are.

What this does NOT do
---------------------
- It does not measure the sampler's own reset-release-to-first-capture
  behaviour. That is one sample clock (``sim/tb/sampler-dff-reset-clocked/``
  shows ``Q`` at full rail on the first rising edge after release, at all 45
  PVT points), and it is added as exactly one sample period below.
- The health-test and conditioner latencies are **behavioural** sample counts
  taken from the shipped RTL's own parameters, not from a transistor-level
  run. Per [DR-0009] that is the right level for them, and it is why those two
  terms carry no corner dependence of their own -- all of this row's PVT
  dependence lives in the oscillator start-up term and in the sample rate.
- It says nothing about whether the early bits are GOOD, only about when the
  block first declares one valid. Early-bit entropy is #12's.

[DR-0003]: ../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0009]: ../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0010]: ../../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _record_parsing import format_corner, parse_corner, parse_values  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"

# `-[0-9]` and not `-`: the sequence number must follow the slug directly, so
# a record from a *variant* testbench whose slug starts with this one (e.g.
# `ro-array-core-startup-extracted`, issue #17's post-layout re-run, which
# shares every PVT corner label with the pre-layout family it is a sibling
# of) can never be silently read as a pre-layout transistor-level point --
# see sim/tools/power_rollup.py's ARRAY_GLOBS for the same rule, established
# first for exactly this failure mode (issue #75's unadopted buffer variant).
STARTUP_GLOB = "*-ro-array-core-startup-[0-9]*.md"

#: DR-0002 start-up health test: STARTUP_SAMPLES = W = 1024 consecutive clean
#: raw samples. Read from design/health_test/rct_apt.v's defaults.
STARTUP_SAMPLES = 1024

#: DR-0008 conditioner: K = 8 blocks of 32 raw bits per 32-bit output word.
#: design/conditioner/crc32_conditioner.py's own K.
CONDITIONER_SAMPLES = 8 * 32

#: One sample clock for the sampler to produce its first raw bit after reset
#: release (sim/tb/sampler-dff-reset-clocked/: Q at full rail on the first
#: rising edge after release, all 45 points).
SAMPLER_SAMPLES = 1

#: DR-0003's ratified raw rate, bits per second. The README's Time-to-first-
#: valid row is stated at this rate.
RATIFIED_RAW_RATE_BPS = 1e6

#: DR-0010 §1's PROPOSED raw rate. Proposed, not ratified.
DR0010_RAW_RATE_BPS = 500.0

#: The README's current arithmetic floor, seconds, at the ratified rate.
README_FLOOR_S = 1.28e-3


class Record:
    def __init__(self, path: Path) -> None:
        text = path.read_text()
        self.stem = path.stem
        self.values = parse_values(text)
        self.process, self.temp_c, self.vdd = parse_corner(text, label=self.stem)

    @property
    def corner(self) -> str:
        return format_corner(self.process, self.temp_c, self.vdd)


def load_startup_records() -> list[Record]:
    return [Record(p) for p in sorted(RECORDS.glob(STARTUP_GLOB))]


def dedupe_by_corner(records: list[Record]) -> list[Record]:
    """One record per PVT corner: the newest measurement of that corner wins.

    Until #78 this family had exactly one generation -- one record per corner,
    nothing to choose between. #78 adopted the per-ring output buffer
    (``DR-0018``), which moves the array's operating point, and re-ran this
    whole 27-point grid against the adopted netlist. Both generations are
    committed and both keep ``status: valid``: ``sim/records/`` is append-only
    and the older ones remain true of the unbuffered array they measured. But
    only one of them describes the array as it now ships, and a tool that
    reports a start-up time for the *shipped* design must not average or race
    the two -- the pre-adoption records are slower, so without this the
    binding corner would be picked from the design that is no longer built.

    Record stems begin with the run's date and ``load_startup_records`` sorts
    them, so "later in the list" means "measured later"; the last record of a
    given corner is the newest. Superseding a record in the
    ``sim/README.md`` sense is a different operation -- it marks a run
    *mistaken*, which these are not -- so it deliberately is not used here.
    """
    best: dict[str, Record] = {}
    for rec in records:
        best[rec.corner] = rec
    return list(best.values())


def ring_edges(rec: Record, ring: int) -> list[float]:
    """The recorded rising-edge times for one ring, in order."""
    out = []
    for i in range(1, 32):
        key = f"t{i}r{ring}_s"
        if key not in rec.values:
            break
        out.append(rec.values[key])
    return out


#: How many consecutive in-band period estimates a corner must show before this
#: script will call it converged. Without a floor here the test is vacuous: the
#: last estimate is always inside its own tolerance band, so "converged by the
#: last edge" would be true of a ring whose period was still growing
#: monotonically. Three is the smallest number that distinguishes a plateau
#: from a pair of points, and it leaves six of the nine recorded estimates free
#: to be part of the settling transient.
MIN_STABLE_PERIODS = 3


def converged_time(edges: list[float], t_en: float, tol: float,
                   min_stable: int = MIN_STABLE_PERIODS):
    """(elapsed start-up time, steady period, index) or (None, period, None).

    The steady period is the last available estimate. Convergence is the first
    estimate that is inside the tolerance band around it AND is followed only
    by estimates that are also inside it -- so a single lucky crossing on the
    way past does not count -- AND that is followed by at least ``min_stable``
    in-band estimates in total, so a run that never settles cannot qualify on
    the strength of its own final point. The start-up time is the elapsed time
    from ``en`` to the edge that OPENS that first converged period.
    """
    if len(edges) < min_stable + 1:
        return None, None, None
    periods = [b - a for a, b in zip(edges, edges[1:])]
    steady = periods[-1]
    inside = [abs(p - steady) <= tol * abs(steady) for p in periods]
    for i in range(len(periods) - min_stable + 1):
        if all(inside[i:]):
            return edges[i] - t_en, steady, i
    return None, steady, None


class CornerResult:
    def __init__(self, rec: Record, tol: float) -> None:
        self.rec = rec
        self.t_en = rec.values.get("en_assert_s", 0.0)
        self.rings = {}
        for ring in (1, 2):
            edges = ring_edges(rec, ring)
            self.rings[ring] = converged_time(edges, self.t_en, tol)
        times = [t for t, _p, _i in self.rings.values() if t is not None]
        self.converged = len(times) == len(self.rings)
        #: The array is settled only when BOTH rings are.
        self.t_startup = max(times) if self.converged else None
        self.periods = {r: p for r, (_t, p, _i) in self.rings.items()}
        #: First XOR-node edge after `en`: when the sampler first sees a moving
        #: input at all, which is earlier than, and not a substitute for, the
        #: settled time above.
        self.t_first_xo = (
            rec.values["t1xo_s"] - self.t_en if "t1xo_s" in rec.values else None
        )
        self.swing_early = rec.values.get("ring_swing_early_v")
        self.swing_late = rec.values.get("ring_swing_late_v")
        self.xo_swing_late = rec.values.get("xo_swing_late_v")

    @property
    def swing_ratio(self):
        if self.swing_early is None or not self.swing_late:
            return None
        return self.swing_early / self.swing_late


def budget(rate_bps: float) -> dict:
    """The fixed, corner-independent sample-count terms, converted to seconds."""
    tsamp = 1.0 / rate_bps
    return {
        "sample_period_s": tsamp,
        "sampler_s": SAMPLER_SAMPLES * tsamp,
        "health_test_s": STARTUP_SAMPLES * tsamp,
        "conditioner_s": CONDITIONER_SAMPLES * tsamp,
        "digital_total_s": (SAMPLER_SAMPLES + STARTUP_SAMPLES + CONDITIONER_SAMPLES) * tsamp,
    }


def _s(x: float) -> str:
    for unit, scale in (("s", 1.0), ("ms", 1e-3), ("us", 1e-6), ("ns", 1e-9), ("ps", 1e-12)):
        if abs(x) >= scale or scale == 1e-12:
            return f"{x / scale:.4g} {unit}"
    return f"{x:g} s"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--rate", type=float, default=RATIFIED_RAW_RATE_BPS,
                   help="raw sample rate in bit/s (default 1e6, DR-0003's ratified row; "
                        "DR-0010 proposes 500)")
    p.add_argument("--tolerance", type=float, default=0.01,
                   help="relative period-convergence band (default 0.01 = 1 %%)")
    p.add_argument("--check", action="store_true",
                   help="exit non-zero if any corner fails to converge, or if the "
                        "total at the ratified rate is not bounded below by the "
                        "README's arithmetic floor")
    args = p.parse_args(argv)

    records = load_startup_records()
    if not records:
        print(f"ERROR: no start-up records found (glob: {STARTUP_GLOB})", file=sys.stderr)
        return 2

    found = len(records)
    records = dedupe_by_corner(records)
    superseded_in_effect = found - len(records)

    results = [CornerResult(r, args.tolerance) for r in records]
    b = budget(args.rate)

    print(f"records          : {len(results)} x {STARTUP_GLOB}")
    if superseded_in_effect:
        print(f"                   ({found} found; {superseded_in_effect} older "
              f"measurement(s) of an already-covered corner not used -- see "
              f"dedupe_by_corner)")
    print(f"raw sample rate  : {args.rate:g} bit/s  (sample period {_s(b['sample_period_s'])})")
    print(f"convergence band : +/-{args.tolerance:.1%} of the last measured period")
    print()
    print("Fixed, corner-independent sample-count terms (behavioural, DR-0009):")
    print(f"  sampler first raw bit after reset release : {SAMPLER_SAMPLES:>5} samples"
          f"  = {_s(b['sampler_s'])}")
    print(f"  DR-0002 start-up health test              : {STARTUP_SAMPLES:>5} samples"
          f"  = {_s(b['health_test_s'])}")
    print(f"  DR-0008 conditioner latency (K = 8)       : {CONDITIONER_SAMPLES:>5} samples"
          f"  = {_s(b['conditioner_s'])}")
    print(f"  {'digital total':<42}{SAMPLER_SAMPLES + STARTUP_SAMPLES + CONDITIONER_SAMPLES:>6}"
          f" samples  = {_s(b['digital_total_s'])}")
    print()

    hdr = (f"| {'corner':<16} | {'T0 ring1':>9} | {'osc start':>10} | {'1st xo':>8} |"
           f" {'swing e/l':>9} | {'total':>10} |")
    rule = "|" + "-" * 18 + "|" + "-" * 11 + "|" + "-" * 12 + "|" + "-" * 10 + "|" \
           + "-" * 11 + "|" + "-" * 12 + "|"
    print(hdr)
    print(rule)

    worst = None
    unconverged = []
    for res in sorted(results, key=lambda r: -(r.t_startup or float("inf"))):
        if not res.converged:
            unconverged.append(res.rec.corner)
            print(f"| {res.rec.corner:<16} | {'':>9} | {'NOT CONVERGED':>10} |"
                  f" {'':>8} | {'':>9} | {'':>10} |")
            continue
        total = res.t_startup + b["digital_total_s"]
        if worst is None or total > worst[0]:
            worst = (total, res)
        ratio = res.swing_ratio
        print(
            f"| {res.rec.corner:<16} | {_s(res.periods[1]):>9} | {_s(res.t_startup):>10} |"
            f" {_s(res.t_first_xo):>8} | {ratio:>9.3f} | {_s(total):>10} |"
        )
    print(rule)
    print()

    if worst is None:
        print("ERROR: no corner converged; nothing to total.", file=sys.stderr)
        return 1

    total, res = worst
    print(f"Binding corner (longest total): {res.rec.corner}  ({res.rec.stem})")
    print(f"  oscillator start-up            : {_s(res.t_startup)}")
    print(f"  digital sample-count terms     : {_s(b['digital_total_s'])}")
    print(f"  TIME-TO-FIRST-VALID            : {_s(total)}")
    print(f"  oscillator share of that total : {res.t_startup / total:.3%}")
    print()
    if abs(args.rate - RATIFIED_RAW_RATE_BPS) / RATIFIED_RAW_RATE_BPS < 1e-9:
        print(f"README row (arithmetic floor)    : >= ~{_s(README_FLOOR_S)}")
        print(f"measured total vs that floor     : {total / README_FLOOR_S:.5f}x")
        print("The floor is not contradicted: it counts only the 1280 fixed digital")
        print("samples, and the measured oscillator start-up is strictly additional.")
    else:
        ratified = max(
            r.t_startup + budget(RATIFIED_RAW_RATE_BPS)["digital_total_s"]
            for r in results if r.converged
        )
        print(f"At this rate the total is {total / ratified:.4g}x the same figure at the")
        print(f"ratified {RATIFIED_RAW_RATE_BPS:g} bit/s ({_s(ratified)}). The rate row is what moves it.")
    print()
    print("Swing check (early window / late window, ring 1): a value near 1 means the")
    print("amplitude had already settled by 15-45 ns after en, i.e. the period-based")
    print("start-up time above is not hiding an amplitude still on its way up.")

    if args.check:
        if unconverged:
            print(f"\nFAIL: {len(unconverged)} corner(s) did not converge: "
                  f"{', '.join(unconverged)}", file=sys.stderr)
            return 1
        worst_ratio = max(
            (r.swing_ratio for r in results if r.swing_ratio is not None), default=1.0
        )
        best_ratio = min(
            (r.swing_ratio for r in results if r.swing_ratio is not None), default=1.0
        )
        if not (0.9 <= best_ratio and worst_ratio <= 1.1):
            print(f"\nFAIL: ring swing has not settled at every corner "
                  f"(early/late ratio spans {best_ratio:.3f}..{worst_ratio:.3f})",
                  file=sys.stderr)
            return 1
        ratified_total = max(
            r.t_startup + budget(RATIFIED_RAW_RATE_BPS)["digital_total_s"]
            for r in results if r.converged
        )
        if ratified_total < README_FLOOR_S:
            print(f"\nFAIL: measured total {_s(ratified_total)} is BELOW the README's "
                  f"arithmetic floor {_s(README_FLOOR_S)} -- the floor claims to be a "
                  "lower bound and would be wrong.", file=sys.stderr)
            return 1
        print(f"\nOK: {len(results)} corners converged; ring swing settled at every one; "
              f"total at the ratified rate ({_s(ratified_total)}) is bounded below by "
              f"the README floor ({_s(README_FLOOR_S)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
