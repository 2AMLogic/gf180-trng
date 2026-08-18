---
record: 2026-08-18-trng-top-post-route-01
date: 2026-08-18T00:45:04Z
status: valid

level: gate-simulation (DR-0022, sibling of DR-0021's `level: gate`) -- a DYNAMIC simulation of the as-built post-route netlist with SDF cell delays back-annotated, compared cycle by cycle against a zero-delay RTL run of the same stimulus and against the behavioural model. Not `behavioral` (there is a netlist, a cell library and a liberty corner in the loop), not `transistor` (no device model is instantiated and ngspice is never invoked), and not `gate` (that level is static analysis and MAY be cited for timing closure; this one may not -- see Caveats)

testbench:
  path: sim/tb/trng-top-post-route/run_demo.py
  sha: cb9a85581a0bf0cfee0f0a548e5dc808ecad0d9e
  cocotb_module: sim/tb/trng-top-post-route/post_route_tb.py
  cocotb_module_sha: b7e7bb66f3bfc350b7c9d33deaf46e00e7d181e2
  stimulus: sim/tb/trng-top-post-route/scenarios.py
  stimulus_sha: e39c6e048af2fdbfcd847b15570c8491a5f0c650
netlist:
  path: layout/digital/trng_top.pnr.v
  sha: 78f83d351892603aa92c60b322e5eee6d9c67a0a
  sha256: 3129bdbbb960cc4a2045c64d9cce63c3f3df188121989fbe0735eaadf1c0c4a2
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
    - design/trng_top/trng_top.v  sha:6acd09579c5d69834bb593dffd87ede94dbf1592
    - design/conditioner/crc32_conditioner.v  sha:f46c1ebfb3aea8c9272e7bab4dab03c78563d48d
    - design/health_test/rct_apt.v  sha:4a324ebee1fd07c507e7ae080514ea850303275f
    - design/health_test/ring_liveness.v  sha:79cad3e871a261498e8318e9659c7fe83d19f95d
    - design/interface/trng_interface.v  sha:6105517e57270655b23cd96cf6f27c7d3df552d1
reference_model:
  path: design/trng_top/trng_top.py
  sha: 5c05845e77ed3e92227f54a3f807ac555c463277
  note: >-
    The behavioural model both legs are compared against every cycle:
    the same model the five `level: behavioral` records this re-runs
    were produced from.

timing_annotation:
  sdf: layout/digital/trng_top.sdf
  sdf_sha: 3e88714a269cbcfdd4e2b2e8bf60288890e5bf76
  sdf_sha256: c61b5d5e037b6439efadc2fb7929f982fa6fe78d287b425e507f756e4aa980e1
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

repo_commit: b041312b13593066c1dbb465d885abc62b00e5bf-dirty

pdk: gf180mcuD @ open_pdks c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v (timing models -- the non-FUNCTIONAL branch, the one that carries the specify blocks an SDF annotates)
  - libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/primitives.v (UDPs)
  - libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (read by layout/digital/gen_sdf.py -- the delays in the SDF above come from this deck)
  - n/a: no ngspice device model card is read by this run at all

tool:
  ngspice: "n/a (gate-level record -- ngspice is not invoked; the delays come from the standard-cell liberty deck named above)"
  iverilog: "Icarus Verilog version 13.0 (stable) (v13_0-dirty)"
  cocotb: "2.0.1"
  klt: "0.2.0" (commit a482d3934bd644b763cf925f6344ac05f54a1623, interpreter CPython 3.10.20)
  klt_binary: "/home/ubuntu/.local/bin/klt"
  openroad: "26Q3-1260-g06a5a02279" (wrote the SDF, via layout/digital/gen_sdf.py)
  python: "3.12.3 (CPython)"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

corner:
  process: ss (from the liberty deck's own operating conditions, per DR-0021's rule for a gate-level corner -- not an ngspice model card)
  voltage: 3.00 V (nominal 3.3 V, -10%; DR-0003's binding supply)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib
  interconnect: n/a -- no parasitics are extracted or annotated at all (see timing_annotation.omits), so there is no interconnect corner to name. DR-0021's `level: gate` records DO have one; this run's delays are cell-only.
  note: >-
    One corner, and it is the corner layout/digital/build.py placed and
    routed against (layout/digital/README.md's 'Corners'). A
    standard-cell library corner is a characterised .lib deck, not a
    transistor model card: this record may be cited for what the
    netlist DOES at that deck's delays, and for nothing about device
    physics. The reference leg has no corner at all (zero-delay RTL).

analysis:
  type: post-route-gate-level-equivalence
  tstop: 219974.1ns simulated in the post-route leg across 8 scenarios (4349 clock cycles at 50 ns)
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
  path: sim/records/raw/2026-08-18-trng-top-post-route-01/
  files:
    - environment.json  sha256:9adb521d1960ebb15250cd7911d687310eaf4eb42f93bb9e9cbc6eeb8b63f5f8
    - gate_comparison.json  sha256:09bf77babce3b1f93888301614ad3ef571b4259a0c8fe946ff09c06dc14a8f12
    - gate_klt_response.json  sha256:5351fe0d4b4634f6da54094cb93833f1b0288b43d3fae6f05031d202b88db3f5
    - gate_request.json  sha256:8dfb93b65586595bb1a7cd2fbc0d2a8d30786b71fbfc04a7a2df206e2586a8cc
    - gate_transcript_digest.json  sha256:87ce1eaaf51f0ab0e6e5d304a39308503404473299ee779990f07b69ba8e847d
    - rtl_comparison.json  sha256:0dcd1e6e4bd923b3619755589f942e64f9ca2ba39953a4ee2436b752f6db8ea0
    - rtl_klt_response.json  sha256:c0ce26ec561d1359e214107a347914e040189fb4abde0932375be656d170200e
    - rtl_request.json  sha256:f4771a8a6c5241109e7edfdadec35cd03f16187b0e8e32e5088549cbd87d9106
    - rtl_transcript_digest.json  sha256:ea45b6f43d930649c8e588a53042841c16666225138d763b6e83d9a195a8234d
    - verdict.json  sha256:c970eed5c5747006f439894bc22edc4738d347f5dc87c92d01d1fbeb48b5e1c9
wall_time: 0.1m
---

## Result

The verdict a post-layout re-run exists to deliver is the fourth column:
**does the as-built netlist still do what the RTL does, under the annotated
cell delays of the corner it was routed at?**

| Scenario | Behavioural counterpart | Cycles | Post-route netlist vs. RTL | Post-route netlist vs. behavioural model |
|---|---|---|---|---|
| `smoke` | sim/tb/smoke-trng-top | 11 | identical | identical, every cycle |
| `startup-and-regfile` | sim/tb/interface-regfile | 1070 | identical | identical, every cycle |
| `conditioner-blocks` | sim/tb/conditioner-crc32 | 1552 | identical | identical, every cycle |
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
| netlist matches behavioural model | yes |
| handoff skew would be detected | yes |

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
`DATA` were `0x64dcc17c`, `0xe1704bb4` on the netlist, **bit-identical to both the RTL's and
the behavioural model's** (`0x64dcc17c`, `0xe1704bb4`). That is the claim that matters for
DR-0007's conditioner: mapping, CTS buffering, cell resizing and routing did
not change a single bit of the word the RTL computes, and the CRC-32 arithmetic
the behavioural records verified is the arithmetic the placed-and-routed gates
perform.

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

**No behavioural-level conclusion was invalidated.** All three descriptions of
the digital partition — the post-route netlist under annotated delay, the RTL
it was synthesized from, and the behavioural model the five
`level: behavioral` records were produced from — agree cycle for cycle on
every one of the 5 suite scenarios, 3197 cycles, with
0 cycles differing.

- **Synthesis, CTS, resizing and routing changed nothing.** The netlist's
  complete output trace (SHA-256 over every compared port on every cycle) is
  *identical* to the RTL's. That is the item-7 verdict, and it is exact over
  all 3197 cycles rather than over a sampled subset.
- **The behavioural conclusions transfer.** The conditioner's CRC-32
  arithmetic, the DR-0002 latch/gate/flush behaviour, the register map's
  read/write semantics, the RCT stuck-source detection latency and the
  DR-0016 per-ring watchdog all reproduce bit-exactly on the as-built netlist.
  Nothing needed a correction and **no record is superseded by this one**:
  they remain valid at their own level, and this is a second, independent
  level of evidence for the same behaviour.
- **Extended, not changed.** Two detection latencies the behavioural records
  could only state in *samples of the model* are now also measured in *clock
  cycles of the netlist*, and agree (the table above).
- **This agreement is not free, and it is one commit old.** The first run of
  this testbench found the netlist and the RTL agreeing with each other and
  **both disagreeing with the behavioural model** on 270 of 3197
  cycles — because `trng_top.py`'s `TopLevel.step` passed two cross-block
  handoffs (`ht_startup_pass`, and `cond_word`/`cond_valid`) combinationally
  where `rct_apt.v` and `crc32_conditioner.v` register them, un-gating the
  conditioned path one raw sample early and so shifting the first 256-bit
  conditioner block by one bit. Identical counts in both legs is what
  attributed it to the RTL rather than to layout; a probe that registered
  exactly those two handoffs and nothing else brought the divergence to zero,
  which identified the cause. Filed as **#176** and fixed in **#178** before
  this record was written, so the numbers above are against the corrected
  model. The probe survives in `model_probe.py` as a *sensitivity* check
  (`handoff_skew_would_be_detected` above): applying it now double-delays
  those handoffs and must break the match, which is what proves this
  comparison can still see a cycle of skew on them.
- **What the netlist shows that the model cannot.** 512 of the netlist's 708
  flops (the two 8x32-bit FIFO memories) have no reset port and hold `x` out
  of reset, where the model starts every field at 0. Zero of the
  3197 compared cycles saw an `x` reach a pin — the design's own
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
  power grid is not in this simulation at all, regardless of whether it is in
  the committed layout: `gen_sdf.py` links the netlist against the liberty
  deck alone, with no DEF and no parasitic extraction in the loop (see the
  interconnect-delay caveat above), so it would carry no PDN even for a DEF
  that has one — as this DEF has, since #171.
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
