# `sim/tb/smoke-trng-top/` — top-level assembly smoke test (#27)

One nominal-corner (`tt` / 27 C / 3.30 V) demonstration that the five-block
assembly — entropy source (#7), sampler (#9), conditioner (#8), health
tests (#11), interface (#26) — produces bits end to end. Produced at the
level fixed by
[`DR-0009`](../../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md),
against the wiring in [`design/trng_top/`](../../../design/trng_top/).

**This testbench has no `tb.json` and is not an ngspice testbench.** Per
DR-0009 rule 7, a behavioral testbench is deliberately invisible to
`sim/run_corners.py`. It is run directly:

```sh
python3 sim/tb/smoke-trng-top/run_demo.py --no-write   # print only
python3 sim/tb/smoke-trng-top/run_demo.py               # mint a record
```

## What is under test

```
  sim/records/2026-08-01-sampler-array-digitize-03.md
  (transistor-derived, tt/27C/3.30V, 10 raw bits: 0001111100)
        │
        └──► trng_top.TopLevel  (design/trng_top/trng_top.py)
                 │        │        │
                 ▼        ▼        ▼
           conditioner  health   interface ──► DATA / RAW_DATA / STATUS
              (#8)      tests      (#26)        / streaming
                        (#11)
```

Unlike `sim/tb/interface-regfile/`'s demonstration (conditioner + interface
only, driven by a declared synthetic source, with a stand-in health-test
counter), this one wires the **real** health-test model in too and closes
the `startup_req` loop for real — see `trng_top.py`'s own docstring for the
registered-vs-combinational ordering that loop depends on.

## Files

| File | What it is |
|---|---|
| `raw_source.py` | Reads the ten transistor-derived raw bits straight out of the already-committed `sim/tb/sampler-array-digitize/` record, without re-running ngspice. |
| `run_demo.py` | The testbench. Drives `trng_top.TopLevel` with those ten bits plus one register-bus read, and writes one append-only evidence record. |

## Why ten bits, and what this does and does not show

Ten raw bits is what the cited transistor-level record has — a longer
capture would cost the better part of an hour of ngspice per corner (see
that record's own `wall_time`), which is exactly the cost DR-0009's own
argument section measured and is not what a *smoke* test is for. It shows:

- the raw tap's four signals (`clk`/`rst_n`/`raw_bit`/`raw_valid`) reach the
  conditioner and the health tests with the names each block's own RTL
  declares (mechanically checked, not just drawn — see
  `sim/tests/test_trng_top.py`);
- the conditioner's and the health tests' outputs reach the interface, and
  the interface's `cond_en`/`cond_flush`/`startup_req` reach back, without
  a runtime error or a stuck state;
- the register bus is live (the final `STATUS` read in every record).

It does **not** show entropy quality, rate, power, timing closure, or a
completed start-up window / first conditioned word — all corner-dependent
or length-dependent claims this record's `n/a` corner fields and DR-0009
rule 3 forbid it from making. Those remain the constituent blocks' own
jobs, at the length and PVT coverage each already has:
`sim/tb/sampler-array-digitize/`, `sim/tb/rostage-noise/`,
`sim/tb/conditioner-crc32/`, `sim/tb/health-test-fault-injection/`,
`sim/tb/interface-regfile/`.
