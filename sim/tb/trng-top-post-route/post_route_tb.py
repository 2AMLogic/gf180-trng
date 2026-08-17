#!/usr/bin/env python3
"""cocotb regression: the post-route gate netlist against RTL, and both
against the behavioural model.

This is the module ``klt functional-verification`` imports (Icarus 13.0 +
cocotb 2.0, ``request.testbench.module = "post_route_tb"``). It is **not**
run directly -- ``run_demo.py`` builds the requests, invokes `klt` twice, and
turns what this module writes into an append-only evidence record.

Two legs, one testbench
------------------------
``$TRNG_POST_ROUTE_LEG`` selects which DUT this process is driving, and the
*same* stimulus, the same comparison and the same trace hashing run against
both:

* ``rtl`` -- ``design/trng_top/trng_top.v`` and its four child modules,
  zero-delay, no SDF. The **reference leg**: it establishes what the RTL
  does, cycle for cycle.
* ``gate`` -- ``layout/digital/trng_top.pnr.v``, the as-built post-route
  netlist (CTS buffers and resized cells included), with
  ``layout/digital/trng_top.sdf``'s cell delays back-annotated by Icarus's
  ``$sdf_annotate``. This leg additionally asserts that its per-scenario
  output **trace hash equals the reference leg's** -- which is the actual
  question a post-layout re-run has to answer: did synthesis, CTS, resizing
  and routing preserve the RTL's behaviour, under real annotated delay?

Why the primary verdict is against the RTL and not against the model: the
behavioural model is the golden reference for *what the block should do*, and
this run compares against it too (every cycle, reported below) -- but a
difference between the model and the netlist can have two very different
causes, "P&R broke something" and "the RTL and the model already disagreed".
Running both legs through one testbench separates them mechanically instead
of by argument: a model divergence that appears in **both** legs was already
in the RTL, and a divergence that appears only in the ``gate`` leg was
introduced downstream of it.

What it does, once per scenario in ``scenarios.SCENARIOS``:

1. Reset the DUT.
2. Drive the scenario's per-cycle stimulus rows into ``trng_top``'s input
   ports, one row per clock cycle.
3. Step the **same** rows through ``design/trng_top/trng_top.py``'s
   behavioural ``TopLevel`` -- the same model the five ``level: behavioral``
   records under ``sim/records/`` were produced from -- and compare all four
   top-level outputs (``reg_rdata``, ``str_data``, ``str_valid``,
   ``ht_alarm``) every cycle.
4. Hash the DUT's complete per-cycle output trace (SHA-256 over every
   compared port on every cycle, ``x``/``z`` included verbatim), so
   leg-to-leg equivalence is an exact check over *all* cycles rather than
   over the truncated per-cycle detail the record quotes.
5. Write the per-cycle comparison statistics to the JSON file named by
   ``$TRNG_POST_ROUTE_RESULT``, after every scenario, so a killed run still
   leaves the scenarios it finished.

Cycle timing, and why the comparison is well-defined
-----------------------------------------------------
``trng_interface.py``'s ``step()`` computes its outputs "from the pre-edge
state" (its own comment) and *then* updates state, and ``trng_interface.v``
drives ``reg_rdata``/``str_data``/``str_valid``/``ht_alarm`` combinationally
from registers plus this cycle's inputs. So one model ``step(row)`` equals
"the DUT's outputs while ``row`` is applied and before the edge that consumes
it", and the comparison protocol follows directly:

    posedge ──┬── +DRIVE_NS ──────────── apply row ─────┐
              │                                          │
              │                    + sample_offset_ns ───┴── sample & compare
              └── +CLOCK_NS ─── next posedge: the edge that commits the row

``DRIVE_NS`` keeps the stimulus off the clock edge (so an input change is
never inside a flop's hold window), and the default
``sample_offset_ns = CLOCK_NS - 2*DRIVE_NS`` leaves the combinational cone a
full 40 ns to settle against a worst path OpenROAD's own post-route STA puts
at ~22 ns. Both are deliberately *loose*: this regression checks functional
equivalence under annotated delay, and the question "how much settling time
does the register-read path actually need" is asked separately and
quantitatively by the ``reg-read-walk-settle-sweep`` scenario, which walks
``sample_offset_ns`` down a ladder and reports where equality breaks.

An unresolved (``x``/``z``) output bit is counted separately from a
value mismatch, because the two have different causes and different fixes:
512 of the netlist's 708 flops are ``dffq`` (no reset port -- they are the
two 8x32-bit FIFO memories), so they hold ``x`` out of reset until written,
whereas the Python model starts every field at 0. Anywhere the design gates
those flops out of the output path (``cond_avail ? cond_mem[head] : 0``) the
``x`` never reaches a pin and the comparison is exact; anywhere it did reach
a pin, that would be a real finding about the netlist, not about the model,
and it is reported as its own count rather than folded into "mismatch".
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

TB_DIR = Path(__file__).resolve().parent
if str(TB_DIR) not in sys.path:
    sys.path.insert(0, str(TB_DIR))

import model_probe  # noqa: E402
import scenarios  # noqa: E402

REPO_ROOT = scenarios.REPO_ROOT
if str(REPO_ROOT / "design" / "trng_top") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "design" / "trng_top"))

import trng_top as top  # noqa: E402

#: Clock period, ns. 50 ns (20 MHz) is the constraint `layout/digital/build.py`
#: placed and routed against and the period `layout/digital/gen_sdf.py` timed
#: the SDF at -- not a new pick, and not a spec value (no issue in this
#: repository sets a digital Fmax requirement; see layout/digital/README.md's
#: "What may be cited from this, and what may not").
CLOCK_NS = float(os.environ.get("TRNG_POST_ROUTE_CLOCK_NS", "50"))

#: How long after a clock edge the stimulus for the next cycle is applied.
#: Keeps every input transition clear of the flops' hold windows.
DRIVE_NS = 5.0

#: Default settling time between the stimulus changing and the outputs being
#: sampled. See the module docstring.
DEFAULT_SAMPLE_OFFSET_NS = CLOCK_NS - 2 * DRIVE_NS

#: Compared every cycle: the complete set of `trng_top` output ports.
OUTPUT_PORTS = ("reg_rdata", "str_data", "str_valid", "ht_alarm")

#: Cap on how many individual diff/x rows and bus reads a scenario records.
#: The counts are always complete; only the per-cycle detail is truncated, so
#: a pathological run cannot write a 100 MB record.
DETAIL_CAP = 32

RESULT_PATH = Path(
    os.environ.get("TRNG_POST_ROUTE_RESULT", str(TB_DIR / "post_route_results.json"))
)

#: ``"rtl"`` (zero-delay reference) or ``"gate"`` (post-route + SDF). See the
#: module docstring.
LEG = os.environ.get("TRNG_POST_ROUTE_LEG", "gate")

#: The reference leg's own result file, when this is the ``gate`` leg. Absent
#: means "no reference available", which downgrades the leg-to-leg trace
#: assertions to a recorded observation rather than a verdict -- never to a
#: silent pass.
REFERENCE_PATH = os.environ.get("TRNG_POST_ROUTE_REFERENCE")

#: Accumulated across every scenario in this simulator process.
RESULTS: dict[str, dict] = {}


def _reference() -> dict:
    if not REFERENCE_PATH:
        return {}
    try:
        return json.loads(Path(REFERENCE_PATH).read_text()).get("scenarios", {})
    except (OSError, json.JSONDecodeError):
        return {}


def _flush_results() -> None:
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 2,
        "leg": LEG,
        "reference": REFERENCE_PATH,
        "clock_period_ns": CLOCK_NS,
        "drive_offset_ns": DRIVE_NS,
        "default_sample_offset_ns": DEFAULT_SAMPLE_OFFSET_NS,
        "output_ports": list(OUTPUT_PORTS),
        "scenarios": RESULTS,
    }
    RESULT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


#: The registered-handoff hypothesis probe lives in its own cocotb-free module
#: (`model_probe.py`) so `sim/tests/test_post_route_scenarios.py` can pin the
#: same finding on the PR-blocking CI path, where there is no simulator.
_registered_handoff_model = model_probe.registered_handoff_model


def _read(handle):
    """``(int_value_or_None, binary_string)`` for one output port.

    ``None`` means the port carried at least one ``x``/``z`` bit, which is
    tracked separately from a wrong value (see the module docstring).
    """
    text = str(handle.value)
    if "x" in text.lower() or "z" in text.lower():
        return None, text
    return int(handle.value), text


def _apply(dut, row: dict) -> None:
    dut.raw_bit.value = row["raw_bit"]
    dut.raw_valid.value = int(row["raw_valid"])
    # ring_bit[0] is ring 1 (design/xschem/trng_top.sch's ring_bit1), which is
    # index 0 of the model's ring_bit tuple -- the mapping
    # sim/tests/test_trng_top.py checks by name.
    ring = row["ring_bit"]
    dut.ring_bit.value = (ring[0] & 1) | ((ring[1] & 1) << 1)
    dut.reg_sel.value = int(row["reg_sel"])
    dut.reg_write.value = int(row["reg_write"])
    dut.reg_addr.value = row["reg_addr"]
    dut.reg_wdata.value = row["reg_wdata"]
    dut.str_ready.value = int(row["str_ready"])


def _idle(dut) -> None:
    _apply(dut, scenarios.cycle())


async def _reset(dut) -> None:
    """Assert the async reset for three full cycles and release it clear of
    an edge. The model is constructed fresh by the caller, which *is* the
    reset state on that side."""
    dut.rst_n.value = 0
    _idle(dut)
    for _ in range(3):
        await RisingEdge(dut.clk)
    await Timer(DRIVE_NS, unit="ns")
    dut.rst_n.value = 1


async def _drive_and_compare(dut, rows: list[dict], sample_offset_ns: float) -> dict:
    """Drive ``rows`` cycle by cycle, comparing every output against a fresh
    behavioural model. Returns the comparison statistics for one pass."""
    model = top.TopLevel()
    probe = _registered_handoff_model()
    probe_mismatch_cycles = 0
    started = time.time()

    # SHA-256 over the DUT's complete per-cycle output trace, and over the
    # model's, in the same canonical form. The DUT hash is what makes the
    # gate-vs-RTL check exact over every cycle rather than over the
    # DETAIL_CAP-truncated detail the record quotes; the model hash proves
    # both legs really did see identical stimulus (it must come out the same
    # in both, since `scenarios.py` is deterministic).
    dut_trace = hashlib.sha256()
    model_trace = hashlib.sha256()

    diffs: list[dict] = []
    probe_diffs: list[dict] = []
    unresolved: list[dict] = []
    bus_reads: list[dict] = []
    mismatch_cycles = 0
    unresolved_cycles = 0
    dut_alarm_cycle: int | None = None
    model_alarm_cycle: int | None = None

    for index, row in enumerate(rows):
        await RisingEdge(dut.clk)
        await Timer(DRIVE_NS, unit="ns")
        _apply(dut, row)
        await Timer(sample_offset_ns, unit="ns")

        expected = model.step(**row)
        probed = probe.step(**row)
        want = {
            "reg_rdata": int(expected.reg_rdata),
            "str_data": int(expected.str_data),
            "str_valid": int(bool(expected.str_valid)),
            "ht_alarm": int(bool(expected.ht_alarm)),
        }
        got: dict[str, int | None] = {}
        raw_text: dict[str, str] = {}
        for port in OUTPUT_PORTS:
            value, text = _read(getattr(dut, port))
            got[port] = value
            raw_text[port] = text

        # The trace is the raw binary strings, so an `x` is hashed as an `x`
        # rather than collapsing into the same digest as some integer.
        dut_trace.update(
            (f"{index}|" + "|".join(raw_text[p] for p in OUTPUT_PORTS) + "\n").encode()
        )
        model_trace.update(
            (f"{index}|" + "|".join(str(want[p]) for p in OUTPUT_PORTS) + "\n").encode()
        )

        probe_want = {
            "reg_rdata": int(probed.reg_rdata),
            "str_data": int(probed.str_data),
            "str_valid": int(bool(probed.str_valid)),
            "ht_alarm": int(bool(probed.ht_alarm)),
        }
        probe_bad = [
            p for p in OUTPUT_PORTS if got[p] is not None and got[p] != probe_want[p]
        ]
        if probe_bad or any(got[p] is None for p in OUTPUT_PORTS):
            probe_mismatch_cycles += 1
            if len(probe_diffs) < DETAIL_CAP:
                probe_diffs.append(
                    {
                        "cycle": index,
                        "ports": probe_bad,
                        "want": {p: probe_want[p] for p in probe_bad},
                        "got": {p: got[p] for p in probe_bad},
                        "as_committed_model_wanted": {p: want[p] for p in probe_bad},
                    }
                )

        bad = [p for p in OUTPUT_PORTS if got[p] is not None and got[p] != want[p]]
        unknown = [p for p in OUTPUT_PORTS if got[p] is None]
        if bad:
            mismatch_cycles += 1
            if len(diffs) < DETAIL_CAP:
                diffs.append(
                    {
                        "cycle": index,
                        "ports": bad,
                        "want": {p: want[p] for p in bad},
                        "got": {p: got[p] for p in bad},
                        "stimulus": {
                            k: (list(v) if isinstance(v, tuple) else v)
                            for k, v in row.items()
                        },
                    }
                )
        if unknown:
            unresolved_cycles += 1
            if len(unresolved) < DETAIL_CAP:
                unresolved.append(
                    {
                        "cycle": index,
                        "ports": unknown,
                        "binary": {p: raw_text[p] for p in unknown},
                    }
                )

        if dut_alarm_cycle is None and got["ht_alarm"] == 1:
            dut_alarm_cycle = index
        if model_alarm_cycle is None and want["ht_alarm"] == 1:
            model_alarm_cycle = index

        if row["reg_sel"] and not row["reg_write"] and len(bus_reads) < DETAIL_CAP:
            bus_reads.append(
                {
                    "cycle": index,
                    "reg_addr": row["reg_addr"],
                    "dut_reg_rdata": got["reg_rdata"],
                    "model_reg_rdata": want["reg_rdata"],
                }
            )

    return {
        "cycles": len(rows),
        "sample_offset_ns": sample_offset_ns,
        "dut_trace_sha256": dut_trace.hexdigest(),
        "model_trace_sha256": model_trace.hexdigest(),
        "mismatch_cycles": mismatch_cycles,
        "registered_handoff_probe_mismatch_cycles": probe_mismatch_cycles,
        "first_registered_handoff_probe_mismatches": probe_diffs,
        "unresolved_cycles": unresolved_cycles,
        "first_mismatches": diffs,
        "first_unresolved": unresolved,
        "bus_reads": bus_reads,
        "dut_first_alarm_cycle": dut_alarm_cycle,
        "model_first_alarm_cycle": model_alarm_cycle,
        "model_raw_samples": model.raw_samples,
        "model_startup_passes": model.health.startup_passes,
        "model_conditioned_words": model.cond.words_out,
        "wall_time_s": round(time.time() - started, 3),
    }


async def _run(dut, name: str) -> dict:
    """Run one named scenario, record it, and return its result."""
    scenario = scenarios.SCENARIOS[name]
    rows = scenario.build()
    clock = cocotb.start_soon(Clock(dut.clk, CLOCK_NS, unit="ns").start())
    try:
        if scenario.expect == "settle-sweep":
            sweep = []
            for offset in scenario.sweep_offsets_ns:
                await _reset(dut)
                pass_result = await _drive_and_compare(dut, rows, offset)
                sweep.append(
                    {
                        "sample_offset_ns": offset,
                        "mismatch_cycles": pass_result["mismatch_cycles"],
                        "unresolved_cycles": pass_result["unresolved_cycles"],
                        "dut_trace_sha256": pass_result["dut_trace_sha256"],
                        "registered_handoff_probe_mismatch_cycles": pass_result[
                            "registered_handoff_probe_mismatch_cycles"
                        ],
                    }
                )
            clean = [
                entry["sample_offset_ns"]
                for entry in sweep
                if entry["mismatch_cycles"] == 0 and entry["unresolved_cycles"] == 0
            ]
            result = {
                "kind": "settle-sweep",
                "cycles_per_pass": len(rows),
                "sweep": sweep,
                "smallest_clean_offset_ns": min(clean) if clean else None,
                "largest_dirty_offset_ns": max(
                    (
                        entry["sample_offset_ns"]
                        for entry in sweep
                        if entry["mismatch_cycles"] or entry["unresolved_cycles"]
                    ),
                    default=None,
                ),
            }
        else:
            await _reset(dut)
            offset = (
                scenario.sample_offset_ns
                if scenario.sample_offset_ns is not None
                else DEFAULT_SAMPLE_OFFSET_NS
            )
            result = await _drive_and_compare(dut, rows, offset)
            result["kind"] = scenario.expect
        result["counterpart"] = scenario.counterpart
        result["expect"] = scenario.expect
        result["leg"] = LEG
        if scenario.shortened_from:
            result["shortened_from"] = scenario.shortened_from
        reference = _reference().get(name)
        if reference is not None:
            result["reference_dut_trace_sha256"] = reference.get("dut_trace_sha256")
            result["reference_model_trace_sha256"] = reference.get("model_trace_sha256")
            result["matches_reference_trace"] = (
                reference.get("dut_trace_sha256") == result.get("dut_trace_sha256")
            )
            result["reference_mismatch_cycles"] = reference.get("mismatch_cycles")
    finally:
        clock.cancel()
    RESULTS[name] = result
    _flush_results()
    return result


def _assert_no_unresolved(name: str, result: dict) -> None:
    """No `x`/`z` may reach a top-level pin, in either leg.

    This is the one assertion that is a verdict about the netlist on its own
    terms rather than a comparison: 512 of the netlist's 708 flops have no
    reset port, so `x` exists inside it out of reset by construction, and the
    claim being checked is that the design's own availability gating keeps it
    off the pins.
    """
    assert result["unresolved_cycles"] == 0, (
        f"{name} [{LEG}]: {result['unresolved_cycles']} of {result['cycles']} cycles "
        f"had an unresolved (x/z) output bit -- first: {result['first_unresolved'][:3]}"
    )


def _assert_matches_reference(name: str, result: dict) -> None:
    """The post-route netlist must reproduce the RTL's trace exactly.

    **This is the post-layout verification verdict** (T1 item 7's digital
    column): synthesis, clock-tree insertion, cell resizing and routing must
    not have changed what the design does, under the annotated cell delays of
    the corner it was routed at.

    In the ``rtl`` leg there is nothing to compare against, so this is a
    no-op there -- and deliberately *not* a silent pass in the ``gate`` leg: a
    missing reference fails rather than being skipped, because "the reference
    was not available" and "the netlist matches" must never look the same.
    """
    if LEG != "gate":
        return
    assert "matches_reference_trace" in result, (
        f"{name}: no reference-leg trace to compare against "
        f"(TRNG_POST_ROUTE_REFERENCE={REFERENCE_PATH!r}) -- a post-route run "
        "with no RTL reference cannot answer whether P&R preserved behaviour"
    )
    assert result["reference_model_trace_sha256"] == result["model_trace_sha256"], (
        f"{name}: the two legs' behavioural-model traces differ, so they did "
        "not see identical stimulus -- the comparison below would be "
        "meaningless"
    )
    assert result["matches_reference_trace"], (
        f"{name}: the post-route netlist's output trace differs from the RTL's "
        f"({result['dut_trace_sha256'][:16]} vs "
        f"{result['reference_dut_trace_sha256'][:16]}). Cycles differing from "
        f"the behavioural model: {result['mismatch_cycles']} here vs "
        f"{result['reference_mismatch_cycles']} in the RTL leg; first: "
        f"{result['first_mismatches'][:3]}"
    )


# --------------------------------------------------------------------------- #
# One test per scenario. Written out rather than generated so the test names
# in `results.xml` (and so in `klt`'s own per-test breakdown, and so in the
# evidence record) are greppable strings in this file.
# --------------------------------------------------------------------------- #


@cocotb.test()
async def smoke(dut):
    """sim/tb/smoke-trng-top's ten transistor-derived raw bits."""
    result = await _run(dut, "smoke")
    _assert_no_unresolved("smoke", result)
    _assert_matches_reference("smoke", result)


