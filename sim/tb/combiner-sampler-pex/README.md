# combiner-sampler-pex — the assembled combiner/sampler, schematic vs. extracted

Issue [#418](https://github.com/2AMLogic/gf180-trng/issues/418). Additional
post-layout coverage beside ring1's `sim/tb/ro-ring11-pex/` (#326). That run
deliberately excluded the buffers, the XOR combiner and the four samplers;
this one tests exactly that signal path, the one that delivers raw samples.
It is **not** a T1 citation: `signoff/block-manifest.json`'s `7.analog`
still cites ring1 alone (see "Status" below).

`klt pex` extracts `layout/blocks/combiner_sampler/combiner_sampler.gds`
(two `ro_buf` inverters, one `xor2`, four `sampler_dff` flip-flops; 104
MOSFETs) with parasitics, runs `request.json` once against the schematic DUT
and once against the extracted netlist at every corner, and reports a
per-corner, per-row delta.

| File | Role |
|---|---|
| `stimulus.py` | the schedule and the block's contract; renders `tb_combiner_sampler_pex.sp` and `request.json`, `--check`s them, `--table` prints every scenario |
| `tb_combiner_sampler_pex.sp` | generated circuit body: supply, `rn1`/`rn2`/`clk`/`rst_n` stimulus, the DUT, supply-normalised monitors; its one `.include` is what `klt pex` re-points |
| `request.json` | generated `klt sim` request: DR-0006's 27 corners, `tran 10p 370n`, 66 rows |
| `combiner_sampler_schematic.spice` | generated schematic DUT under the extraction's 14-port header |
| `build_dut.py` | renders the DUT, resolves the extraction's ports by connectivity, `--check-source`s and `--verify-netlist`s |

The publisher is `signoff/publish_combiner_sampler_pex.py`; its evidence goes
to `signoff/evidence/post-layout/combiner_sampler/`.

## Cold start

```bash
export KLT="uvx --from klayout-tools==0.6.0 --with klayout==0.30.10 klt"  # DR-0026's producer build
# (or: pip install "klayout-tools==0.6.0" "klayout==0.30.10" and leave KLT unset)
python3 sim/tb/combiner-sampler-pex/stimulus.py --check
python3 sim/tb/combiner-sampler-pex/build_dut.py --check-source      # offline
python3 sim/tb/combiner-sampler-pex/build_dut.py --check             # runs klt extract
python3 signoff/publish_combiner_sampler_pex.py --backend batch      # or --backend local
python3 signoff/check.py
python3 -m unittest sim/tests/test_combiner_sampler_pex.py           # offline
```

Prerequisites: the gf180mcuD PDK where `klt` finds it (`$PDK_ROOT`,
`~/.ciel` or `~/.volare`) and ngspice on the simulating host. klt 0.6.0 does
not read `KLT_SIM_BACKEND`, so the publisher passes `--backend` itself
(default: that variable, else `local`). `--backend batch` needs a configured
batch fleet (`KLT_BATCH_PROVISION_SCRIPT` and a job bucket; see klt's
`docs/cli/sim.md`, "Batch backend"); `--backend local` runs 54 transients
(27 corners x 2 sides) on the calling host.

## Ports

`klt pex` reuses the testbench's `xdut` line on both sides, so the schematic
DUT carries the extraction's own port list, position for position. klt 0.6.0
promotes fourteen ports named after labels inside the instanced cells:

| extracted | schematic | how it is known |
|---|---|---|
| `a`, `a$1` | `rn1`, `rn2` | buffer inputs; told apart by which XOR NMOS-stack position their buffer output gates |
| `a|d|y`, `b|d|y` | `ro1`, `ro2` | buffer outputs, which are also XOR inputs and ring-sampler D inputs |
| `d|y` | `xo` | XOR output and `raw_bit`'s D input |
| `d|vdd` | `vdd` | also `raw_valid`'s D input |
| `q`, `q$1`, `q$2`, `q$3` | `raw_bit`, `raw_valid`, `ring_bit1`, `ring_bit2` | each by its flip-flop's D input |
| `clk`, `rst_n`, `vss` | same | by connectivity; the label must agree |
| `vsubs` | `vsubs` | passed through; NMOS bulk only, unused in the schematic |

`build_dut.py` derives the right-hand column from connectivity alone: joint
colour refinement over both netlists' MOSFET/net graphs (device type, W, L;
gate vs. source/drain; bulk ignored). A port whose class holds more than one
net is refused as ambiguous; a class populated differently on the two sides
is refused as a different circuit; labels can veto a mapping but never make
one. Exposing `ro1`, `ro2` and `xo` as ports is what makes the internal
buffer and XOR nets observable on both sides.

