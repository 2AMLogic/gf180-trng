# `sim/tb/trng-top-post-route/` — the digital suite, re-run on the placed-and-routed netlist

The digital half of [#140][gf140]'s T1 checklist **item 7, "post-layout
verification"** — the item that had to read *FAIL* for the digital partition
because no post-route netlist existed to re-run anything against. It does now
([#111][gf111] / PR #172), so this directory re-runs the digital functional
suite against it, with timing back-annotated, and records what changed.

```sh
python3 sim/tb/trng-top-post-route/run_demo.py --check-env   # what this needs, and whether it is here
python3 sim/tb/trng-top-post-route/run_demo.py --no-write    # run both legs, print, mint nothing
python3 sim/tb/trng-top-post-route/run_demo.py               # run both legs and mint a record
```

Like every other testbench under `sim/tb/`, this one has **no `tb.json`**: it
is not an ngspice testbench, so `sim/run_corners.py` cannot discover it and
must not sweep it over a PVT grid it has no meaning on
([DR-0009][dr9] rule 7).

## What is under test, and against what

```
  scenarios.py  ── one per-cycle stimulus row list per behavioural suite member
        │
        ├──►  RTL leg    design/trng_top/trng_top.v + 4 child modules
        │               zero delay, no SDF                    ── reference
        │
        ├──►  GATE leg   layout/digital/trng_top.pnr.v (2447 cells, CTS
        │               buffers and resized cells included)
        │               + layout/digital/trng_top.sdf via $sdf_annotate
        │
        └──►  MODEL      design/trng_top/trng_top.py  ── the same behavioural
                        model the five `level: behavioral` records came from
```

Every cycle, all four of `trng_top`'s outputs (`reg_rdata`, `str_data`,
`str_valid`, `ht_alarm`) are compared, and each leg's complete output trace is
hashed (SHA-256 over every port on every cycle), so leg-to-leg equivalence is
exact over all cycles rather than over a sampled subset.

**The verdict of a post-layout re-run is GATE vs RTL**, and the model is the
third opinion. That split is the point: a difference between the netlist and
the model can mean "P&R broke something" or "the RTL and the model already
disagreed", and running both legs through one testbench separates those
mechanically instead of by argument.

## Files

| File | What it is |
|---|---|
| `scenarios.py` | The per-cycle stimulus. One scenario per behavioural suite member, reusing that testbench's **own** source model at the same label and seed, plus three scenarios that only exist at this level. No simulator, no netlist — importable and cheap. |
| `post_route_tb.py` | The cocotb regression `klt functional-verification` imports: drives the DUT, steps the model, compares, hashes, writes `comparison.json`. |
| `model_probe.py` | The registered-handoff probe — importable without cocotb, so `sim/tests/` can use it too. It found #176; it now guards the comparison's sensitivity to that class of defect. |
| `run_demo.py` | Environment checks, the two `klt` requests, the pass/fail derivation, and the append-only evidence record. |

## The five suite members, re-expressed at the top level

Four of the five behavioural suite members drive **one sub-block** each. There
is no gate-level equivalent of that: `klt synthesize` deliberately produces one
netlist for the whole digital partition (`design/synth.py`'s "One netlist, not
five") and `klt place-and-route` flattens it, so `trng_top.pnr.v` is a single
`module trng_top` with no sub-block hierarchy left to bind a per-block
testbench to. Every sub-block's stimulus and observable therefore travels
through `trng_top`'s own pins:

| Behavioural testbench | Scenario here | Driven through | Observed through |
|---|---|---|---|
| `sim/tb/smoke-trng-top/` | `smoke` | the same ten transistor-derived raw bits | all four outputs |
| `sim/tb/interface-regfile/` | `startup-and-regfile` | `reg_*` bus + `raw_bit` | `reg_rdata`, `str_*` |
| `sim/tb/conditioner-crc32/` | `conditioner-blocks` | `raw_bit`/`raw_valid` | `DATA` reads |
| `sim/tb/health-test-fault-injection/` | `rct-stuck-output` | `raw_bit`/`raw_valid` | `ht_alarm`, `STATUS` |
| `sim/tb/ring-liveness-fault-injection/` | `ring1-stuck` | `ring_bit[1:0]` | `ht_alarm`, `STATUS` |

Plus three that have no behavioural counterpart and exist only to keep this
level honest: `reg-read-walk` (a register read every cycle, so `reg_rdata`
changes on every one), `reg-read-walk-early-sample` (the annotation control,
below) and `reg-read-walk-settle-sweep` (the same walk at a ladder of sampling
offsets).

## The annotation control, and why there is one

A gate-level run whose SDF silently failed to apply is indistinguishable from a
green run — `vvp` exits 0 after skipping an annotation it could not apply. `klt
functional-verification` guards that by scanning both Icarus transcripts before
it will report `annotated: true`, and this directory adds a second, independent
check that does not depend on reading a transcript at all:

`reg-read-walk-early-sample` re-runs the identical stimulus sampled **0.1 ns**
after the inputs change instead of 40 ns. The required outcome is
leg-dependent, which is what makes it a control rather than a coincidence:

- **gate leg** — annotated cell delay: the trace **must differ** from the
  settled one. Equality would mean the run was effectively zero-delay and every
  other scenario's pass was vacuous.
- **rtl leg** — zero delay: the same control **must match**, because there is
  no delay to wait for.

`reg-read-walk-settle-sweep` then turns that into a number: the smallest
sampling offset at which the register-read path is fully settled. It is a
**lower bound** on that path's real delay, never an Fmax figure — see the
coverage limits below.

## What this covers, and what it does not

The evidence record this mints states the coverage limits next to its own
numbers; they are summarised here because they are the reason to trust or
distrust the result, in the same "coverage honesty" style
[`layout/digital/README.md`](../../../layout/digital/README.md) uses for the
DRC deck's gaps and `layout/README.md` for LVS's.

**Modelled**: per-instance cell delay (`IOPATH`), from the resolved liberty at
`ss_125C_3v00` — the corner the design was placed and routed at — at the
as-built netlist's real fan-out, including the CTS buffers and the drive
strengths P&R resized to.

**Not modelled**, and therefore not claimable:

- **Interconnect (wire) delay — none at all.** `layout/digital/gen_sdf.py`
  explains why the alternative was worse: the only route to real routed
  parasitics is `klt place-and-route`'s `post_route_spef`, which extracts from
  a DEF→GDS merge that is geometrically wrong by a factor of two
  ([klayout-tools#1090][klt1090]), and an SDF whose interconnect delays are
  wrong by a data-dependent factor is worse than one that models none.
  Consequence: every delay here is optimistic, and the settle bound is a floor.
- **Setup/hold/width checking — none of it, not a weaker version of it.**
  Icarus 13.0 drops it twice: it implements no SDF `TIMINGCHECK` annotation
  (one `TIMINGCHECK not supported` line per flop) *and* no
  `$setup`/`$hold`/`$width` at all (a `Timing checks are not supported`
  warning per check while elaborating the cell library), so the `notifier`
  regs those checks would drive never fire. **A violation this run did not
  report is not evidence of anything.** The run models cell delay and
  propagates it; that is the whole of its timing content. Signoff timing stays
  with OpenROAD's own STA and [#145][gf145]. Both counts are derived from the
  run's own transcripts and quoted in the record. That `klt`'s response cannot
  express this distinction is filed generically upstream as
  [klayout-tools#1102][klt1102].
- **A minority of IOPATH arcs.** Icarus cannot elaborate an `ifnone`-qualified
  edge-sensitive `specify` path, which is the shape
  `xor`/`xnor`/`mux`/`addf`/`addh` use for their select/toggle inputs; those
  arcs run at the library default delay. `gen_sdf.py` derives the exact list
  mechanically and the record counts them.
- **Anything other than one corner.** One `.lib` deck, one voltage, one
  temperature. No parasitic coupling, no IR drop, no on-chip variation, no
  SSTA. The power grid is not in this simulation, and per [#171][gf171] it is
  not in the committed layout yet either.
- **Statistics.** Each scenario runs the shortest prefix that exercises the
  mechanism it is named for; `Scenario.shortened_from` records the behavioural
  length it was cut down from (8192–131072 samples, for scenarios that make
  statistical claims). Monobit balances, observed false-positive rates and the
  SP 800-90B arithmetic stay with the behavioural records. What transfers to
  the netlist is functional equivalence on the stimulus actually run.
- **Internal state.** The behavioural testbenches read a block's counters
  directly; this one sees only pins. A divergence that never reaches a pin on
  this stimulus is not detected here.

**The behavioural records keep their level.** This directory adds a level
(`level: gate-simulation`, see [`sim/README.md`](../../README.md)); it does not
reclassify the existing `level: behavioral` records, which remain citable
exactly as far as DR-0009 rule 3 allows.

## What the per-block suite could not see

Two findings came out of driving the *assembled* top level rather than one
block at a time. Both are recorded because nothing else in the repository
documents them.

1. **`trng_top` has liveness inputs the per-block testbenches do not.**
   Leaving `ring_bit[1:0]` idle is not "no stimulus", it is two dead rings:
   DR-0016's watchdog fires at `C_LIVE` = 81 cycles, latches `ht_alarm` and
   gates the conditioned path. A scenario aimed at the conditioner or the
   register file would silently be measuring the alarm path instead. Every
   scenario here longer than 81 cycles drives healthy per-ring taps; the one
   that does not (`smoke`, 11 cycles, faithful to its counterpart) is shorter
   than the cutoff. This is DR-0016 behaving as ratified — worth knowing if you
   are an integrator about to tie `ring_bit` to a constant.
2. **A one-cycle skew between the behavioural top-level model and the RTL, on
   two cross-block handoffs** (`ht_startup_pass`, and `cond_word`/`cond_valid`)
   which the RTL registers and `trng_top.py`'s `TopLevel.step` passed
   combinationally. The first run of this testbench found the netlist and the
   RTL agreeing exactly and **both** differing from the model, by identical
   counts — which is what attributed it to the RTL rather than to layout — and
   `model_probe.py`, registering exactly those two signals, brought the
   difference to zero and so identified the cause. Filed as [#176][gf176] and
   fixed in #178 (which also added `sim/tb/trng-top-crosscheck/`, a
   CI-affordable RTL-only version of the same cycle-by-cycle check). All three
   descriptions now agree, and `model_probe.py` stays as the *sensitivity*
   check: delaying those handoffs again must still break the match, or this
   comparison's agreement would not be evidence that the skew is gone.

## Environment

This is the one flow in the repository that needs more than `klt` on `$PATH`:
`klt functional-verification` drives cocotb, so it needs an interpreter that
can **load** cocotb's compiled VPI module — stricter than `import cocotb`
succeeding, and not satisfied by an ABI-mismatched wheel (which imports fine
and then fails inside `vvp` with no `results.xml`). `run_demo.py --check-env`
reports exactly why a given `klt` was accepted or rejected; provision one once,
machine-locally, and point `TRNG_POST_ROUTE_KLT` at it:

```sh
python3.13 -m venv ~/.local/venvs/klt-cocotb
~/.local/venvs/klt-cocotb/bin/pip install 'cocotb==2.0.1' \
  'klayout-tools @ git+https://github.com/2AMLogic/klayout-tools@<commit>'
```

`<commit>` is the one `.github/workflows/pdk-nightly.yml` pins. Python 3.13 is
what that workflow already uses and what cocotb 2.0.1 publishes a wheel for.
`~/.local/venvs/klt-cocotb/bin/klt` is probed automatically, so on a host set
up this way no environment variable is needed at all.

Also required: `iverilog` **13.0 or newer** (SDF `INTERCONNECT` entries need
`-ginterconnect`, which does not exist before 13.0), the gf180mcu PDK (resolved
through `sim/harness/pdk.py` like everything else), and the two committed
artefacts this consumes — `layout/digital/trng_top.pnr.v` and
`layout/digital/trng_top.sdf`.

## Where the aggregated version lives

[#145][gf145]'s digital characterization document is where item 8's digital
column will cite this from; it does not exist yet, so until it does **the
evidence record under `sim/records/` is the citable source** and this README is
the prose. When #145 lands, its aggregating section should cite the record stem
rather than restating its numbers (`sim/README.md`: summary documents cite
record stems, they do not copy metadata).

[gf111]: https://github.com/2AMLogic/gf180-trng/issues/111
[gf140]: https://github.com/2AMLogic/gf180-trng/issues/140
[gf145]: https://github.com/2AMLogic/gf180-trng/issues/145
[gf171]: https://github.com/2AMLogic/gf180-trng/issues/171
[gf176]: https://github.com/2AMLogic/gf180-trng/issues/176
[klt1090]: https://github.com/2AMLogic/klayout-tools/issues/1090
[klt1102]: https://github.com/2AMLogic/klayout-tools/issues/1102
[dr9]: ../../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
