# ro-ring11-ring2-pex — ring2 schematic vs. extracted, as a native `klt pex` report

Issue [#423](https://github.com/2AMLogic/gf180-trng/issues/423). The ring1
comparison in [`../ro-ring11-pex/`](../ro-ring11-pex/README.md) does not
establish anything about ring2, which is a separately sized physical
oscillator (`xr2`, `wstv=0.240u`, versus ring1's `wstv=0.220u` in
`design/ro_array_core.spice`). This is the same comparison, paired, over
`layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds`.

**Status: unrun fixture.** The fixture is committed and freshness-checked
offline; no ring2 `klt pex` result is committed. The one attempt to submit the
27-corner grid to the batch backend (two tries, `klayout-tools==0.6.0`) was
refused by the fleet for capacity (`8 instance(s) already running + 1
requested exceeds BATCH_MAX_CONCURRENT_INSTANCES=8`, then `no capacity in any
of the 30 pools`). The grid was deliberately not run locally. No number from
ring2 appears anywhere in this repository because of this work.

| File | Role |
|---|---|
| `request.json` | the `klt sim` request: byte-for-byte ring1's apart from the testbench name (27 corners, `tran 10p 1300n`, the same three `.meas` rows); `signoff/check.py` enforces that |
| `tb_ro_ring11_ring2_pex.sp` | the circuit body; its `xdut` line carries ring2's own extraction port order |
| `ro_ring11_ring2_schematic.spice` | generated schematic DUT: `ro_ring11` at the `xr2` sizing, under ring2's extraction header, subcircuit `ro_ring11_ring2` |
| `../ro-ring11-pex/build_dut.py --ring ring2` | generates / `--check`s / `--check-source`s / `--verify-netlist`s the DUT |

Ring2's extracted port order is not ring1's (the ring output is the first
port, not the twelfth), so the testbench and DUT header are derived from ring2's
own extracted device geometry, not copied. The DUT sizing is read from the
`xr2` instance, and `build_dut.py` refuses a DUT, header, instance or restated
sizing that would make ring2 carry ring1's widths, an extraction whose
`.SUBCKT` is not `ro_ring11_ring2`, a port that drives no gate, or two ports
tied on position.

## Reproducing the run

```bash
# DR-0026's producer build, in a throwaway environment (do not install it on a shared host)
export KLT="uvx --from klayout-tools==0.6.0 --with klayout==0.30.10 klt"

python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check-source   # offline
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check          # re-extracts (klt extract only)

# 27 corners x 2 sides: a SPICE grid, so submit it to the batch backend.
# klt 0.6.0 does not read KLT_SIM_BACKEND; pass --backend explicitly.
python3 signoff/publish_item7_analog.py --ring ring2 --backend batch
python3 signoff/check.py
```

The publisher refuses to publish a stale fixture, a response from any klt but
the pin, a pin-count or flat-DUT mismatch, or an `incomplete` verdict (a
declared corner/row unmeasured) unless `--allow-incomplete` is given. It
publishes to `signoff/evidence/post-layout/ring2/` (native envelope byte for
byte, the extracted netlist, `publication.json` pinning input hashes, the
consumed-source identity, the port map, the verdict and the body-bias status).
A failing run is published as it stands. `signoff/check.py` recomputes the recorded verdict from
the envelope and request on every run and checks ring2 independently of ring1.

## What this does not claim

- **Not a manifest citation.** T1 item 7's `7.analog` stays ring1's; the
  manifest is never touched by `--ring ring2`, and `check.py` fails if it cites
  ring2 evidence. A separately reviewed change would be needed to cite it.
- **Isolation, unloaded output.** One ring on its own supply with `en` tied to it;
  `ro` carries no buffer or load, and nothing couples to ring1 or any block.
- **Deterministic.** Noiseless transient, no mismatch. The rows (period, average
  supply current, output swing) carry no limits; a row's `pass` means "measured
  on both sides". Nothing here estimates entropy, bias or jitter, and nothing is a
  full-chip timing or silicon-performance claim.
- **Bodies.** Ring2's layout has no n-well taps either: every PMOS body in the
  extraction is an anonymous floating well, and the schematic side ties PMOS bulk to
  `vddr`. Whether to draw ties is the open decision in #339/#411, not made here. Any
  result from this fixture on the current layout is a diagnosis under that
  limitation, and its envelope's `body_bias.status` is recorded in
  `publication.json`. A silicon-predictive reading depends on resolving #411 and
  rerunning against the applicable layout.