@cocotb.test()
async def startup_and_regfile(dut):
    """sim/tb/interface-regfile: a full start-up window plus the register bus."""
    result = await _run(dut, "startup-and-regfile")
    assert result["model_startup_passes"] == 1, (
        "scenario did not complete a DR-0002 start-up window -- the stimulus "
        "is wrong, not the DUT"
    )
    _assert_no_unresolved("startup-and-regfile", result)
    _assert_matches_reference("startup-and-regfile", result)


@cocotb.test()
async def conditioner_blocks(dut):
    """sim/tb/conditioner-crc32: two 256-bit blocks, read out through DATA."""
    result = await _run(dut, "conditioner-blocks")
    assert result["model_conditioned_words"] >= 2, (
        "scenario produced fewer than two conditioned words -- the stimulus "
        "is wrong, not the DUT"
    )
    _assert_no_unresolved("conditioner-blocks", result)
    _assert_matches_reference("conditioner-blocks", result)


@cocotb.test()
async def rct_stuck_output(dut):
    """sim/tb/health-test-fault-injection: DR-0002 stuck-output detection."""
    result = await _run(dut, "rct-stuck-output")
    _assert_no_unresolved("rct-stuck-output", result)
    _assert_matches_reference("rct-stuck-output", result)
    assert result["dut_first_alarm_cycle"] is not None, (
        "ht_alarm never rose for a stuck raw source"
    )


