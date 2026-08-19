#!/usr/bin/env python3
"""Does one per-ring buffer ahead of the XOR combiner remove the 28.6x
ring-to-ring coupling issue #51 / PR #67 measured? (issue #75)

    python3 sim/tools/array_coupling_buffer_variant.py           # the table
    python3 sim/tools/array_coupling_buffer_variant.py --check   # gate the finding

Like ``sim/tools/array_coupling_variants.py`` this is a *derivation*, not a
simulation: it reads only records already committed under ``sim/records/``
and does arithmetic on them. It needs neither ngspice nor the PDK, and it
writes nothing.

The question (issue #75)
-------------------------
``sim/characterization-array-ring-coupling.md`` (issue #51 / PR #67) measured
that a ring driving the XOR combiner alongside a switching neighbour shows
``sigma_1`` 28.6x higher than the same ring with a quiet neighbour, at
tt/27 C/3.30 V -- charge injected backwards into the ring node through the
gate-drain/gate-source capacitance of the combiner's input stage, a shared
electrical node by construction. ``layout/floorplan/README.md`` (issue #16)
proposes a mitigation -- one minimum-width inverter buffer per ring, between
the ring node and every consumer -- and explicitly declines to adopt it
because nothing measured whether it works. This script reads the fourth
variant deck (``sim/tb/ro-array-coupling-xor-driven-buffered/``) that closes
that gap and states the answer against BOTH of issue #51's controls: the
standalone control (1.00x) and the static-load control (1.06x), so the
result says how much of the 28.6x the buffer removes, not only that it moved.

Sigma here is RAW at the fixed injected level, exactly as in
``array_coupling_variants.py`` -- comparable across these rows, not physical
jitter, and no entropy claim may be built on it (DR-0004 tiering).

A note on tense, since #78
--------------------------
#78 / ``DR-0018`` adopted the buffer, so this script is now retrospective: it
states the case the decision record acted on, against the design that was
shipping at the time. That makes its record selection the mirror image of
every other tool's. The shipped-design rollups want the *newest* measurement
of a corner; this one wants the *pre-adoption* one on the unbuffered side, and
pins it by netlist blob SHA so a later re-run of the same family cannot drift
into it -- see ``UNBUFFERED_NETLIST_SHA``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import power_rollup as pr  # noqa: E402
from starved_cell_jitter_energy import Record, RecordError, _lags, _loglog_slope  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"

#: The one corner this experiment (and issue #51's) is run at.
CORNER = "tt/27/3.30"

#: The power-binding corner. This is where layout/floorplan/README.md's
#: ~24.4 uW estimate for the mitigation was made, so it is where the
#: measurement that replaces that estimate has to be read.
#: Plain `process/temp_c/vdd`, matching `power_rollup.Record.corner` (issue
#: #104 unified every sim/tools/*.py corner format on this one; before that
#: power_rollup.py rendered it with `C`/`V` units, `"ff/-40C/3.63V"`).
POWER_CORNER = "ff/-40/3.63"

#: The shipped array's own power record family, and the buffered variant's.
#: `-[0-9]` on the first is load-bearing: without it the glob also matches the
#: buffered records and the "unbuffered" column would silently become the
#: buffered one (the same trap the shipped rollups carry a guard for).
POWER_GLOB_UNBUFFERED = "*-ro-array-core-power-[0-9]*.md"
POWER_GLOB_BUFFERED = "*-ro-array-core-power-buffered-*.md"

#: ``design/ro_array_core.spice``'s blob SHA as it stood BEFORE #78 adopted
#: the per-ring output buffer ([DR-0018]) -- the netlist every pre-adoption
#: ``ro-array-core-power`` record was measured against.
#:
#: This pin is what the family glob alone cannot do. Adopting the buffer
#: changed the shipped netlist and #78 re-ran ``ro-array-core-power`` against
#: it, so ``sim/records/`` now holds two generations of ``ff/-40C/3.63V``
#: under the SAME family slug: the pre-adoption unbuffered array, and the
#: adopted buffered one. Both are ``status: valid`` and both stay committed --
#: the records are append-only and each is true of the design it measured. But
#: this script's "unbuffered" column is not "the newest measurement of that
#: corner"; it is specifically *the design the buffer was adopted instead of*,
#: and taking the newest record of the family silently makes the column
#: buffered, compares buffered against buffered, and reduces the power gate
#: below to testbench-to-testbench noise (~2 uW, in the wrong direction).
#:
#: The four shipped-design rollups fixed alongside this one (``power_rollup.
#: by_corner``, ``array_sizing.dedupe_by_corner``, ``worst_corner_entropy.
#: shipped_points``, ``time_to_first_valid.dedupe_by_corner``) resolve the
#: same two generations the opposite way, and correctly: every claim they make
#: is about the array *as it ships*, so for them the newest record of a corner
#: wins. This script is the one place that means the older generation on
#: purpose, so it is the one place that has to name it -- and it names it by
#: the DUT's blob SHA rather than by record stem, because what makes that
#: record the baseline is which netlist it measured, not when it was run.
#:
#: [DR-0018]: ../../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md
UNBUFFERED_NETLIST_SHA = "339e858e0010f1ca26412919af47621d40dedf93"

#: ``(label, record glob)``, in the order the comparisons are meant to be read.
#: The first three are issue #51's own committed records (PR #67); the last two
#: are this issue's buffered pair.
#:
#: The two UNBUFFERED globs end ``-[0-9]*`` deliberately: without it they also
#: match this issue's own ``…-buffered-…`` records and the "unbuffered" rows
#: would silently become the buffered ones.
#:
#: The buffered pair is a PAIR on purpose. Reading the buffered driven deck
#: against issue #51's unbuffered controls mixes two changes -- the buffer's
#: isolation and the buffer's lighter load, which moves the ring's operating
#: point. ``xor-static-buffered`` holds the load fixed at the buffered
#: operating point with the neighbour on a rail, so
#: ``xor-driven-buffered`` / ``xor-static-buffered`` differs in exactly one
#: thing (does the neighbour switch), the same one-change ratio that gives
#: 28.6x unbuffered.
VARIANTS = [
    ("1 control", "*-ro-ring5-starved-jitter-long-[0-9]*.md"),
    ("2 xor-static", "*-ro-array-coupling-xor-static-[0-9]*.md"),
    ("3 xor-driven", "*-ro-array-coupling-xor-driven-[0-9]*.md"),
    ("5 xor-static-buffered", "*-ro-array-coupling-xor-static-buffered-*.md"),
    ("6 xor-driven-buffered", "*-ro-array-coupling-xor-driven-buffered-*.md"),
]


class Variant:
    def __init__(self, label: str, record: Record) -> None:
        self.label = label
        self.rec = record
        self.period = record.values["period"]
        self.lags = _lags(record)
        self.sigma = {L: record.values[f"sigma_{L}"] for L in self.lags}
        self.exponent = _loglog_slope(
            [float(L) for L in self.lags], [self.sigma[L] for L in self.lags]
        )

    @property
    def spread_1(self) -> float | None:
        return self.rec.spread("sigma_1")


def load_variants() -> list[Variant]:
    out: list[Variant] = []
    for label, glob in VARIANTS:
        matches = []
        for path in sorted(RECORDS.glob(glob)):
            rec = Record(path)
            if rec.corner != CORNER or "sigma_1" not in rec.values:
                continue
            matches.append(rec)
        if not matches:
            raise RecordError(
                f"variant {label!r}: no sim/records/{glob} record at {CORNER} carries a "
                "sigma_1, so this variant cannot be compared"
            )
        # Latest record wins; earlier ones (including failed/superseded runs)
        # stay on file as append-only evidence. A failed run's record has no
        # sigma_1 value (measurements come back "no data"), so it never
        # reaches this filter in the first place -- see the "sigma_1" in
        # rec.values check above.
        out.append(Variant(label, matches[-1]))
    return out


# --------------------------------------------------------------------------
# what the buffer costs -- measured, not estimated
# --------------------------------------------------------------------------


def _power_record(glob: str, netlist_sha: str | None = None) -> pr.Record:
    """The newest power record at ``POWER_CORNER`` matching ``glob``.

    ``netlist_sha`` narrows the search to records measured against one
    specific revision of the DUT netlist before "newest" is applied, which is
    how the unbuffered baseline stays unbuffered now that #78 has re-run this
    family against the adopted (buffered) netlist -- see
    ``UNBUFFERED_NETLIST_SHA``. Record stems begin with the run date and the
    glob is sorted, so the last surviving match is the newest one.
    """
    all_at_corner = [
        rec for rec in (pr.Record(p) for p in sorted(RECORDS.glob(glob)))
        if rec.corner == POWER_CORNER
    ]
    matches = [
        rec for rec in all_at_corner
        if netlist_sha is None or rec.netlist_sha == netlist_sha
    ]
    if not matches:
        if all_at_corner and netlist_sha is not None:
            raise RecordError(
                f"sim/records/{glob} has {len(all_at_corner)} record(s) at "
                f"{POWER_CORNER}, but none measured netlist {netlist_sha[:12]} "
                "-- the baseline this comparison is against is no longer on "
                "file, and sim/records/ is append-only, so it should be"
            )
        raise RecordError(
            f"no sim/records/{glob} record at {POWER_CORNER}, so the buffer's "
            "measured cost cannot be read"
        )
    return matches[-1]


def _branches(rec: pr.Record) -> dict[str, float]:
    """Per-branch active power in watts, as magnitudes.

    The charge integrators in these decks run negative (they meter a current
    flowing *out* of the supply node), so every recorded power is negative by
    construction; the rollup reads magnitudes and so does this.
    """
    vdd = abs(rec.values["vdd_mean_v"]) if "vdd_mean_v" in rec.values else rec.vdd
    out = {
        "ring 1": abs(rec.values["i_r1_a"]) * vdd,
        "ring 2": abs(rec.values["i_r2_a"]) * vdd,
        "buffer 1": abs(rec.values.get("i_buf1_a", 0.0)) * vdd,
        "buffer 2": abs(rec.values.get("i_buf2_a", 0.0)) * vdd,
        "combiner xa1": abs(rec.values["i_tree_a"]) * vdd,
    }
    out["TOTAL"] = abs(rec.values["p_total_w"])
    return out


def _rollup_total(p_entropy_w: float, r_xo: float, rate_bps: float,
                  sampler: pr.Record, p_dig_w: float | None) -> tuple[float, float]:
    """(entropy + sampler [+ digital]) at ``POWER_CORNER``, and the sampler part.

    Exactly ``sim/tools/power_rollup.py``'s own active-row arithmetic, called
    with a different entropy-source figure -- so substituting the buffered
    array into the block budget is the committed rollup's arithmetic and not a
    second, hand-rolled one.
    """
    s = pr.sampler_active(sampler, r_xo, rate_bps)
    total = p_entropy_w + s["p_total_w"] + (p_dig_w or 0.0)
    return total, s["p_total_w"]


def report_power(rate_bps: float) -> dict:
    """Print the measured cost of the mitigation; return the two rollup totals."""
    unbuf = _power_record(POWER_GLOB_UNBUFFERED, netlist_sha=UNBUFFERED_NETLIST_SHA)
    buf = _power_record(POWER_GLOB_BUFFERED)
    b_un, b_bu = _branches(unbuf), _branches(buf)

    print(f"\n\nwhat the buffer COSTS, at {POWER_CORNER} (the power-binding corner)")
    print(f"  unbuffered: {unbuf.stem}  (pre-adoption netlist "
          f"{UNBUFFERED_NETLIST_SHA[:12]})")
    print(f"  buffered  : {buf.stem}\n")
    header = f"{'branch':<16}{'unbuffered':>13}{'buffered':>13}{'delta':>13}"
    print(header)
    print("-" * len(header))
    for name in ("ring 1", "ring 2", "buffer 1", "buffer 2", "combiner xa1", "TOTAL"):
        u, b = b_un[name], b_bu[name]
        delta = b - u
        pct = f" ({delta / u * 100:+.1f}%)" if u else " (new)"
        print(f"{name:<16}{u * 1e6:12.2f}u{b * 1e6:12.2f}u{delta * 1e6:12.2f}u{pct}")

    f_un, f_bu = unbuf.values["f_r1"], buf.values["f_r1"]
    e_un, e_bu = abs(unbuf.values["e_cycle_r1_j"]), abs(buf.values["e_cycle_r1_j"])
    print(
        f"\n  ring 1 under the lighter load: f_r1 {f_un / 1e6:.1f} -> {f_bu / 1e6:.1f} MHz "
        f"({(f_bu / f_un - 1) * 100:+.1f}%), per-cycle energy "
        f"{e_un:.4e} -> {e_bu:.4e} J ({(e_bu / e_un - 1) * 100:+.1f}%)"
    )

    # ---- substitute into the block's active rollup ------------------------
    samplers = pr.by_corner(pr.load(pr.SAMPLER_ACTIVE_GLOB))
    sampler = samplers.get(POWER_CORNER)
    if sampler is None:
        print(f"\n  (no sampler record at {POWER_CORNER}: block rollup not substituted)")
        return {}
    p_dig = None
    try:
        p_dig = pr.digital_estimate(pr.DIGITAL_CORNER_ACTIVE, rate_bps)["shipped_total"]["active_w"]
    except RuntimeError:
        print("\n  digital term UNAVAILABLE (no PDK Liberty on this host) -- the two")
        print("  totals below are measured-silicon-only and are a FLOOR, but their")
        print("  DIFFERENCE is exact, because the digital term is identical in both.")

    t_un, s_un = _rollup_total(b_un["TOTAL"], abs(unbuf.values["xo_trans_per_s"]),
                               rate_bps, sampler, p_dig)
    t_bu, s_bu = _rollup_total(b_bu["TOTAL"], abs(buf.values["xo_trans_per_s"]),
                               rate_bps, sampler, p_dig)
    print(f"\n  block ACTIVE rollup at {POWER_CORNER}, buffered array substituted in")
    print(f"  (same arithmetic as sim/tools/power_rollup.py, entropy source swapped):")
    print(f"    unbuffered: {b_un['TOTAL'] * 1e6:7.1f}u entropy + {s_un * 1e6:5.2f}u sampler"
          + (f" + {p_dig * 1e6:5.2f}u digital" if p_dig is not None else "")
          + f" = {t_un * 1e6:7.1f}u  ({t_un / pr.ACTIVE_BUDGET_W:5.1%} of the < 500 uW row)")
    print(f"    buffered  : {b_bu['TOTAL'] * 1e6:7.1f}u entropy + {s_bu * 1e6:5.2f}u sampler"
          + (f" + {p_dig * 1e6:5.2f}u digital" if p_dig is not None else "")
          + f" = {t_bu * 1e6:7.1f}u  ({t_bu / pr.ACTIVE_BUDGET_W:5.1%} of the < 500 uW row)")
    print(f"    net effect of adopting the buffer: {(t_bu - t_un) * 1e6:+.1f} uW "
          f"({(t_bu / t_un - 1) * 100:+.1f}%)")
    return {"unbuffered_w": t_un, "buffered_w": t_bu, "digital_w": p_dig}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="array_coupling_buffer_variant.py",
        description="Does one per-ring buffer ahead of the XOR combiner remove "
        "the 28.6x ring-to-ring coupling issue #51 measured? (issue #75)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero unless the buffered variant's sigma_1 is BELOW the "
        "unbuffered xor-driven variant's -- a minimal sanity gate that the "
        "mitigation moved sigma_1 in the isolating direction, not a claim "
        "about how much",
    )
    parser.add_argument(
        "--rate", type=float, default=pr.RATIFIED_RAW_RATE_BPS, metavar="BPS",
        help="raw output rate the sampler and digital terms of the block rollup "
             "are priced at (default: DR-0003's ratified 1 Mbps, the same "
             "default sim/tools/power_rollup.py uses)",
    )
    parser.add_argument(
        "--no-power", action="store_true",
        help="skip the power section (the coupling table needs no power records)",
    )
    args = parser.parse_args(argv)

    try:
        variants = load_variants()
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    control = variants[0]
    by_label = {v.label.split()[-1]: v for v in variants}
    static = by_label["xor-static"]
    driven = by_label["xor-driven"]
    static_buf = by_label["xor-static-buffered"]
    buffered = by_label["xor-driven-buffered"]

    print(
        f"issue #75 -- does a per-ring buffer ahead of the XOR combiner remove\n"
        f"the coupling issue #51 measured, at {CORNER} (process/degC/V)?\n"
        f"sigma is RAW at the injected level: comparable across these rows, not\n"
        f"physical jitter.\n"
    )

    lags = control.lags
    header = (
        f"{'variant':<24} {'T0 (s)':>11} "
        + "".join(f"{'L=' + str(L):>11}" for L in lags)
        + f"{'expon':>7}{'spr_1':>8}"
    )
    print(header)
    print("-" * len(header))
    for v in variants:
        spread = v.spread_1
        print(
            f"{v.label:<24} {v.period:11.4e} "
            + "".join(f"{v.sigma[L]:11.4e}" for L in lags)
            + f"{v.exponent:7.3f}"
            + (f"{100 * spread:7.1f}%" if spread is not None else f"{'n/a':>8}")
        )

    ratio_to_control = buffered.sigma[1] / control.sigma[1]
    ratio_to_static = buffered.sigma[1] / static.sigma[1]
    ratio_to_driven = buffered.sigma[1] / driven.sigma[1]
    driven_ratio_to_control = driven.sigma[1] / control.sigma[1]

    print("\nratio to the two #51 controls at lag 1, buffered driven variant")
    print(f"  vs standalone control (#51's 1.00x baseline): {ratio_to_control:6.2f}x")
    print(f"  vs xor-static        (#51's 1.06x baseline): {ratio_to_static:6.2f}x")
    print(f"  vs xor-driven, the unbuffered 28.6x case   : {ratio_to_driven:6.3f}x")
    print(f"  xor-driven vs standalone control, unbuffered (pre-mitigation "
          f"baseline for the row above): {driven_ratio_to_control:6.2f}x")

    # The attributing comparison. Every other ratio above spans TWO changes
    # (the buffer's isolation AND the buffer's lighter load, which moves the
    # ring's operating point). This one spans exactly one -- whether the
    # neighbour switches -- and it is the direct counterpart of the 28.6x
    # issue #51 got from the same ratio without the buffer.
    coupling_unbuffered = driven.sigma[1] / static.sigma[1]
    coupling_buffered = buffered.sigma[1] / static_buf.sigma[1]
    print("\nTHE COUPLING FACTOR -- driven/static at the SAME operating point")
    print("  (one change between numerator and denominator: does the neighbour switch)")
    print(f"  unbuffered: {driven.sigma[1]:.4e} / {static.sigma[1]:.4e} = "
          f"{coupling_unbuffered:8.2f}x   (issue #51's headline)")
    print(f"  buffered  : {buffered.sigma[1]:.4e} / {static_buf.sigma[1]:.4e} = "
          f"{coupling_buffered:8.2f}x")
    if coupling_unbuffered > 1.0:
        removed = 1.0 - (coupling_buffered - 1.0) / (coupling_unbuffered - 1.0)
        print(f"  -> the buffer removes {removed * 100:.2f}% of the coupling excess, "
              f"leaving {coupling_buffered:.2f}x")
        print(f"  -> squared (what DR-0007 §2 substitutes): "
              f"{coupling_unbuffered ** 2:.0f}x over-statement becomes "
              f"{coupling_buffered ** 2:.2f}x")

    print("\noperating points (the reason the matched control exists)")
    for v in (static, driven, static_buf, buffered):
        print(f"  {v.label:<24} T0 = {v.period:.4e} s")

    rollup = {}
    if not args.no_power:
        try:
            rollup = report_power(args.rate)
        except Exception as exc:  # noqa: BLE001 - reported, never swallowed
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    if args.check:
        failed = False
        # The gate is on the ATTRIBUTING ratio, not on the raw sigma: the
        # claim sim/characterization-ring-buffer-mitigation.md makes is that
        # the coupling factor collapses, and the coupling factor is
        # driven/static at one operating point.
        if coupling_buffered < coupling_unbuffered:
            print(
                f"\nOK: the coupling factor falls from {coupling_unbuffered:.2f}x "
                f"(unbuffered) to {coupling_buffered:.2f}x (buffered) at {CORNER} -- "
                "the mitigation isolates the ring."
            )
        else:
            print(
                f"\nFAIL: the coupling factor is {coupling_buffered:.2f}x buffered "
                f"against {coupling_unbuffered:.2f}x unbuffered at {CORNER} -- the "
                "buffer did not isolate the ring.",
                file=sys.stderr,
            )
            failed = True
        # The power gate is a DIRECTION check, not a budget check: the block
        # budget row is power_rollup.py's to enforce. What this asserts is the
        # claim sim/characterization-ring-buffer-mitigation.md makes -- that
        # adopting the buffer does not COST active power at the power-binding
        # corner, which is the opposite of what the floorplan's estimate
        # projected and therefore the part most worth guarding.
        if rollup:
            if rollup["buffered_w"] <= rollup["unbuffered_w"]:
                print(
                    f"OK: the buffered block rollup ({rollup['buffered_w'] * 1e6:.1f} uW) "
                    f"is no higher than the unbuffered one "
                    f"({rollup['unbuffered_w'] * 1e6:.1f} uW) at {POWER_CORNER}."
                )
            else:
                print(
                    f"FAIL: the buffered block rollup ({rollup['buffered_w'] * 1e6:.1f} uW) "
                    f"is ABOVE the unbuffered one ({rollup['unbuffered_w'] * 1e6:.1f} uW) "
                    f"at {POWER_CORNER} -- the mitigation costs active power after all.",
                    file=sys.stderr,
                )
                failed = True
        if failed:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
