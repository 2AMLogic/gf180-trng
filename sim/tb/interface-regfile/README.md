# `sim/tb/interface-regfile/` — interface/register-block demonstration (behavioral)

Raw tap in, `DATA` / `RAW_DATA` / streaming out. The demonstration run
[`DR-0013`](../../../spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md)
cites, produced at the level fixed by
[`DR-0009`](../../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md).

**This testbench has no `tb.json` and is not an ngspice testbench.** Per
DR-0009 rule 7, a behavioral testbench is deliberately invisible to
`sim/run_corners.py` (which only discovers directories containing a
`tb.json`), so it cannot be swept across a PVT grid it has no meaning on.
It is run directly:

```sh
python3 sim/tb/interface-regfile/run_demo.py --no-write   # print only
python3 sim/tb/interface-regfile/run_demo.py              # mint records
python3 sim/tb/interface-regfile/run_demo.py --scenario ht-gate
```

## What is under test

Both digital blocks, wired as `trng_top` (#27) will wire them:

```
  source_model (declared synthetic)
        │
        ├──────────────► trng_conditioner_crc32  (#8, DR-0008)
        │                        │ cond_word/cond_valid
        │   cond_en / cond_flush │
        └──────────────► trng_interface (#26, DR-0013) ──► DATA / RAW_DATA / streaming
```

The conditioner's `en`/`flush` are taken from the interface's **own outputs in
the same cycle** (`Interface.peek_control`), so what runs is the real
inter-block contract rather than a scripted approximation of it. That is the
point of running the two together at all — either block alone can be checked
by its unit tests.

## Files

| File | What it is |
|---|---|
| `run_demo.py` | The testbench. Runs the fixed scenario set and writes one append-only evidence record per scenario. |
| `tb_rtl_equivalence.v` | Icarus Verilog testbench driving `design/interface/trng_interface.v` from a per-cycle stimulus file, for the cycle-for-cycle RTL/model equivalence check in `sim/tests/test_interface.py`. |

The raw source is `sim/tb/conditioner-crc32/source_model.py` — reused rather
than duplicated, so both digital blocks are driven by the same declared
synthetic source with the same seed discipline.

## Scenarios

| Scenario | What it is in the set for |
|---|---|
| `startup` | DR-0002's start-up gate: the conditioned path is held gated for the whole 1024-sample window while the raw path runs from the first sample. Measures the samples to the first conditioned word. |
| `ht-gate` | DR-0002's latch-and-gate and its recovery: a failure latches, gates, flushes; `RAW_DATA` keeps working throughout; resuming needs the explicit write-1-to-clear *and* a fresh start-up pass. |
| `mode-switch` | DR-0001 §2's flush rule, in both directions: nothing survives the switch in either FIFO. |
| `overrun` | A consumer that stops reading: the FIFOs drop the incoming word rather than a buffered one, and `OVF_DATA`/`OVF_RAW` say so. |

## What these runs do and do not show

They show the **block and the contract between blocks**: the gating, the two
flush scopes, the FIFO behaviour, and that the `en`/`flush` the conditioner's
README specifies is actually what this block drives.

The `startup` scenario also puts a number on the ratified time-to-first-valid
arithmetic: **1280 raw samples** from power-on to the first readable
conditioned word — DR-0002's 1024-sample start-up window plus DR-0008's
256-sample conditioner fill, non-overlapping, which is exactly what the
README's `≥ ~1.28 ms at 1 Mbps` row claims. Note the unit: this record counts
**samples**, not seconds. Converting is a corner-dependent system question
(DR-0003, DR-0012) that a behavioral record may not answer.

They show **nothing about the entropy source**, and nothing about the health
tests:

- The raw source is a declared synthetic IID biased coin whose min-entropy is
  an input parameter, not a jitter-sampled ring oscillator.
- The health-test block (#11) does not exist yet. These runs stand in for
  exactly the part of it this block contracts with — a counter that pulses
  `ht_startup_pass` after 1024 consecutive raw samples and restarts on
  `startup_req` — and inject failures on a script. No RCT or APT runs here.

They also have **no P/V/T corner**, so they may not be cited for rate, power,
or timing (DR-0009 rule 3).
