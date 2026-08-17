#!/usr/bin/env python3
"""Per-cycle top-level stimulus for the post-route gate-level re-run (#147).

One scenario per member of the behavioural **digital functional suite**, plus
two that only exist at this level (a register-read walk and its
negative control). Each scenario is a plain list of per-cycle stimulus rows --
no simulator, no cocotb, no gate netlist -- so the *same* list drives both
sides of the pre/post comparison:

* ``post_route_tb.py`` drives it into the SDF-annotated gate netlist
  (``layout/digital/trng_top.pnr.v``) through ``klt
  functional-verification``, and
* the same list is stepped through ``design/trng_top/trng_top.py``'s
  behavioural ``TopLevel`` model, which is the golden reference.

Both sides therefore see byte-identical stimulus by construction, and a
difference in the comparison is a difference in the *implementation*, never
in the stimulus.

Why the stimulus is re-expressed at the top level
--------------------------------------------------
Four of the five suite members (``sim/tb/conditioner-crc32/``,
``sim/tb/health-test-fault-injection/``, ``sim/tb/interface-regfile/``,
``sim/tb/ring-liveness-fault-injection/``) drive **one sub-block** each,
either through its Python model or through its own
``tb_rtl_equivalence.v``. There is no gate-level equivalent of that: `klt
synthesize` deliberately produces *one* netlist for the whole digital
partition (``design/synth.py``'s "One netlist, not five"), and
``klt place-and-route`` flattens it -- ``layout/digital/trng_top.pnr.v`` is a
single ``module trng_top`` with 2447 cell instances and no sub-block
hierarchy left to bind a per-block testbench to. Every sub-block's stimulus
and every sub-block's observable therefore has to travel through
``trng_top``'s own ports:

| suite member | driven through | observed through |
|---|---|---|
| `conditioner-crc32` | `raw_bit`/`raw_valid` | `DATA` register reads / `str_data` |
| `health-test-fault-injection` | `raw_bit`/`raw_valid` | `ht_alarm`, `STATUS` |
| `interface-regfile` | `reg_*` bus + `raw_bit` | `reg_rdata`, `str_*`, `ht_alarm` |
| `ring-liveness-fault-injection` | `ring_bit[1:0]` | `ht_alarm`, `STATUS` |
| `smoke-trng-top` | `raw_bit` + one bus read | all of the above |

That is a *narrower* observation surface than the behavioural testbenches
have (they can read a block's internal counters directly; this level sees
only the pins), which is stated as a coverage limit in this directory's
README rather than papered over.

Stimulus provenance, and where it is deliberately shortened
------------------------------------------------------------
Every scenario reuses the behavioural testbench's **own** source model, with
the same label and seed, so the bits are the same bits -- ``source_model``
here is imported from the sibling testbench directory, not re-implemented.
Lengths are a different matter: the behavioural scenarios run 8192-131072
samples because they make *statistical* claims (monobit balance, an observed
false-positive rate against a binomial prediction). This level makes no
statistical claim at all -- it is an equivalence check between an
implementation and a model on identical stimulus -- so each scenario runs the
shortest prefix that still exercises the mechanism it is named for, and
``Scenario.shortened_from`` records the behavioural length it was cut down
from. See the README's "What this does not cover".
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Callable

TB_DIR = Path(__file__).resolve().parent
SIM_DIR = TB_DIR.parents[1]
REPO_ROOT = SIM_DIR.parent

for _path in (
    REPO_ROOT / "design" / "conditioner",
    REPO_ROOT / "design" / "health_test",
    REPO_ROOT / "design" / "interface",
    REPO_ROOT / "design" / "trng_top",
    SIM_DIR / "tb" / "conditioner-crc32",
    SIM_DIR / "tb" / "ring-liveness-fault-injection",
    SIM_DIR / "tb" / "smoke-trng-top",
):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import rct_apt as ht  # noqa: E402
import regmap  # noqa: E402
import ring_liveness as rl  # noqa: E402
import ring_source_model  # noqa: E402
import source_model  # noqa: E402  (sim/tb/conditioner-crc32/source_model.py)

import raw_source  # noqa: E402  (sim/tb/smoke-trng-top/raw_source.py)

#: DR-0002's start-up window: 1024 consecutive clean raw samples before the
#: conditioned path is un-gated. Read from the design, never typed in.
STARTUP_SAMPLES = ht.W

#: DR-0002's repetition-count cutoff at the ratified draft H0 = 0.5, and
#: DR-0016's per-ring liveness cutoff (the same number, from the same H).
C_RCT = ht.c_rct(ht.H0)
C_LIVE = rl.RingLivenessMonitor().c_live

#: Declared per-sample min-entropy of every synthetic raw source used here --
#: an input parameter, never a result (the same value and the same wording
#: `sim/tb/interface-regfile/run_demo.py` uses).
DECLARED_H = Decimal("0.5")

#: The four register indices, from the generated map rather than literals.
CTRL, STATUS, DATA, RAW_DATA = (
    regmap.CTRL.index,
    regmap.STATUS.index,
    regmap.DATA.index,
    regmap.RAW_DATA.index,
)


def _bit_lsb(register, field_name: str) -> int:
    return next(f for f in register.fields if f.name == field_name).lsb


def healthy_rings(label: str, seed: int, n: int) -> list[tuple[int, int]]:
    """``n`` rows of healthy per-ring liveness taps.

    **Every scenario longer than C_LIVE cycles has to drive these**, and that
    is a finding of this re-run rather than a detail. ``trng_top`` has a
    DR-0016 per-ring input (``ring_bit[1:0]``) that four of the five
    behavioural suite members have no equivalent of at all: each drives one
    sub-block, and only ``ring_liveness`` has ring inputs. Leaving
    ``ring_bit`` idle at the top level is not "no stimulus", it is *two dead
    rings* -- the watchdog fires at ``C_LIVE`` (81) samples, latches
    ``ht_alarm``, and gates the conditioned path, so a scenario aimed at the
    conditioner or the register file would silently be measuring the alarm
    path instead. The behavioural per-block suite cannot see that
    interaction; this level cannot avoid it. See the README's "What the
    per-block suite could not see".

    Uses the same generator and label convention as
    ``sim/tb/ring-liveness-fault-injection/run_demo.py``'s own
    ``_healthy_rows``, so the bits are that testbench's bits.
    """
    streams = [
        ring_source_model.healthy_ring_bits(f"{label}-ring{r}", seed + r, n)
        for r in range(2)
    ]
    return [(streams[0][i], streams[1][i]) for i in range(n)]


def with_healthy_rings(rows: list[dict], label: str, seed: int) -> list[dict]:
    """Overwrite ``ring_bit`` on **every** row with a healthy per-ring sample.

    Every row, not just the rows that carry a raw sample: ``ring_liveness.v``
    is clocked by the same ``clk`` and has no ``valid`` gate, so a bus-only
    cycle still counts toward each ring's run length. Missing that is how a
    scenario ends up alarmed 81 cycles in for reasons that have nothing to do
    with what it is testing.
    """
    rings = healthy_rings(label, seed, len(rows))
    return [dict(row, ring_bit=rings[i]) for i, row in enumerate(rows)]


#: `CTRL` word with `OUT_MODE` = raw (DR-0001 §2's other output path).
CTRL_OUT_MODE_RAW = (1 << _bit_lsb(regmap.CTRL, "OUT_MODE")) | (
    1 << _bit_lsb(regmap.CTRL, "EN")
)
#: `CTRL` word back to the reset default (conditioned, enabled).
CTRL_OUT_MODE_COND = 1 << _bit_lsb(regmap.CTRL, "EN")
#: `STATUS` write-1-to-clear word that clears both sticky overflow flags.
STATUS_CLEAR_OVF = (1 << _bit_lsb(regmap.STATUS, "OVF_DATA")) | (
    1 << _bit_lsb(regmap.STATUS, "OVF_RAW")
)


def cycle(
    raw_bit: int = 0,
    raw_valid: bool = False,
    ring_bit: tuple[int, int] = (0, 0),
    reg_sel: bool = False,
    reg_write: bool = False,
    reg_addr: int = 0,
    reg_wdata: int = 0,
    str_ready: bool = False,
) -> dict:
    """One sampler-clock cycle of top-level stimulus.

    The keys are exactly ``trng_top``'s input ports, and exactly the keyword
    arguments ``trng_top.TopLevel.step`` accepts, so one row drives the DUT
    and the model without translation.
    """
    return {
        "raw_bit": int(raw_bit) & 1,
        "raw_valid": bool(raw_valid),
        "ring_bit": tuple(int(b) & 1 for b in ring_bit),
        "reg_sel": bool(reg_sel),
        "reg_write": bool(reg_write),
        "reg_addr": int(reg_addr),
        "reg_wdata": int(reg_wdata) & 0xFFFFFFFF,
        "str_ready": bool(str_ready),
    }


@dataclass(frozen=True)
class Scenario:
    """One post-route scenario.

    ``counterpart`` names the behavioural testbench this re-runs, so the
    pre/post table in the evidence record has a row per suite member and a
    reader can find the ``level: behavioral`` record it is being compared
    with. ``expect`` is what the *comparison* must show, not what the design
    must do:

    * ``"match"`` -- every compared cycle's four top-level outputs must equal
      the behavioural model's, exactly, with no unresolved (``x``/``z``) bit.
    * ``"mismatch"`` -- a **negative control**: the comparison is required to
      *fail*. A control that passes means the thing it controls for is not
      actually in the loop (see ``reg-read-walk-early-sample``).
    * ``"settle-sweep"`` -- not a pass/fail comparison at all: the same
      stimulus is compared at a ladder of sampling offsets and the smallest
      offset that still matches is reported.
    """

    name: str
    counterpart: str
    why: str
    build: Callable[[], list[dict]]
    expect: str = "match"
    shortened_from: str | None = None
    #: Offsets (ns after the inputs change) the ``settle-sweep`` kind walks.
    sweep_offsets_ns: tuple[float, ...] = ()
    #: Offset (ns after the inputs change) at which outputs are sampled, when
    #: this scenario deliberately departs from the default sampling point.
    sample_offset_ns: float | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


# --------------------------------------------------------------------------- #
# 1. smoke-trng-top -- the ten transistor-derived raw bits, unchanged.
# --------------------------------------------------------------------------- #


def _smoke() -> list[dict]:
    bits = raw_source.raw_bits()
    rows = [cycle(raw_bit=b, raw_valid=True) for b in bits]
    # The same "second signal path" cycle sim/tb/smoke-trng-top/run_demo.py
    # ends on: one register-bus read of STATUS.
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    return rows


# --------------------------------------------------------------------------- #
# 2. interface-regfile -- a full DR-0002 start-up window, then the register
#    bus: reads, an OUT_MODE switch in both directions, a W1C clear.
# --------------------------------------------------------------------------- #


def _startup_and_regfile() -> list[dict]:
    bits, _p_one, _threshold = source_model.biased_bits(
        "interface-regfile-startup", 1, STARTUP_SAMPLES + 64, DECLARED_H
    )
    rows: list[dict] = []
    for i, bit in enumerate(bits[:STARTUP_SAMPLES]):
        # Two bus reads inside the window, to show the raw path is live from
        # the first sample while the conditioned path is still gated
        # (DR-0002's "starting up" state, DR-0001's "raw always available").
        if i == 200:
            rows.append(cycle(raw_bit=bit, raw_valid=True, reg_sel=True, reg_addr=STATUS))
        elif i == 400:
            rows.append(
                cycle(raw_bit=bit, raw_valid=True, reg_sel=True, reg_addr=RAW_DATA)
            )
        else:
            rows.append(cycle(raw_bit=bit, raw_valid=True))

    tail = bits[STARTUP_SAMPLES:]
    # Post-start-up: STATUS (STARTUP clear, COND_READY set), a DATA read, a
    # sticky-overflow clear, an OUT_MODE switch to raw and back (each of
    # which flushes, DR-0001 §2), and a streaming-port handshake.
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    rows.append(cycle(reg_sel=True, reg_addr=DATA))
    rows.append(cycle(reg_sel=True, reg_addr=RAW_DATA))
    rows.append(
        cycle(reg_sel=True, reg_write=True, reg_addr=STATUS, reg_wdata=STATUS_CLEAR_OVF)
    )
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    rows.append(
        cycle(reg_sel=True, reg_write=True, reg_addr=CTRL, reg_wdata=CTRL_OUT_MODE_RAW)
    )
    rows.append(cycle(reg_sel=True, reg_addr=CTRL))
    for bit in tail[:16]:
        rows.append(cycle(raw_bit=bit, raw_valid=True, str_ready=True))
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    rows.append(
        cycle(reg_sel=True, reg_write=True, reg_addr=CTRL, reg_wdata=CTRL_OUT_MODE_COND)
    )
    for bit in tail[16:32]:
        rows.append(cycle(raw_bit=bit, raw_valid=True, str_ready=True))
    rows.append(cycle(reg_sel=True, reg_addr=CTRL))
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    return with_healthy_rings(rows, "interface-regfile-startup", 51)


# --------------------------------------------------------------------------- #
# 3. conditioner-crc32 -- the start-up window, then two full 256-bit
#    conditioner blocks, read out through DATA.
# --------------------------------------------------------------------------- #

#: Raw samples per conditioned word: `crc32_conditioner`'s own K * 32.
BLOCK_BITS = 256


#: Raw samples past the two blocks' worth, so *both* the model and the
#: hardware complete two whole blocks. They do not agree on when the
#: conditioned path un-gates -- the model un-gates one sample earlier (#176) --
#: so a stimulus of exactly 2 x BLOCK_BITS post-start-up samples gives the
#: model two words and the hardware one, and the scenario would be comparing
#: "two words" against "one word and an empty FIFO" rather than comparing
#: conditioned words.
BLOCK_SLACK_SAMPLES = 8


def _conditioner_blocks() -> list[dict]:
    total = STARTUP_SAMPLES + 2 * BLOCK_BITS + BLOCK_SLACK_SAMPLES
    bits, _p_one, _threshold = source_model.biased_bits(
        "conditioner-crc32-h050", 1, total, DECLARED_H
    )
    rows = [cycle(raw_bit=b, raw_valid=True) for b in bits]
    # Read the conditioned words out through DATA. A word that survives
    # synthesis, CTS resizing and routing bit-exactly is the whole point of
    # this scenario -- the CRC-32 arithmetic is where a mis-mapped XOR tree
    # would show up.
    #
    # THREE reads, not two, and two idle cycles first. `crc32_conditioner.v`
    # registers `cond_valid`/`cond_word` (they are `output reg`), so a word
    # reaches the interface's FIFO one cycle later in hardware than in
    # `trng_top.py`'s model, which hands it over combinationally (#176). Two
    # back-to-back reads therefore drain the FIFO faster than the *hardware*
    # refills it and the second read returns 0 -- an artefact of the read
    # timing, not a missing word, but one that would make this scenario's
    # headline number ("the two conditioned words") quietly wrong. The idle
    # cycles plus the third read give the slower of the two paths room, so
    # both sides really do read both words.
    rows.append(cycle())
    rows.append(cycle())
    rows.append(cycle(reg_sel=True, reg_addr=DATA))
    rows.append(cycle())
    rows.append(cycle(reg_sel=True, reg_addr=DATA))
    rows.append(cycle())
    rows.append(cycle(reg_sel=True, reg_addr=DATA))
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    return with_healthy_rings(rows, "conditioner-crc32-h050", 61)


# --------------------------------------------------------------------------- #
# 4. health-test-fault-injection -- DR-0002's stuck-output detection latency.
# --------------------------------------------------------------------------- #

#: Clean lead-in before the fault. The behavioural scenario uses 2000; the
#: RCT is a run-length test with no window state, so what the latency bound
#: depends on is the *run* after onset, not the length of what preceded it.
LEAD_IN_BITS = 200


def _rct_stuck_output() -> list[dict]:
    lead_in, _p_one, _threshold = source_model.biased_bits(
        "stuck-output-lead-in", 20, LEAD_IN_BITS, ht.H0
    )
    fault = source_model.constant_bits(1, C_RCT + 40)
    rows = [cycle(raw_bit=b, raw_valid=True) for b in lead_in + fault]
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    return with_healthy_rings(rows, "stuck-output", 71)


#: Index of the first fault sample in `_rct_stuck_output`'s row list -- the
#: onset the observed detection latency is measured from.
RCT_ONSET_CYCLE = LEAD_IN_BITS


# --------------------------------------------------------------------------- #
# 5. ring-liveness-fault-injection -- DR-0016's per-ring watchdog.
# --------------------------------------------------------------------------- #

RING_LEAD_IN_BITS = 120


def _ring1_stuck() -> list[dict]:
    n = RING_LEAD_IN_BITS
    fault_len = C_LIVE + 40
    lead = [
        ring_source_model.healthy_ring_bits(f"ring{r}", 41 + r, n) for r in range(2)
    ]
    lead_rows = [(lead[0][i], lead[1][i]) for i in range(n)]
    frozen = lead_rows[-1][0]
    stuck = ring_source_model.stuck_ring_bits(frozen, fault_len)
    other = ring_source_model.healthy_ring_bits("ring1-stuck-other", 141, fault_len)
    fault_rows = [(stuck[i], other[i]) for i in range(fault_len)]

    # The raw tap keeps running through the whole scenario: DR-0016's point is
    # that one dead ring is *invisible* at the XOR-combined raw tap, so the
    # raw path must look healthy while the per-ring watchdog fires.
    raw, _p_one, _threshold = source_model.biased_bits(
        "ring1-stuck-raw", 41, n + fault_len, DECLARED_H
    )
    rows = [
        cycle(raw_bit=raw[i], raw_valid=True, ring_bit=row)
        for i, row in enumerate(lead_rows + fault_rows)
    ]
    rows.append(cycle(reg_sel=True, reg_addr=STATUS))
    return rows


RING_ONSET_CYCLE = RING_LEAD_IN_BITS


# --------------------------------------------------------------------------- #
# 6/7/8. The register-read walk: a positive scenario, a negative control, and
#        a settle sweep. These have no behavioural counterpart -- they exist
#        only to establish that the SDF annotation is in the loop at all, and
#        what it costs.
# --------------------------------------------------------------------------- #


def _reg_read_walk() -> list[dict]:
    """Read a different register every cycle, so ``reg_rdata`` changes on
    every single cycle.

    That is what makes the negative control below discriminating: sampling
    ``reg_rdata`` before it has settled reads the *previous* cycle's word,
    which on this stimulus is always a different word. On idle stimulus
    (every output holding 0) an early sample is indistinguishable from a
    settled one, and the control would pass for the wrong reason.
    """
    order = [CTRL, STATUS, RAW_DATA, DATA]
    rows: list[dict] = []
    # A short raw run first, so STATUS and RAW_DATA carry non-zero content
    # (raw samples counted, a packed raw word available) rather than reading
    # back the reset word.
    bits, _p_one, _threshold = source_model.biased_bits(
        "reg-read-walk", 7, 64, DECLARED_H
    )
    rows += [cycle(raw_bit=b, raw_valid=True) for b in bits]
    for i in range(32):
        rows.append(cycle(reg_sel=True, reg_addr=order[i % len(order)]))
    return with_healthy_rings(rows, "reg-read-walk", 81)


#: Sampling offsets (ns after the inputs change) the settle sweep walks, from
#: "immediately" to "one 50 ns cycle minus the drive margin". Coarse on
#: purpose: this bounds the annotated combinational delay of the register-read
#: path, it does not measure it.
SWEEP_OFFSETS_NS = (0.1, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 24.0, 32.0, 44.0)


SCENARIOS: dict[str, Scenario] = {
    "smoke": Scenario(
        name="smoke",
        counterpart="sim/tb/smoke-trng-top",
        why=(
            "the same ten transistor-derived raw bits (tt / 27 C / 3.30 V, "
            "read out of sim/records/2026-08-01-sampler-array-digitize-03.md "
            "by that testbench's own raw_source.py) plus its closing STATUS "
            "read, driven into the post-route netlist instead of the "
            "behavioural model"
        ),
        build=_smoke,
    ),
    "startup-and-regfile": Scenario(
        name="startup-and-regfile",
        counterpart="sim/tb/interface-regfile",
        why=(
            "a full DR-0002 start-up window (1024 clean samples) followed by "
            "the register bus: reads of all four registers, a write-1-to-clear "
            "of the sticky overflow flags, an OUT_MODE switch in both "
            "directions with its DR-0001 flush, and a streaming handshake"
        ),
        build=_startup_and_regfile,
        shortened_from="4096 samples (that testbench's `startup` scenario)",
    ),
    "conditioner-blocks": Scenario(
        name="conditioner-blocks",
        counterpart="sim/tb/conditioner-crc32",
        why=(
            "two complete 256-bit conditioner blocks, read out through DATA: "
            "the CRC-32 arithmetic must be bit-exact after mapping, CTS "
            "buffering, cell resizing and routing"
        ),
        build=_conditioner_blocks,
        shortened_from="131072 samples (that testbench's `h050` scenario)",
    ),
    "rct-stuck-output": Scenario(
        name="rct-stuck-output",
        counterpart="sim/tb/health-test-fault-injection",
        why=(
            "DR-0002's first detection-latency target: a raw output that "
            "sticks must raise ht_alarm within C_RCT samples of onset. The "
            "latency is measured on the netlist, not assumed from the model"
        ),
        build=_rct_stuck_output,
        shortened_from="2000-sample lead-in (that testbench's `stuck-output` scenario)",
    ),
    "ring1-stuck": Scenario(
        name="ring1-stuck",
        counterpart="sim/tb/ring-liveness-fault-injection",
        why=(
            "DR-0016's per-ring watchdog: ring 1 freezes while ring 2 and the "
            "XOR-combined raw tap keep running, so only the per-ring monitor "
            "can see it -- ht_alarm must rise within C_LIVE samples of onset"
        ),
        build=_ring1_stuck,
        shortened_from="2000-sample lead-in (that testbench's `ring1-stuck` scenario)",
    ),
    "reg-read-walk": Scenario(
        name="reg-read-walk",
        counterpart="n/a (post-route-level only)",
        why=(
            "a register read on every cycle, rotating through all four "
            "addresses, so reg_rdata changes every cycle. The positive half "
            "of the annotation control below"
        ),
        build=_reg_read_walk,
    ),
    "reg-read-walk-early-sample": Scenario(
        name="reg-read-walk-early-sample",
        counterpart="n/a (post-route-level only -- negative control)",
        why=(
            "the identical stimulus, sampled 0.1 ns after the inputs change "
            "instead of 45 ns. With real annotated cell delays in the loop "
            "this MUST mismatch; a zero-delay (silently unannotated) run "
            "would settle instantly and match. This is the control that "
            "makes the other scenarios' green results mean something"
        ),
        build=_reg_read_walk,
        expect="mismatch",
        sample_offset_ns=0.1,
    ),
    "reg-read-walk-settle-sweep": Scenario(
        name="reg-read-walk-settle-sweep",
        counterpart="n/a (post-route-level only)",
        why=(
            "the same stimulus compared at a ladder of sampling offsets, "
            "reporting the smallest offset at which the register-read path is "
            "fully settled -- an observed bound on the annotated "
            "combinational delay of that path (cell delay only; see the "
            "coverage limits)"
        ),
        build=_reg_read_walk,
        expect="settle-sweep",
        sweep_offsets_ns=SWEEP_OFFSETS_NS,
    ),
}

#: The five behavioural suite members this re-runs, in the order the pre/post
#: table lists them.
SUITE_SCENARIOS = (
    "smoke",
    "startup-and-regfile",
    "conditioner-blocks",
    "rct-stuck-output",
    "ring1-stuck",
)

#: The scenarios that exist only at this level (annotation control + sweep).
CONTROL_SCENARIOS = (
    "reg-read-walk",
    "reg-read-walk-early-sample",
    "reg-read-walk-settle-sweep",
)

ALL_SCENARIOS = SUITE_SCENARIOS + CONTROL_SCENARIOS


def cycle_counts() -> dict[str, int]:
    """Cycle count per scenario -- cheap, and computed the same way both
    sides do it (by building the stimulus), so a documented cost figure can
    never drift from the stimulus that produced it."""
    return {name: len(SCENARIOS[name].build()) for name in ALL_SCENARIOS}


if __name__ == "__main__":  # pragma: no cover - a human sanity check
    counts = cycle_counts()
    for scenario_name, count in counts.items():
        print(f"{scenario_name:34s} {count:6d} cycles")
    print(f"{'TOTAL':34s} {sum(counts.values()):6d} cycles")
    print(f"STARTUP_SAMPLES={STARTUP_SAMPLES} C_RCT={C_RCT} C_LIVE={C_LIVE}")