## Schedule and rows

`python3 sim/tb/combiner-sampler-pex/stimulus.py --table` prints the full
table. Clock period 40 ns (rising edges at 20 + 40k ns). `rn1`/`rn2` change
only at falling edges; reset (`rst_n` low) from 0 to 70 ns and again from
325 ns.

| Scenario | When | Checked |
|---|---|---|
| `rst_hold_e1`, `rst_hold_e2` | after the two capture edges inside the first reset | all four flops low, although each flop's D is 1 at one of those edges |
| `startup_pre_e3` | 25 ns after reset release, before the first edge | all four low (nothing captured yet; `raw_valid` still low) |
| `pre_e3` .. `pre_e8` | 1 ns before each capture edge | `xo`, `ro1`, `ro2` at the contract's levels; the six edges cover all four (`ro1`, `ro2`) combinations |
| `cap_e3` .. `cap_e8` | 15 ns after each capture edge | `raw_bit` = sampled `xo`, `ring_bit1`/`ring_bit2` = sampled `ro1`/`ro2`, `raw_valid` = 1 from the first edge on; every data flop toggles 0→1 and 1→0 |
| `rst_async` | 5 ns after reset assertion, clock low, before any edge | all four low (asynchronous clear of `raw_bit`, `raw_valid`, `ring_bit2` from 1) |
| `rst_hold_e9` | after a capture edge under reset | all four low (reset dominates the clock) |

Each of those 62 rows is `.meas tran <row> find v(<node>n) at=<t>` on a
supply-normalised copy of the node, with `limits` `{"min": 0.9}` (expected
high) or `{"max": 0.1}` (expected low): 90 %/10 % of the corner's own supply.
The expected level comes from `stimulus.py`'s model of the contract (ring
inputs inverted by the buffers, XOR, rising-edge flip-flops with an
asynchronous, clock-dominating active-low reset), not from hand-typed
constants. Four more rows (`tcq_raw_valid_e3`, `tcq_raw_bit_e5`,
`tcq_raw_bit_e7`, `trst_raw_valid`) measure clock-to-Q and reset-to-Q 50 %
crossings and carry no limits: their `pass` means "measured on both sides".

Settling windows: inputs change 20 ns before a capture edge and 20 ns after
the previous one; combinational nodes are sampled 1 ns before the edge;
flip-flop outputs 15 ns after it, 5 ns before the next falling edge; reset
edges are at least 10 ns from any clock edge. Data or reset changing near a
clock edge (setup/hold, recovery/removal, metastability) is outside this
test.

## Verdict

`klt pex` 0.6.0 grades only the extracted side's limits; a delta row's
`status` says nothing about the schematic value (klayout-tools#2989). `signoff/check.py`'s
`combiner_sampler_verdict()` therefore holds **both** sides to each row's
limits and classifies every declared (corner, row) pair as `pass`, `fail`
(naming the failing side), `measured` (informational row, both values
present) or `unmeasured` (missing, errored, or a null value on either side —
never a pass). The run is `incomplete` if anything is unmeasured, else
`fail` if anything fails, else `pass`. The publisher records that verdict;
`check.py` recomputes it on every run, so it cannot be edited by hand. A
`fail` is published as it stands; an `incomplete` run is refused unless
`--allow-incomplete` is given.

## What this does not cover

- **The rings.** `rn1`/`rn2` are logic steps at `vdd` level, not
  oscillators; ring layout, ring supplies and the ring-to-buffer
  inter-region nets are outside this layout.
- **Randomness.** Deterministic stimulus; nothing here estimates entropy,
  bias or jitter.
- **Boundary timing.** See "Settling windows" above.
- **Bodies.** The layout draws no n-well taps: every PMOS body in the
  extraction is an anonymous floating well (`body_bias.status` is expected
  to read `"unbiased"`), while the schematic ties PMOS bulk to `vdd` and
  NMOS bulk to `vss`. `klt`'s own documentation calls a re-simulation of
  such a netlist physically wrong, not merely imprecise; #339 measured the
  error at 10–18 % on ring1's period. The extracted-side numbers are a
  diagnosis under that limitation (#411, #412), not a prediction of
  silicon.
- **Loads, noise, mismatch, full chip.** Outputs unloaded; no device noise
  or mismatch; block-level extraction only, no top-level routing or supply
  network.
- **The PDK switch file.** `design.ngspice`'s `.param` values are restated
  in the testbench body: `klt pex` allows one `.include`, and it is the one
  it swaps (klayout-tools#2871).

## Status

See `signoff/README.md`, "Combiner/sampler post-layout coverage", for the
latest run and its result.