@cocotb.test()
async def ring1_stuck(dut):
    """sim/tb/ring-liveness-fault-injection: DR-0016 per-ring watchdog."""
    result = await _run(dut, "ring1-stuck")
    _assert_no_unresolved("ring1-stuck", result)
    _assert_matches_reference("ring1-stuck", result)
    assert result["dut_first_alarm_cycle"] is not None, (
        "the per-ring watchdog never fired for a frozen ring"
    )


@cocotb.test()
async def reg_read_walk(dut):
    """A register read every cycle: the positive half of the SDF control."""
    result = await _run(dut, "reg-read-walk")
    _assert_no_unresolved("reg-read-walk", result)
    _assert_matches_reference("reg-read-walk", result)


@cocotb.test()
async def reg_read_walk_early_sample(dut):
    """CONTROL: the same walk sampled 0.1 ns after the inputs change.

    The whole regression rests on the SDF actually being in the loop, and a
    silently-unannotated gate-level run looks *exactly* like a green one --
    that is the failure mode `klt functional-verification`'s own transcript
    gate exists for, and this is a second, independent check of the same
    thing that does not depend on reading a transcript.

    The required outcome is leg-dependent, which is what makes it a control
    rather than a coincidence:

    * ``gate`` leg -- annotated cell delays: sampling 0.1 ns after the inputs
      move CANNOT see settled outputs, so this trace MUST differ from the
      same walk's settled trace. Equality here would mean the run was
      effectively zero-delay and every other scenario's pass was vacuous.
    * ``rtl`` leg -- zero delay: the outputs settle in the same delta cycle,
      so this trace MUST equal the settled one. That is the same control
      returning the opposite answer on a DUT with no delay in it, which is
      what rules out "the comparison is just noisy".
    """
    result = await _run(dut, "reg-read-walk-early-sample")
    settled = RESULTS.get("reg-read-walk")
    assert settled is not None, (
        "reg-read-walk must run before its early-sample control (cocotb runs "
        "tests in definition order)"
    )
    same = result["dut_trace_sha256"] == settled["dut_trace_sha256"]
    if LEG == "gate":
        assert not same, (
            "control did not fire: the gate netlist produced an identical "
            "trace 0.1 ns after its inputs changed as it did 40 ns after, "
            "which means no delay was back-annotated and every other "
            "scenario's PASS is vacuous"
        )
    else:
        assert same, (
            "the zero-delay RTL leg produced a different trace when sampled "
            "0.1 ns after its inputs changed -- the sampling protocol itself "
            "is unsound, so nothing the gate leg reports can be attributed "
            "to annotated delay"
        )


@cocotb.test()
async def reg_read_walk_settle_sweep(dut):
    """Walk the sampling offset down a ladder and report where equality breaks."""
    result = await _run(dut, "reg-read-walk-settle-sweep")
    assert result["smallest_clean_offset_ns"] is not None, (
        "no sampling offset in the ladder produced an exact match -- the "
        f"sweep is: {result['sweep']}"
    )
    if LEG == "gate":
        assert result["largest_dirty_offset_ns"] is not None, (
            "every sampling offset in the ladder matched, including the "
            "shortest -- as in the control above, that means no annotated "
            f"delay is in the loop. Sweep: {result['sweep']}"
        )
    else:
        assert result["largest_dirty_offset_ns"] is None, (
            "the zero-delay RTL leg needed settling time, which it cannot: "
            f"sweep is {result['sweep']}"
        )
