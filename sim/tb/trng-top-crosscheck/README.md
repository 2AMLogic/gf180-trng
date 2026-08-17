# `sim/tb/trng-top-crosscheck/` — assembled RTL vs. assembled model, cycle by cycle (#176)

Closes the coverage gap #176 found: `sim/tests/test_trng_top.py`'s
pre-existing `PinoutCrossCheckTests` and `RtlWiringTests` check that
`design/trng_top/trng_top.v` elaborates and that its pins line up with the
behavioural model's, but neither one runs the assembled RTL and the
assembled model over the same stimulus and compares their outputs cycle by
cycle. That gap is exactly what let `TopLevel.step` hand
`ht_startup_pass` and `cond_word`/`cond_valid` to the interface
combinationally, in the same model cycle they were computed, for a period
before this fix — a same-cycle-vs-next-cycle skew that a pinout check or an
elaboration check cannot see, and that only showed up when #147's (still
unbuilt, as of this writing) post-route gate-level re-run happened to
compare per-cycle traces.

**This testbench has no `tb.json` and is not an ngspice testbench.** Per
DR-0009 rule 7, a behavioral testbench is deliberately invisible to
`sim/run_corners.py`. It is driven by `sim/tests/test_trng_top.py`'s
`AssembledCrossCheckTests`, not run standalone.

## What is under test

```
  stimulus vector (Python, sim/tests/test_trng_top.py)
        │
        ├──────────────► design/trng_top/trng_top.TopLevel        (the model)
        │
        └──────────────► design/trng_top/trng_top.v via Icarus Verilog  (the RTL)
                                    │
                          tb_rtl_equivalence.v drives it, dumps
                          reg_rdata/str_data/str_valid/ht_alarm every cycle
```

Both sides see byte-for-byte the same per-cycle `raw_bit`/`raw_valid`/
`ring_bit`/register-bus stimulus. `sim/tests/test_trng_top.py` requires the
two per-cycle output traces to be identical -- not just the final state, and
not just the sequence of conditioned words (which
`sim/tb/conditioner-crc32/tb_rtl_equivalence.v` already checks for the
conditioner alone, and which is blind to a one-cycle timing skew the way a
sequence comparison always is).

## Files

| File | What it is |
|---|---|
| `tb_rtl_equivalence.v` | Icarus Verilog testbench driving the assembled `design/trng_top/trng_top.v` from a per-cycle stimulus file. |

## Sampling convention

Same convention `sim/tb/interface-regfile/tb_rtl_equivalence.v` uses (DR-0013
"Flush timing"): stimulus is applied after the falling edge, the
combinational outputs are sampled one time unit later (before the next
rising edge), then the edge is let through to update every block's state.
That is exactly the order `TopLevel.step` computes in, one Python call per
iteration of the testbench's stimulus loop.

## Why this is a real cross-block check, not a relabeled per-block one

`design/conditioner/`, `design/health_test/` and `design/interface/` each
already have their own `tb_rtl_equivalence.v`, but each one drives its block
in isolation against that block's own bit-exact model -- neither the RTL side
nor the model side of any of those three checks a handoff *between* blocks,
because there is only one block instantiated. `trng_top.v` is where
`crc32_conditioner.v`'s `cond_word`/`cond_valid` and `rct_apt.v`'s
`ht_startup_pass` actually reach `trng_interface.v`'s input pins, and
`design/trng_top/trng_top.py`'s `TopLevel.step` is where the equivalent
handoff happens in the model -- so this is the one place in the repository
where a same-cycle-vs-next-cycle skew on either handoff is even expressible,
let alone catchable.
