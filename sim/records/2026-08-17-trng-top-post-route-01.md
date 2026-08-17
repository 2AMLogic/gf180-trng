---
record: 2026-08-17-trng-top-post-route-01
date: 2026-08-17T16:22:23Z
status: valid

level: post-route-gate (see sim/README.md's 'Post-route gate-level records') -- a gate-level simulation of the as-built post-route netlist with SDF cell delays back-annotated, checked against a zero-delay RTL run of the same stimulus and against the behavioural model. Not `behavioral` (there is a netlist, a cell library and a liberty corner in the loop) and not `transistor` (no device model is instantiated and ngspice is never invoked)

testbench:
  path: sim/tb/trng-top-post-route/run_demo.py
  sha: 7f259fb648fb9c6b2c22dc4ec4f565941f63f85d
  cocotb_module: sim/tb/trng-top-post-route/post_route_tb.py
  cocotb_module_sha: b7e7bb66f3bfc350b7c9d33deaf46e00e7d181e2
  stimulus: sim/tb/trng-top-post-route/scenarios.py
  stimulus_sha: 8fd448ae7025d95f77acba384e75c2e9e97b23b6
netlist:
  path: layout/digital/trng_top.pnr.v
  sha: ecdfebe92bb2f5d01c5fb542c177ae7a66e251b8
  sha256: dccb39943528907ef8538f5ed54fd4981e1bc4871da4366659f6f269b7ef66e8
  kind: >-
    Post-route gate-level netlist -- klt place-and-route's own
    write_verilog after clock-tree synthesis and cell resizing (#111,
    PR #172), so the CTS buffers and the resized drive strengths are
    in this simulation. NOT design/trng_top/trng_top.synth.v, which is
    the pre-CTS mapped netlist.
reference_leg:
  what: >-
    The same stimulus, the same testbench and the same comparison, run
    against the RTL the netlist was synthesized from, zero-delay, no
    SDF. Present so every difference can be attributed: a divergence
    from the behavioural model that shows up in BOTH legs was already
    in the RTL; one that shows up only in the netlist was introduced
    by synthesis, CTS, resizing or routing.
  sources:
    - design/trng_top/trng_top.v  sha:80dfc85d0d2a898eecaf56dcf1aa512d20d5beb4
    - design/conditioner/crc32_conditioner.v  sha:f46c1ebfb3aea8c9272e7bab4dab03c78563d48d
    - design/health_test/rct_apt.v  sha:4a324ebee1fd07c507e7ae080514ea850303275f
    - design/health_test/ring_liveness.v  sha:79cad3e871a261498e8318e9659c7fe83d19f95d
    - design/interface/trng_interface.v  sha:6105517e57270655b23cd96cf6f27c7d3df552d1
reference_model:
  path: design/trng_top/trng_top.py
  sha: 6c9f2965aeef135c8a35165d51d03c36db4c370d
  note: >-
    The behavioural model both legs are compared against every cycle:
    the same model the five `level: behavioral` records this re-runs
    were produced from.

timing_annotation:
  sdf: layout/digital/trng_top.sdf
  sdf_sha: dd60f39cdc9230b1d1302845c003623d2c7a3f7d
  sdf_sha256: ae77633baa9dc59afa7da3e1fa5f78de83f8c13b034888b36e3417a48c500a88
  generated_by: layout/digital/gen_sdf.py (engine: opensta 26Q3-1260-g06a5a02279)
  applied_by: Icarus $sdf_annotate, via klt functional-verification's options.sdf (generated klt_sdf_annotate elaboration root, -gspecify -ginterconnect -T typ)
  corner_selected: typ
  klt_reports_annotated: true
  models: >-
    modeled (per-instance IOPATH from the resolved liberty timing arcs, at the as-built netlist's real fan-out)
  omits: >-
    interconnect delay: not modeled -- zero-length/zero-RC net assumption; no DEF, no placement, no parasitic extraction (see this script's own module docstring);
    setup/hold/width checking: NONE ran. Icarus 13.0 implements no SDF
    TIMINGCHECK annotation (708
    'TIMINGCHECK not supported' lines, one per flop) AND no
    $setup/$hold/$width at all
    (1926 'Timing checks are
    not supported' lines while elaborating the cell library), so this
    run cannot detect a timing violation of any kind -- it models cell
    delay and nothing else;
    IOPATH arcs Icarus cannot elaborate: 1332 dropped (46 cells lost every arc);
    no parasitic coupling, no IR drop, no on-chip variation, single
    corner. Enumerated in full under Caveats.

repo_commit: e413a4d0c7003e269af26f80bf668a542f2d4834-dirty

pdk: gf180mcuD @ open_pdks c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v (timing models -- the non-FUNCTIONAL branch, the one that carries the specify blocks an SDF annotates)
  - libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/primitives.v (UDPs)
  - libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (read by layout/digital/gen_sdf.py -- the delays in the SDF above come from this deck)
  - n/a: no ngspice device model card is read by this run at all

tool:
  ngspice: "n/a (gate-level record -- ngspice is not invoked; the delays come from the standard-cell liberty deck named above)"
  iverilog: "Icarus Verilog version 13.0 (stable) (v13_0)"
  cocotb: "2.0.1"
  klt: "0.2.0" (commit a482d3934bd644b763cf925f6344ac05f54a1623, interpreter CPython 3.13.15)
  klt_binary: "/Users/rwalters/.local/venvs/klt-cocotb/bin/klt"
  openroad: "26Q3-1260-g06a5a02279" (wrote the SDF, via layout/digital/gen_sdf.py)
  python: "3.14.7 (CPython)"
  platform: macOS-26.6.1-arm64-arm-64bit-Mach-O

corner:
  process: ss (from the liberty deck gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib, not an ngspice model card)
  voltage: 3.00 V (nominal 3.3 V, -10%; DR-0003's binding supply)
  temperature: 125
  note: >-
    One corner, and it is the corner layout/digital/build.py placed and
    routed against (layout/digital/README.md's 'Corners'). A
    standard-cell library corner is a characterised .lib deck, not a
    transistor model card: this record may be cited for what the
    netlist DOES at that deck's delays, and for nothing about device
    physics. The reference leg has no corner at all (zero-delay RTL).

analysis:
  type: post-route-gate-level-equivalence
  tstop: 219824.1ns simulated in the post-route leg across 8 scenarios (4346 clock cycles at 50 ns)
  tstep: n/a (event-driven digital simulation)
  tmax: n/a (event-driven)
  noise_params: n/a (no device noise in a gate-level run)
  runs: 1 per leg (2 legs: rtl reference, gate post-route)
  drive_offset_ns: 5 (stimulus applied this long after each clock edge, clear of the flops' hold windows)
  sample_offset_ns: 40 (outputs compared this long after the stimulus changes, except where a scenario states otherwise)
  compared_ports: reg_rdata, str_data, str_valid, ht_alarm

seeds:
  cocotb_random_seed: 1 (pinned; no scenario draws from cocotb's own generator)
  stimulus:
    smoke: n/a (the ten raw bits are read verbatim out of sim/records/2026-08-01-sampler-array-digitize-03.md; that record carries its own ngspice seeds)
    startup-and-regfile: raw: biased_bits('interface-regfile-startup', 1); rings: healthy_ring_bits('interface-regfile-startup-ring{0,1}', 51/52)
    conditioner-blocks: raw: biased_bits('conditioner-crc32-h050', 1); rings: healthy_ring_bits('conditioner-crc32-h050-ring{0,1}', 61/62)
    rct-stuck-output: lead-in: biased_bits('stuck-output-lead-in', 20); fault: constant_bits(1) (unseeded by construction); rings: healthy_ring_bits('stuck-output-ring{0,1}', 71/72)
    ring1-stuck: rings: healthy_ring_bits('ring{0,1}', 41/42) then stuck_ring_bits(frozen) + healthy_ring_bits('ring1-stuck-other', 141); raw: biased_bits('ring1-stuck-raw', 41)
    reg-read-walk: raw: biased_bits('reg-read-walk', 7); rings: healthy_ring_bits('reg-read-walk-ring{0,1}', 81/82)
    reg-read-walk-early-sample: same as reg-read-walk
    reg-read-walk-settle-sweep: same as reg-read-walk

raw:
  path: sim/records/raw/2026-08-17-trng-top-post-route-01/
  files:
    - environment.json  sha256:aa11ac73577ce80d3ba56def4e8724614200b27632f58125be691c27433176e6
    - gate_comparison.json  sha256:45045a9e6f65f3adc5983f047ad1af83c669cee4dbb924e31d16f0d177a8318d
    - gate_klt_response.json  sha256:2bf53c852e4296d8d40e54b863dcef4cea9f91241b4be3f17d1c5f22a89f7ce2
    - gate_request.json  sha256:71d39ed363d44583352348c5eb5c001b20e72a4b7df05232b3267f44bc97d667
    - gate_transcript_digest.json  sha256:9a695a9e3e4b6d414f54f70ad0d7f795eceba0583fd483c80bd0d2c6fea640f1
    - rtl_comparison.json  sha256:24fcf9d4973ce05dd88d3d0faa659156dffd9d53a912cd00abeab2c038aedb4b
    - rtl_klt_response.json  sha256:0dd75126e3d221231ce9affb001a8360bdc5d616b9a398936b695c01559293e3
    - rtl_request.json  sha256:92a39be2271a873e3fb4b321828ef66c31e78c09fcbe0d77d020db7b60aea3be
    - rtl_transcript_digest.json  sha256:fb0c4c3cb61d26bc7058b696b36209f5d5a1b86530994aa2feefead7dd7e1c3d
    - verdict.json  sha256:159f71df647555509cc148a0258b53601f9ff4aae6a4810810f18208d39336ae
wall_time: 0.7m
---

## Result

The verdict a post-layout re-run exists to deliver is the fourth column:
**does the as-built netlist still do what the RTL does, under the annotated
cell delays of the corner it was routed at?**

| Scenario | Behavioural counterpart | Cycles | Post-route netlist vs. RTL | Post-route netlist vs. behavioural model |
|---|---|---|---|---|
| `smoke` | sim/tb/smoke-trng-top | 11 | identical | identical, every cycle |
| `startup-and-regfile` | sim/tb/interface-regfile | 1067 | identical | differs on 1 cycle (RTL leg: 1) |
| `conditioner-blocks` | sim/tb/conditioner-crc32 | 1552 | identical | differs on 269 cycles (RTL leg: 269) |
| `rct-stuck-output` | sim/tb/health-test-fault-injection | 322 | identical | identical, every cycle |
| `ring1-stuck` | sim/tb/ring-liveness-fault-injection | 242 | identical | identical, every cycle |
| `reg-read-walk` | n/a (post-route-level only) | 96 | identical | identical, every cycle |
| `reg-read-walk-early-sample` | n/a (post-route-level only -- negative control) | 96 | **DIFFERS** | differs on 26 cycles (required — see the control below) |
| `reg-read-walk-settle-sweep` | n/a (post-route-level only) | 10 x 96 | settles by 8 ns, not by 4 ns | — |

Every one of the checks this run derives from its own artefacts:

| Check | Holds |
|---|---|
| every scenario ran | yes |
| pnr preserved behaviour | yes |
| identical stimulus both legs | yes |
| no x reached a pin | yes |
| sdf annotation applied | yes |
| annotation control fired | yes |
| model divergence is pre existing | yes |
| registered handoffs explain every divergence | yes |

`klt functional-verification` reported `status: pass` for the
post-route leg (8 passed,
0 failed, 0
skipped) and `status: pass` for the RTL
reference leg.

Two latencies were measured on the netlist rather than inherited from the
model:

| Quantity | Post-route netlist | Behavioural model |
|---|---|---|
| `ht_alarm` rise after a stuck raw source (onset cycle 200, C_RCT = 81) | cycle 282 | cycle 282 |
| `ht_alarm` rise after ring 1 freezes (onset cycle 120, C_LIVE = 81) | cycle 201 | cycle 201 |

The conditioned words the `conditioner-blocks` scenario read back through
`DATA` were `0x64dcc17c`, `0xe1704bb4` on the netlist — **bit-identical to the RTL's**, which
is the claim that matters for DR-0007's conditioner: mapping, CTS buffering,
cell resizing and routing did not change a single bit of the word the RTL
computes. They are *not* the behavioural model's words (`0x38638752`, `0x19919129`), for
the documented reason in the next section and not because the CRC-32
arithmetic differs: the model un-gates the conditioned path one raw sample
earlier than the hardware, so its first 256-bit block starts one bit earlier
and every word after it is a different (correct-for-that-input) CRC.

### The annotation is in the loop (control)

A gate-level run whose SDF silently failed to apply looks exactly like a green
zero-delay run, so this record does not take the annotation on trust — twice
over. `klt` scans both Icarus transcripts itself before reporting
`environment.sdf.annotated: true`.
Independently of that, `reg-read-walk-early-sample` re-runs the identical
stimulus sampled 0.1 ns after the inputs change
instead of 40 ns:

- on the **post-route netlist** it differs from the settled trace, and from
  the model on 26 of 96
  cycles — annotated cell delay means the outputs cannot possibly be settled
  0.1 ns after their inputs move;
- on the **zero-delay RTL** the same control differs on
  0 cycles, because there is no delay to
  wait for.

The same control returning opposite answers on the two legs is what rules out
"the comparison is just noisy". The settle sweep puts a number on it — the
same stimulus compared at a ladder of sampling offsets on the netlist:

| Sampling offset (ns after the stimulus changes) | Cycles differing | Cycles with `x`/`z` |
|---|---|---|
| 0.1 | 26 | 0 |
| 0.5 | 26 | 0 |
| 1 | 26 | 0 |
| 2 | 18 | 0 |
| 4 | 18 | 0 |
| 8 | 0 | 0 |
| 16 | 0 | 0 |
| 24 | 0 | 0 |
| 32 | 0 | 0 |
| 44 | 0 | 0 |

So the register-read path is fully settled by
**8.0 ns** and is not settled at
4.0 ns, under cell delays alone. That is a
**lower bound** on this netlist's combinational delay on that path, not an
Fmax claim: interconnect delay is not modelled at all (see Caveats), so the
real path is slower than this by whatever its routing contributes.

## Pre/post comparison: did any behavioural conclusion change?

**No behavioural-level conclusion was invalidated. A divergence between the
behavioural top-level model and the implementation was found, it is not a P&R
defect, and it was already there in the RTL.**

- **Synthesis, CTS, resizing and routing changed nothing.** For all
  5 suite scenarios the post-route netlist's complete output trace
  (SHA-256 over every compared port on every cycle) is *identical* to the
  RTL's. That is the item-7 verdict, and it is exact over all
  3194 cycles rather than over a sampled subset.
- **The behavioural model and the implementation diverge on
  270 of 3194 cycles**, and by identical counts in
  both legs — so the divergence is a property of the RTL, present before any
  layout step ran.
- **Root cause, measured rather than argued.** `trng_top.py`'s `TopLevel.step`
  passes two cross-block signals combinationally within one cycle that the
  RTL registers:

  1. `ht_startup_pass`. `TopLevel.step` hands the interface *last* cycle's
     `ht_fail_rct` / `ht_fail_apt` / `ring_stuck_any` (its `_last_*` fields,
     matching `rct_apt.v`'s and `ring_liveness.v`'s `output reg` ports) but
     *this* cycle's `ht_startup_pass` — even though `rct_apt.v` registers that
     signal exactly like the other three.
  2. `cond_word` / `cond_valid`. `crc32_conditioner.v` declares both `output
     reg`, so the interface sees a conditioned word the cycle *after* the
     sample that completed the block; `TopLevel.step` hands it over in the
     same cycle.

  Re-running the identical comparison against a model with exactly those two
  handoffs registered (`post_route_tb.py`'s `_registered_handoff_model`, which
  *wraps* the block models rather than reimplementing the step function)
  leaves **zero** diverging cycles, in both legs — the
  `registered_handoffs_explain_every_divergence` check above. Skew (1) is what
  makes the difference large rather than cosmetic: un-gating the conditioned
  path one raw sample early shifts the first 256-bit block by one bit and so
  changes the conditioned word itself, which then differs for every cycle it
  is presented on.
- **Which conclusions this does and does not touch.** The five behavioural
  records' own claims are about their *blocks* — the conditioner's CRC-32
  arithmetic over a given 256-bit block, the RCT/APT cutoffs and latencies,
  the register map's semantics, the per-ring watchdog — and every one of them
  reproduces on the netlist. What the two skews affect is only the top-level
  model's *assembly* timing, which no existing test covers:
  `sim/tests/test_trng_top.py` checks that `trng_top.v` elaborates and that
  the pin names line up, and `sim/tb/conditioner-crc32/tb_rtl_equivalence.v`
  compares the *sequence* of conditioned words rather than the cycle each
  appears on — so neither can see a one-cycle handoff skew. That is why this
  went unnoticed until a top-level cycle-by-cycle simulation existed.
  **No record is superseded by this one**, and the fix belongs in
  `design/trng_top/trng_top.py` (or in its docstring's claim of RTL
  equivalence) — filed as **#176** rather than smuggled into a verification
  change, because silently editing the model this run verifies against would
  have destroyed the finding.
- **What the netlist shows that the model cannot.** 512 of the netlist's 708
  flops (the two 8x32-bit FIFO memories) have no reset port and hold `x` out
  of reset, where the model starts every field at 0. Zero of the
  3194 compared cycles saw an `x` reach a pin — the design's own
  `cond_avail ? cond_mem[head] : 32'd0` gating doing its job, which is a
  property the behavioural model *cannot* check because it has no
  uninitialised state to gate.

### What the per-block behavioural suite could not see

Four of the five suite members drive one sub-block each. The post-route
netlist is a single flattened `module trng_top` with no sub-block hierarchy
left to bind to, so every scenario here goes through the top-level ports — and
that surfaced a cross-block interaction none of the four per-block testbenches
can: `trng_top` has DR-0016 per-ring liveness inputs (`ring_bit[1:0]`) that
the conditioner's, the health test's and the interface's own testbenches have
no equivalent of. Leaving them idle is not "no stimulus", it is *two dead
rings*: the watchdog fires at C_LIVE = 81 cycles, latches
`ht_alarm` and gates the conditioned path. Every scenario here longer than
that drives healthy per-ring taps, and the one that does not (`smoke`, 11
cycles, faithful to its counterpart) is shorter than the cutoff. This is
DR-0016 behaving exactly as ratified, not a defect — it is recorded because an
integrator who ties `ring_bit` to a constant will see an alarm
81 cycles after reset and has no other document to find that
in.

## How to reproduce

```sh
python3 sim/tb/trng-top-post-route/run_demo.py --check-env    # what this flow needs, and whether it is here
python3 sim/tb/trng-top-post-route/run_demo.py --no-write     # run both legs, print, mint nothing
python3 sim/tb/trng-top-post-route/run_demo.py                # run both legs and mint a new record
```

`--check-env` first is not ceremony: this flow needs a `klt` whose interpreter
can *load* cocotb's compiled VPI module, which is stricter than "cocotb
imports" — see `run_demo.py`'s docstring, and `--check-env`'s own output for
the exact reason a given `klt` was rejected. On a host where the `klt` on
`$PATH` cannot, point `TRNG_POST_ROUTE_KLT` at one that can. That the
underlying failure surfaces from `klt` as a generic "the regression did not
run to completion" is filed generically upstream as
[klayout-tools#1103](https://github.com/2AMLogic/klayout-tools/issues/1103).

The run is deterministic: every bit of stimulus comes from `scenarios.py`'s
SHA-256 counter-mode generators at the fixed seeds in the frontmatter,
cocotb's own seed is pinned, and the netlist and SDF are committed artefacts
whose hashes are in the frontmatter. Records are append-only: a re-run mints a
new stem, it never overwrites this one.

## Caveats

These are the annotation's coverage limits, enumerated. Each is something this
run did **not** model, and therefore a claim this record cannot support:

- **No interconnect (wire) delay, at all.** `layout/digital/gen_sdf.py` links
  the netlist against the liberty deck with no DEF, no placement and no
  parasitic extraction, so every net is a zero-length, zero-RC lump and every
  `INTERCONNECT` entry would have been zero — which is why the design-scope
  block that would carry them is not in the committed SDF at all. That script
  also explains why the obvious better answer is *worse* here: the only route
  to real routed parasitics extracts them from the DEF→GDS merge, and that
  merge is geometrically wrong by a factor of two
  ([klayout-tools#1090](https://github.com/2AMLogic/klayout-tools/issues/1090)),
  so it would produce interconnect delays wrong by a data-dependent factor
  rather than absent ones. Consequence: every delay here is optimistic by
  whatever the routing contributes, and the settle bound above is a floor, not
  an estimate.
- **No setup/hold/width checking of any kind — not weaker checking, none.**
  Icarus Verilog 13.0 drops it twice over, and both counts come from this
  run's own transcripts (`gate_transcript_digest.json`):
  **708** `TIMINGCHECK not supported`
  lines (one per flop — the SDF's characterised setup/hold limits are parsed
  and discarded) and
  **1926** `Timing checks are not
  supported` lines while elaborating the cell library (Icarus implements no
  `$setup`/`$hold`/`$width` at all, so the models' own placeholder checks do
  not run either). The `notifier` regs those checks would drive therefore
  never fire, and **a timing violation this run did not report is not evidence
  of anything**: the run models cell delay and propagates it, and that is the
  whole of its timing content. Setup/hold signoff stays with OpenROAD's own
  STA (`layout/digital/reports/place_and_route.json`) and #145. That `klt`'s
  response reports `annotated: true` without distinguishing a fully-annotated
  run from one where every `TIMINGCHECK` was dropped is filed generically
  upstream as
  [klayout-tools#1102](https://github.com/2AMLogic/klayout-tools/issues/1102).
- **1332 IOPATH arcs
  are unannotated.** Icarus refused
  120 `specify` paths in the cell
  *library* (`sorry: ifnone with an edge-sensitive path`, once per library cell
  definition, in this run's own elaboration transcript); across this netlist's
  instances of those cells that accounts for the
  1332 SDF entries
  `gen_sdf.py` therefore drops — the refused shape is an `ifnone`-qualified
  edge-sensitive path, which is what `xor`/`xnor`/`mux`/`addf`/`addh` use for
  their select/toggle inputs, and `gen_sdf.py`'s docstring derives the exact
  `(cell, from, to)` list mechanically from the library's own Verilog. For
  46
  instances every arc they had was in that set, so those instances simulate
  entirely at their *library default* delay rather than at this corner's.
- **One corner, one voltage, one temperature.**
  `ss_125C_3v00` only. Nothing here says anything about any
  other corner, and the SDF's `min:typ:max` triplets are all identical (one
  deck), so `-T min` and `-T max` would simulate the same numbers as the
  `typ` this run used.
- **No parasitic coupling, no IR drop, no on-chip variation, no SSTA.** The
  power grid is not in this simulation — and per #171 it is not in the
  committed layout yet either.
- **Stimulus is a bounded slice, not the behavioural scenario.** Each scenario
  runs the shortest prefix that exercises the mechanism it is named for; the
  Result table's scenario definitions record the behavioural length each was
  cut down from. This record therefore carries **no statistical claim**: the
  monobit balances, the observed false-positive rates and the SP 800-90B
  arithmetic stay with the behavioural records, which run 8192–131072 samples
  for exactly that reason. What transfers to the netlist is functional
  equivalence on the stimulus actually run, and only that.
- **A narrower observation surface than the behavioural suite has.** Those
  testbenches read a block's internal counters directly; this one sees only
  `trng_top`'s pins. A divergence in internal state that never reaches a pin
  on this stimulus would not be detected here.
- **Not a power, area or Fmax record.** Those are #145's deliverable.
- **The behavioural records keep their level.** Nothing here re-labels them:
  they are `level: behavioral` and remain citable exactly as far as DR-0009
  rule 3 allows. This record adds a level; it does not reclassify one.

---

Written by `sim/tb/trng-top-post-route/run_demo.py`. Append-only: never edit or delete this
file — a re-run or correction mints a new record and points back here via
`supersedes` (see `sim/README.md`).
