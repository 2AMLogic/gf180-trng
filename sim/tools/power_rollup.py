#!/usr/bin/env python3
"""Whole-block active and idle power, per PVT corner, against the README rows.

    python3 sim/tools/power_rollup.py                 # per-corner table
    python3 sim/tools/power_rollup.py --check         # assert both README rows
    python3 sim/tools/power_rollup.py --rate 500      # DR-0010's proposed rate
    python3 sim/tools/power_rollup.py --no-digital    # measured silicon only

What the README rows say
------------------------
> **Power** -- < 500 uW active, binding at ``ff`` / +10 % supply; < 1 uA idle,
> binding at ``ff`` / +10 % / +125 C (max leakage).

This script is that evidence, assembled from committed records rather than
restated. Every term below names the record family it comes from and whether
it is a transistor-level MEASUREMENT, a MEASURED-at-gate-level liberty-power
result ([DR-0021]), or a [DR-0004] Tier 2 ESTIMATE, and none of the three are
ever silently added into one number without saying so.

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
- ``P_digital`` -- conditioner + health tests + interface + [#171]'s
  power-delivery cells, **MEASURED-at-gate-level** ([DR-0021]) from the
  synthesized, placed and routed ``trng_top`` digital section:
  ``sim/tools/digital_corner_characterization.py``'s own worst-corner figure
  over the committed ``sim/records/*-digital-sta-power-*.md`` family (15
  corners, 5 liberty decks x 3 interconnect decks), rate-scaled from its own
  1 MHz/20 MHz pair. Per [DR-0023] this REPLACES
  ``design/digital_power_estimate.py``'s [DR-0004] Tier 2 ESTIMATE as the
  figure that feeds the totals below; the estimate is still computed and
  printed alongside it, as context, because it is the pre-synthesis
  prediction the measurement is checked against -- not because it still
  decides anything. "MEASURED-at-gate-level" and not bare "MEASURED":
  [DR-0021] section 3 forbids citing a ``level: gate`` liberty-power result as a
  measured supply current, which is exactly the distinction this label
  exists to preserve.

Idle current, per corner
------------------------
    I_idle = I_analog + I_digital_leakage

- ``I_analog`` -- rings clamped, reset released, clock parked, MEASURED across
  the full 45-point grid by ``sim/tb/sampler-core-idle-leakage/`` on the whole
  of ``sampler_core``. The worse of the two clock-park states is used.
- ``I_digital_leakage`` -- the same gate-level record family's worst-corner
  leakage current. **MEASURED-at-gate-level** ([DR-0021]/[DR-0023]), same
  scope and same replacement-of-the-estimate rule as ``P_digital`` above.

Scope note (per [DR-0023])
---------------------------
The measured digital figure's scope is **wider** than the estimate's: all
2502 logical instances Yosys/OpenROAD placed for ``trng_top``'s digital
section, plus 6136 tapcell/endcap/filler cells [#171] added for the power
delivery network -- against the estimate's 1655-cell, three-block,
logic-only inventory. That is the actual as-built digital section, so it is
the right scope for a whole-block rollup even though it is not an
apples-to-apples re-run of the estimate's inventory.

What this does NOT include
--------------------------
- The metastability-hybrid tap (``ro_array_core_meta``, ~187 uW, [DR-0011]).
  It is not instantiated by the shipped ``sampler_core``/``trng_top``;
  ``--with-taps`` adds it so the cost of adopting it is visible rather than
  forgotten.
- The DR-0016 per-ring liveness samplers ``xsr1``/``xsr2`` ARE instantiated by
  ``design/sampler_core.spice`` (#65) and are therefore a REQUIRED ledger term
  (#463), not an optional tap. Their term comes from ``sim/tb/
  sampler-core-liveness-active/`` records (``*-sampler-core-liveness-active-NN``)
  at each corner that has one; a corner without a record is an explicit GAP, its
  total is printed as a lower bound, and ``inventory`` below says so. The
  historical 81.3 uW constant from ``sim/tb/ring-liveness-tap-power/`` (an
  unbuffered array, a 10 ns clock) is never added to a total.
- Any I/O, level-shifting, clock-generation or reference circuitry outside
  this block. The block does not contain a clock source at all ([DR-0012]).
- Post-layout parasitics beyond the digital section's own routed DEF. The
  analog block has not been laid out (#15/#17).
- A per-net switching-activity annotation. Both the measured and the estimated
  digital figures share the SAME declared uniform 0.25 transitions/net/cycle
  activity (deliberately, so the two are comparable); neither is this design's
  real, data-dependent activity. [DR-0023]'s Follow-up names the annotation
  that would replace the assumption with a measurement.

[DR-0004]: ../../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0011]: ../../spec/decision-records/DR-0011-metastability-hybrid-tap-claims-and-scope.md
[DR-0012]: ../../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0021]: ../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
[DR-0023]: ../../spec/decision-records/DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import digital_corner_characterization as dcc  # noqa: E402
from _record_parsing import format_corner, parse_corner, parse_status, parse_values  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS = REPO_ROOT / "sim" / "records"
DIGITAL_SCRIPT = REPO_ROOT / "design" / "digital_power_estimate.py"

# `-[0-9]` and not `-`: the sequence number must follow the slug directly, so
# a record from a *variant* testbench whose slug starts with one of these
# (e.g. ro-array-core-power-BUFFERED, issue #75's unadopted buffer mitigation)
# can never be rolled up as if it were the shipped design.
ARRAY_GLOBS = ("*-ro-array-core-pvt-q-[0-9]*.md", "*-ro-array-core-power-[0-9]*.md")
# Same `-[0-9]` rule as ARRAY_GLOBS above, and for the same reason: issue #17
# added `sampler-core-idle-leakage-extracted` (a post-layout sibling sharing
# every PVT corner label with this pre-layout family), which a bare `-*`
# glob would silently roll up as if it were the pre-layout shipped-design
# measurement.
SAMPLER_ACTIVE_GLOB = "*-sampler-dff-active-current-[0-9]*.md"
IDLE_GLOB = "*-sampler-core-idle-leakage-[0-9]*.md"
#: The shipped xsr1/xsr2 liveness samplers (#463), same `-[0-9]` slug rule.
LIVENESS_GLOB = "*-sampler-core-liveness-active-[0-9]*.md"

SAMPLER_CORE_NETLIST = REPO_ROOT / "design" / "sampler_core.spice"

#: The active-power ledger, one row per term: which ``sampler_core`` instances
#: (or, for the digital section, which external block) the term accounts for and
#: where its evidence comes from. ``required`` terms are in the default total.
#: ``inventory_check`` fails if an instance is covered by no term (a missing
#: term) or by two (double counting). Idle is a separate, whole-sampler_core
#: measurement and is deliberately NOT a row here (see ``IDLE_SCOPE``).
LEDGER_TERMS = (
    {"name": "array", "covers": ("xdut",), "required": True,
     "evidence": "ro-array-core-pvt-q / ro-array-core-power (rings, ring buffers, XOR)"},
    {"name": "sampler_raw", "covers": ("xsb", "xsv"), "required": True,
     "evidence": "sampler-dff-active-current (per-event charges) x xo rate"},
    {"name": "liveness", "covers": ("xsr1", "xsr2"), "required": True,
     "evidence": "sampler-core-liveness-active (this term plus the taps' loading of the array)"},
)

#: What the idle row's ``sampler-core-idle-leakage`` measurement spans. It is run
#: on the whole ``sampler_core``, so xsr1/xsr2 leakage is ALREADY inside it; the
#: liveness active term must not (and does not) add a second idle term.
IDLE_SCOPE = "sampler_core"

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

#: Liberty corners for `design/digital_power_estimate.py`'s CONTEXT-only
#: comparison figure (see `digital_measured()` docstring for the term that
#: actually feeds the totals below, per DR-0023). One per README row half.
DIGITAL_CORNER_ACTIVE = "ff_n40C_3v60"
DIGITAL_CORNER_IDLE = "ff_125C_3v60"

#: Measured cost of the metastability-hybrid tap, which exists but is not
#: instantiated by the shipped block, for --with-taps. Quoted at ff/-40C/3.63 V.
TAP_META_W = 187e-6
#: HISTORICAL context only, never added to any total (#463): the liveness tap
#: as measured on the UNBUFFERED array at a 10 ns clock (ring-liveness-tap-power,
#: ff/-40C/3.63 V). The shipped samplers are measured by LIVENESS_GLOB records.
HISTORICAL_TAP_LIVENESS_W = 81.3e-6

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
        #: ``valid`` or ``superseded`` (``sim/README.md``); a record with any
        #: other lifecycle raises here, naming the record.
        self.status = parse_status(text, label=self.stem)
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


def load(globs, *, include_superseded: bool = False) -> list[Record]:
    """Records matching ``globs``, chronologically within each glob.

    Records marked ``status: superseded`` were invalidated (mistaken or
    misconfigured runs) and are excluded unless ``include_superseded`` is
    set for an explicit historical read. Older records that remain
    ``status: valid`` are always returned, so design-revision comparisons
    keep working.
    """
    if isinstance(globs, str):
        globs = (globs,)
    recs = [Record(p) for g in globs for p in sorted(RECORDS.glob(g))]
    return recs if include_superseded else [r for r in recs if r.status == "valid"]


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
    """Run design/digital_power_estimate.py and read back its JSON.

    CONTEXT ONLY as of [DR-0023]: this is the [DR-0004] Tier 2 pre-synthesis
    prediction, still computed and printed for comparison, but it no longer
    feeds the totals below -- see ``digital_measured()``.
    """
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


def digital_measured(rate_bps: float) -> dict:
    """Digital section active/idle power, MEASURED-at-gate-level ([DR-0021]),
    from the committed ``sim/records/*-digital-sta-power-*.md`` family --
    this is the term [DR-0023] uses in place of ``digital_estimate()``'s
    ESTIMATE.

    Needs no PDK: unlike the estimate, this reads committed evidence records,
    the same ones ``sim/tools/digital_corner_characterization.py`` aggregates.
    Raises ``dcc.RecordError`` if that family is missing or malformed, exactly
    the failure mode a caller should treat the same way a missing array/
    sampler/idle record family is treated.

    **Corner selection**: the worst of the swept 15-corner set (5 liberty
    decks x 3 interconnect decks) for each quantity independently -- the same
    ``max_1mhz_corner`` / ``max_leakage_corner`` ``sim/tools/
    digital_corner_characterization.py``'s own ``power()`` derives and
    ``--check`` holds to its recorded verdict. This deliberately does NOT
    reuse the two corners the ESTIMATE was pinned to
    (``DIGITAL_CORNER_ACTIVE``/``DIGITAL_CORNER_IDLE``, chosen to match where
    the README row's OWN target text says the row binds): now that the
    digital term dominates the active side, the digital section's own worst
    corner (``ff_125C_3v60``/``max``) is a different corner from the one the
    entropy source binds active power at (``ff_n40C_3v60``), and using each
    term's own worst case is the same conservative convention this script
    already applies to the idle row's two clock-park states.

    **Rate scaling**: the record family carries two fixed clock rates (1 MHz
    and 20 MHz -- the P&R run's own implementation constraint). Every
    non-leakage watt in a liberty power report is ``toggles/sec x energy/
    toggle`` at the declared activity, i.e. linear in the clock rate; leakage
    is not. So ``P(rate) = leakage + (P_1MHz - leakage) * (rate / 1MHz)`` is
    an exact algebraic re-derivation of the SAME model at a different rate,
    not a new approximation -- checked against the committed family's own
    1 MHz/20 MHz pair, which agrees with this formula to better than 2e-6
    relative at every one of the 15 corners.
    """
    records = dcc.load()
    p = dcc.power(records)
    leak_w = p["max_leakage_w"]
    dyn_w_at_1mhz = p["max_1mhz_w"] - leak_w
    active_w = leak_w + dyn_w_at_1mhz * (rate_bps / RATIFIED_RAW_RATE_BPS)
    # Leakage does not depend on the interconnect corner (it is a device-only
    # quantity), so `p["max_leakage_corner"]` names an arbitrary rc suffix --
    # whichever of the three tied interconnect corners `dcc.power()`'s own
    # `max()` happened to see first. Reporting only the liberty deck keeps
    # this from implying an interconnect dependence that is not there.
    leakage_corner = p["max_leakage_corner"].split("/")[0]
    return {
        "active_w": active_w,
        "active_w_at_1mhz": p["max_1mhz_w"],
        "active_corner": p["max_1mhz_corner"],
        "leakage_w": leak_w,
        "leakage_a": p["max_leakage_a"],
        "leakage_corner": leakage_corner,
        "n_corners": len(records),
    }


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


def shipped_instances(netlist: Path = SAMPLER_CORE_NETLIST) -> dict[str, str]:
    """``{instance: subckt}`` for the cells the shipped ``sampler_core`` instantiates.

    Read from the generated netlist, not restated, so a cell added to or removed
    from the schematic changes the inventory the ledger is checked against.
    """
    lines = netlist.read_text().splitlines()
    out: dict[str, str] = {}
    inside = False
    for ln in lines:
        s = ln.strip()
        if s.startswith(".subckt sampler_core"):
            inside = True
            continue
        if inside and s.startswith(".ends"):
            break
        if inside and s[:1].lower() == "x":
            toks = s.split()
            out[toks[0]] = toks[-1]
    if not out:
        raise RuntimeError(f"{netlist}: no instances found inside .subckt sampler_core")
    return out


def inventory_check(instances: dict[str, str], terms=LEDGER_TERMS) -> dict:
    """Map every instantiated cell to its ledger term(s).

    Returns ``{"mapping", "uncovered", "double_counted", "unknown"}``:
    ``uncovered`` are instances no required term accounts for (a missing term),
    ``double_counted`` maps an instance to the several terms claiming it, and
    ``unknown`` are covers that name no instance (a stale ledger).
    """
    mapping: dict[str, list[str]] = {inst: [] for inst in instances}
    unknown: list[str] = []
    for term in terms:
        if not term["required"]:
            continue
        for inst in term["covers"]:
            if inst in mapping:
                mapping[inst].append(term["name"])
            else:
                unknown.append(f"{term['name']}:{inst}")
    return {
        "mapping": mapping,
        "uncovered": sorted(i for i, ts in mapping.items() if not ts),
        "double_counted": {i: ts for i, ts in mapping.items() if len(ts) > 1},
        "unknown": sorted(unknown),
    }


def inventory_problems(inv: dict) -> list[str]:
    probs = []
    if inv["uncovered"]:
        probs.append("instantiated but in no required ledger term: " + ", ".join(inv["uncovered"]))
    for inst, ts in inv["double_counted"].items():
        probs.append(f"{inst} is counted by several terms: {', '.join(ts)}")
    if inv["unknown"]:
        probs.append("ledger covers name no instance of sampler_core: " + ", ".join(inv["unknown"]))
    return probs


def liveness_active(rec: Record, f_clk: float, q_clk_c: float) -> dict:
    """The liveness term at one corner, split so nothing is counted twice.

    ``p_flops_w`` is the xsr1/xsr2 flops themselves at sample-clock rate
    ``f_clk`` (ring-data charge from the record, clock-cycle charge ``q_clk_c``
    from the same corner's sampler-dff-active-current record, as for xsb/xsv).
    ``dp_load_w`` is the SIGNED change those taps cause in the array's own
    supply power, from the record's in-run control array: it belongs next to
    ``P_array`` because the array records were taken without the taps.
    """
    vdd = rec.vdd
    i_data = rec.values["i_data_a"]
    p_flops = vdd * (i_data + 2.0 * f_clk * q_clk_c)
    return {"p_flops_w": p_flops, "dp_load_w": rec.values["dp_load_w"],
            "p_total_w": p_flops + rec.values["dp_load_w"]}


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
                   help="fail instead of degrading if the gate-level digital "
                        "power records are unavailable")
    p.add_argument("--with-taps", action="store_true",
                   help="add the measured but not-instantiated metastability-hybrid "
                        "tap. The liveness samplers are shipped and are a ledger term "
                        "of their own (#463); they are never added here.")
    p.add_argument("--check", action="store_true",
                   help="exit non-zero if a required record family is missing or a "
                        "measured term contradicts the record it came from. Does NOT "
                        "fail on a README row being missed -- a missed row is a spec "
                        "question, routed through spec/, not a tool failure.")
    args = p.parse_args(argv)

    arrays = by_corner(load(ARRAY_GLOBS), prefer="pvt-q")
    samplers = by_corner(load(SAMPLER_ACTIVE_GLOB))
    idles = by_corner(load(IDLE_GLOB))
    lives = by_corner(load(LIVENESS_GLOB))
    inv = inventory_check(shipped_instances())

    missing = [name for name, d in
               (("array", arrays), ("sampler-active", samplers), ("idle", idles)) if not d]
    if missing:
        print(f"ERROR: no records for: {', '.join(missing)}", file=sys.stderr)
        return 2

    dig = None
    dig_note = ""
    if not args.no_digital:
        # The MEASURED-at-gate-level term (DR-0023) reads committed records
        # and needs no PDK. It is the one that feeds the totals below.
        try:
            dig = digital_measured(args.rate)
        except dcc.RecordError as exc:
            if args.require_digital:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2
            dig_note = str(exc)

    # The pre-synthesis ESTIMATE (DR-0004 Tier 2) is CONTEXT ONLY as of
    # DR-0023 -- it no longer feeds the totals below, and its own absence
    # (no PDK Liberty library on this host) never fails `--check` or
    # `--require-digital`, both of which are about the measured term.
    dig_est_active = dig_est_idle = None
    dig_est_note = ""
    if not args.no_digital:
        try:
            dig_est_active = digital_estimate(DIGITAL_CORNER_ACTIVE, args.rate)
            dig_est_idle = digital_estimate(DIGITAL_CORNER_IDLE, args.rate)
        except RuntimeError as exc:
            dig_est_note = str(exc).splitlines()[-1] if str(exc).strip() else "unavailable"

    print(f"sample clock     : {args.rate:g} Hz")
    print(f"array records    : {len(arrays)} corners  {', '.join(ARRAY_GLOBS)}")
    print(f"sampler records  : {len(samplers)} corners  {SAMPLER_ACTIVE_GLOB}")
    print(f"idle records     : {len(idles)} corners  {IDLE_GLOB}")
    print(f"liveness records : {len(lives)} of {len(arrays)} corners  {LIVENESS_GLOB}")
    if dig:
        print(f"digital term     : MEASURED-at-gate-level ({dig['n_corners']} corners, "
              f"active binds {dig['active_corner']}, leakage binds "
              f"{dig['leakage_corner']}) -- DR-0021/DR-0023, feeds the totals below")
    elif dig_note:
        print("digital term     : UNAVAILABLE -- no gate-level power records on this host.")
        print(f"                   ({dig_note})")
        print("                   Totals below are MEASURED SILICON ONLY and are a "
              "lower bound.")
    else:
        print("digital term     : EXCLUDED (--no-digital)")
    if dig_est_active:
        print(f"digital estimate : {DIGITAL_CORNER_ACTIVE} (active) / "
              f"{DIGITAL_CORNER_IDLE} (idle)  -- DR-0004 Tier 2 ESTIMATE, "
              "pre-synthesis prediction, CONTEXT ONLY (does not feed the totals)")
    elif dig_est_note and not args.no_digital:
        print(f"digital estimate : UNAVAILABLE ({dig_est_note}) -- context comparison skipped")
    print()
    print("LEDGER INVENTORY  (design/sampler_core.spice instances -> active-power term)")
    insts = shipped_instances()
    for inst, terms_ in inv["mapping"].items():
        print(f"  {inst:<5} {insts[inst]:<14} -> {', '.join(terms_) if terms_ else 'NO TERM'}")
    for term in LEDGER_TERMS:
        print(f"  term {term['name']:<12} covers {', '.join(term['covers']):<10} evidence: {term['evidence']}")
    print(f"  idle scope: one whole-{IDLE_SCOPE} measurement (xsr1/xsr2 leakage already inside; "
          "no second idle term)")
    missing_live = [c for c in arrays if c in samplers and c not in lives]
    if missing_live:
        print(f"  GAP: liveness samplers (xsr1/xsr2) have no record at {len(missing_live)} of "
              f"{len(arrays)} corners; those totals EXCLUDE them and are lower bounds "
              f"(historical {_w(HISTORICAL_TAP_LIVENESS_W)} is a different topology and rate "
              "and is not used).")
    print()

    # ------------------------------------------------------------------ ACTIVE
    print("ACTIVE POWER  (rings + XOR + sampler measured; digital MEASURED-at-gate-level)")
    live_col = bool(lives)
    hdr = (f"| {'corner':<16} | {'R_xo':>10} | {'P_array':>9} | {'P_sampler':>9} |"
           + (f" {'P_liveness':>10} |" if live_col else "")
           + f" {'P_digital':>9} | {'TOTAL':>9} | {'vs 500uW':>8} |")
    rule = ("|" + "-" * 18 + "|" + "-" * 12 + "|" + "-" * 11 + "|" + "-" * 11
            + ("|" + "-" * 12 if live_col else "")
            + "|" + "-" * 11 + "|" + "-" * 11 + "|" + "-" * 10 + "|")
    print(hdr)
    print(rule)

    p_dig = dig["active_w"] if dig else 0.0
    if args.with_taps:
        p_dig += TAP_META_W

    active_rows = []
    for corner, arec in arrays.items():
        srec = samplers.get(corner)
        if srec is None:
            continue
        r_xo = abs(arec.values["xo_trans_per_s"])
        s = sampler_active(srec, r_xo, args.rate)
        p_array = abs(arec.values["p_total_w"])
        lrec = lives.get(corner)
        live = liveness_active(lrec, args.rate, s["q_clk_c"]) if lrec else None
        total = p_array + s["p_total_w"] + p_dig + (live["p_total_w"] if live else 0.0)
        active_rows.append((total, corner, r_xo, p_array, s, live))
    active_rows.sort(key=lambda r: r[0], reverse=True)
    for total, corner, r_xo, p_array, s, live in active_rows:
        cell = ""
        if live_col:
            cell = (f" {_w(live['p_total_w']):>10} |" if live else f" {'GAP':>10} |")
        print(
            f"| {corner:<16} | {r_xo:>10.3e} | {_w(p_array):>9} | {_w(s['p_total_w']):>9} |"
            f"{cell} {_w(p_dig):>9} | {_w(total):>9} | {total / ACTIVE_BUDGET_W:>7.1%} |"
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
    if dig:
        print(f"  digital (MEASURED-at-gate-level): {_w(p_dig):>7}"
              f"   {p_dig / ACTIVE_BUDGET_W:6.1%}"
              f"   [{dig['active_corner']}, rate-scaled from {_w(dig['active_w_at_1mhz'])} @ 1 MHz]")
        if dig_est_active:
            est_w = dig_est_active["shipped_total"]["active_w"]
            print(f"    cf. pre-synthesis ESTIMATE (context, DR-0004 Tier 2, "
                  f"does not feed this total): {_w(est_w)}"
                  f"   ({p_dig / est_w:.1f}x)")
    headroom = ACTIVE_BUDGET_W - worst_active[3]
    wl = worst_active[5]
    if wl:
        print(f"  liveness samplers xsr1/xsr2 (measured): {_w(wl['p_flops_w']):>8}"
              f"   {wl['p_flops_w'] / ACTIVE_BUDGET_W:6.1%}"
              f"   (flops) + {_w(wl['dp_load_w'])} loading of the array")
    else:
        print("  liveness samplers xsr1/xsr2: GAP at the worst corner -- total is a lower bound")
    measured_rows = [r for r in active_rows if r[5]]
    if measured_rows:
        print("  liveness reconciliation (like-for-like, same corner, same rate; measured corners only):")
        for total, corner, _r, _pa, _s, live in sorted(measured_rows, key=lambda r: r[1]):
            print(f"    {corner:<14} without xsr1/xsr2 {_w(total - live['p_total_w']):>9}"
                  f" -> with {_w(total):>9}  (+{_w(live['p_total_w'])} = flops {_w(live['p_flops_w'])}"
                  f" + array loading {_w(live['dp_load_w'])};"
                  f" {live['p_total_w'] / ACTIVE_BUDGET_W:.1%} of the row)")
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
    i_dig = dig["leakage_a"] if dig else 0.0
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
    if dig:
        print(f"  digital leakage (MEASURED-at-gate-level): {_a(i_dig):>6}"
              f"   {i_dig / IDLE_BUDGET_A:6.1%}"
              f"   [{dig['leakage_corner']}, {dig['n_corners']} corners swept]")
        if dig_est_idle:
            t = dig_est_idle["shipped_total"]
            print(f"    cf. pre-synthesis ESTIMATE (context, DR-0004 Tier 2, "
                  f"does not feed this total): {_a(t['leakage_a'])}"
                  f"   ({i_dig / t['leakage_a']:.2f}x)"
                  f"   [{t['flops']} flops, {t['cells']} cells, no power gating]")
    print()

    if args.check:
        problems = []
        if len(arrays) < 27:
            problems.append(f"only {len(arrays)} array corners (expected >= 27)")
        if len(samplers) < 45:
            problems.append(f"only {len(samplers)} sampler-active corners (expected >= 45)")
        if len(idles) < 45:
            problems.append(f"only {len(idles)} idle corners (expected >= 45)")
        problems += inventory_problems(inv)
        if not args.no_digital:
            if dig is None:
                problems.append(
                    "digital gate-level power records unavailable "
                    f"({dig_note or 'unknown reason'}) -- since DR-0023 these feed the "
                    "totals and, unlike the estimate, need no PDK, so this should not "
                    "happen on a committed checkout"
                )
            elif dig["n_corners"] < 15:
                problems.append(
                    f"only {dig['n_corners']} digital-sta-power corners (expected >= 15, "
                    "DR-0021's 5-liberty x 3-interconnect grid)"
                )
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
