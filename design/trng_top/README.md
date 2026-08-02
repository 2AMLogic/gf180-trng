# `design/trng_top/` — the top-level integration (#27)

The block that closes the gap #15 (DRC/LVS) and #16 (floorplan) both assumed
was already closed: one place that instantiates the entropy source (#7), the
sampler (#9), the conditioner (#8), the health tests (#11) and the interface
(#26) per their pinouts, and one nominal-corner record showing bits produced
end to end.

It is split across two verification levels because
[`DR-0009`](../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)
already fixed where that split sits for this repository, and this issue
inherits the boundary rather than re-litigating it:

```
   transistor level (ngspice)              behavioural (Python / RTL)
  ┌───────────────────────────┐    ┌──────────────────────────────────────┐
  │ design/xschem/trng_top.sch │    │            design/trng_top/           │
  │                            │    │                                        │
  │  sampler_core.sym          │    │  trng_top.py / trng_top.v              │
  │  (#7 entropy source,       │raw │                                        │
  │   #9 sampler) ─────────────┼bit,┼─►  conditioner (#8) ─┐                 │
  │                            │raw │                       │                │
  │  en1/en2/vddr1/vddr2/      │val-┼─►  health tests (#11) ┼─► interface     │
  │  vdd/vss ◄──────────────── │id  │                       │   (#26) ──►    │
  │                            │ring│  ◄────────────────────┘   DATA/RAW_DATA│
  │                            │bit1┼─►  ring liveness      │                │
  │                            │/2  │    (DR-0016) ─────────┘                │
  └───────────────────────────┘    └──────────────────────────────────────┘
         DR-0001 raw tap = the DR-0009 analog/digital verification boundary
```

Five signals cross that boundary, not three: the raw tap
(`raw_bit`/`raw_valid`) plus DR-0016's two per-ring digitized samples
(`ring_bit1`/`ring_bit2`, from the same `sampler_core` and the same
`sampler_dff` cell). The liveness monitor's `ring_stuck_any` then joins
`ht_fail_rct`/`ht_fail_apt` as the third input of the interface's single
latch — one mechanism, three sources.

## Files

| File | What it is |
|---|---|
| [`../xschem/trng_top.sch`](../xschem/trng_top.sch) | The analog half: instantiates `sampler_core.sym` (#7 + #9) unmodified. Exported/checked by `design/netlist.py` like any other top cell — `design/trng_top.spice` is the generated netlist. |
| `trng_top.py` | **Normative** behavioural wiring of the four digital blocks (`crc32_conditioner.Conditioner`, `rct_apt.HealthTest`, `ring_liveness.RingLivenessMonitor`, `trng_interface.Interface`), one `TopLevel.step()` call per sampler-clock edge. Documents, in its own docstring, the registered-vs-combinational ordering the wiring depends on. |
| `trng_top.v` | Synthesisable RTL: instantiates `trng_conditioner_crc32`, `trng_health_test`, `trng_ring_liveness` and `trng_interface` with plain wires, no added logic. Compile-checked (and, where a stimulus-comparable path exists, cross-checked against `trng_top.py`) by `sim/tests/test_trng_top.py`. |

## Why the schematic does not also draw the digital blocks

`design/README.md` already states it for the three digital directories:
"None has a schematic or a netlist, so `design/netlist.py` neither reads nor
checks them." Drawing `trng_conditioner_crc32`/`trng_health_test`/
`trng_interface` as SPICE subcircuits in `trng_top.sch` would mean one of
two things, and both are worse than the split this directory keeps:

- fabricating device-level models for them, contradicting the ratified
  DR-0009 split and reopening the cost problem DR-0009 §"The cost argument"
  measured directly (a single conditioner output word is a ~2-day
  transistor-level run); or
- drawing empty placeholder subcircuits that look wired but cannot be
  simulated, which is a worse failure mode than naming the boundary
  explicitly — a reader who trusts the picture would not know it lied.

So `trng_top.sch`'s text block documents the pin-for-pin handoff instead,
and `sim/tests/test_trng_top.py` checks it mechanically: that
`clk`/`rst_n`/`raw_bit`/`raw_valid` on the analog side of the raw tap
(`design/sampler_core.spice`'s `.subckt` signature, which `trng_top.spice`
wraps unchanged) name the same four signals the conditioner's and the
health tests' own RTL ports declare. The per-ring taps get the same check
plus one the raw tap does not need: the schematic names them as scalar pins
(`ring_bit1`/`ring_bit2`, 1-based like `ro1`/`ro2`) while the RTL carries one
`ring_bit[N_RINGS-1:0]` vector, so the count and the `ring_bit<i+1>` →
`ring_bit[i]` mapping are asserted by name — a swap there is invisible in
every waveform, because both wires carry plausible bits. That is the check that would catch a
signal "wired backwards" between the two halves — the risk this issue's own
curation flagged — in the one place it is actually checkable, since DR-0009
already rejected mixed-signal co-simulation as the mechanism that would
catch it by running the whole thing together.

## Registers, streaming port, and what "bits out" means here

`trng_top.py`/`trng_top.v` expose exactly `design/interface/README.md`'s
contract: `CTRL`/`STATUS`/`DATA`/`RAW_DATA` plus the streaming port. Nothing
new is added at this level — no bus protocol adaptation and no
clock-domain crossing, both of which `design/interface/README.md` already
names as "#27's wrapper, deliberately not baked in" upstream, and which
remain undecided here too.

## Running things

```sh
# Netlist staleness guard, now covering trng_top too.
python3 design/netlist.py --check

# Pinout cross-check, RTL/model wiring tests, and (where iverilog is
# installed) the RTL compile/elaborate check.
python3 -m unittest sim.tests.test_trng_top -v

# The nominal-corner smoke demonstration (see sim/tb/smoke-trng-top/).
python3 sim/tb/smoke-trng-top/run_demo.py --no-write
```

## What is *not* here

- **A ratified worst-corner `H`.** `trng_top.py` uses the health test's
  DR-0002 draft `H0 = 0.5` default for both `C_RCT` and DR-0016's `C_LIVE`
  (they come from the same `rct_apt.c_rct(h)` call), same as every other
  block that consumes it today.
- **Per-ring failure reporting.** `ring_stuck[i]` is a named net in
  `trng_top.v` and nothing reads it: `STATUS.HT_FAIL_RING` says a ring
  stopped, not which one, so DR-0013's published register map does not
  acquire an `N_RINGS` dependency.
- **A full start-up-window or entropy-quality demonstration at this level.**
  The smoke sim's job (per this issue's own curation) is proving the
  assembled netlist produces bits end to end at one nominal corner, not
  re-verifying entropy quality — that stays each constituent block's own
  responsibility (`sim/tb/sampler-array-digitize/`, `sim/tb/rostage-noise/`,
  `sim/tb/health-test-fault-injection/`, `sim/tb/conditioner-crc32/`,
  `sim/tb/interface-regfile/`).
- **Digital timing closure**, still owed per DR-0009 rule 6.
- **DRC/LVS and floorplanning** — #15 and #16, which now depend on this
  issue for a merged top-level pinout instead of assuming one.
