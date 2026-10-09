---
record: 2026-10-09-ro-ring11-pex-welltied-26
date: 2026-10-09T17:16:00Z
status: valid
level: extracted

testbench:
  path: sim/tb/ro-ring11-pex-welltied/tb_ro_ring11_pex_welltied.sp
  sha: cd1f6109062248c9f28c1425fa4708d4a4564f5b
netlist:
  path: sim/tb/ro-ring11-pex-welltied/ro_ring11.welltied.extracted.spice
  sha: bc0153bc5287fac14e06284990ee7d67318e6790
repo_commit: 84a135fb326b6000dbd0c7c452af5889bbafad61-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /opt/pdk/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss; fleet copy, sha256 6edba54d23b38a2c60f8ffdbaa3eb75a7568c615e4820808969bd1121b77b1aa, identical to the gf180mcuD copy this repo's harness resolves locally)

tool:
  ngspice: "ngspice-46 (AWS batch fleet runner)"
  platform: "c7i.8xlarge spot instance, job klt-sim-aabfb69c043d; submitted from Linux-7.0.0-1013-aws-x86_64-with-glibc2.39 with klt 0.6.0"

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 27

analysis:
  type: tran
  tstop: 1300n
  tstep: 10p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-10-09-ro-ring11-pex-welltied-26/
  files:
    - ss_27c_3.63v.spice  sha256:fba1128d5878a28cc92be86f08db44980e23ce91c06eb782d51efcaea5970599
    - ss_27c_3.63v.log  sha256:99f11aba7dc0f6052b515394c61b76d7595f646a9d68f7601fe533fc2e99b766
    - ss_27c_3.63v.json  sha256:7e9089cf18ed224e4b6b41cfd02d648e5f4bb0b0415a3f22a659fec200975b7d
wall_time: 9.332s (this corner; whole 27-corner batch job 76s)
---

## Result

Well-tied extracted netlist (PMOS bodies rewired to `vddr`), this record:

- `period_s`: 1.477660e-08
- `supply_current_avg_a`: -1.648500e-05
- `ro_swing_v`: 3.59987

Same corner, not re-simulated here, from the committed envelope `signoff/evidence/post-layout/ro_ring11.pex.json` (klt pex 0.6.0, schematic DUT and extracted netlist with floating wells):

| row | schematic | extracted, wells floating | extracted, wells tied (this record) | floating vs schematic | tied vs schematic | tied vs floating |
|---|---|---|---|---|---|---|
| `period_s` | 6.960670e-09 | 1.308030e-08 | 1.477660e-08 | +87.9 % | +112.3 % | +13.0 % |
| `supply_current_avg_a` | -1.870100e-05 | -1.688050e-05 | -1.648500e-05 | -9.7 % | -11.8 % | -2.3 % |
| `ro_swing_v` | 3.78601 | 3.57 | 3.59987 | -5.7 % | -4.9 % | +0.8 % |

Numbers only. No spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tb/ro-ring11-pex-welltied/build_welltied.py --check
uvx --from "klayout-tools==0.6.0" klt sim --backend batch -o /tmp/welltied \
    sim/tb/ro-ring11-pex-welltied/request.json --format json > /tmp/welltied/report.json
```

This record is the `ss/3.630V/27C` entry of that 27-corner request (batch job `klt-sim-aabfb69c043d`).
A single corner can be run locally by narrowing `corners` in a copy of the request.

## Caveats

- Single corner (ss / 3.63 V / 27 C). Says nothing about any other corner.
- The netlist is the extraction of `layout/rings/ro_ring11/ro_ring11.gds` (`signoff/evidence/post-layout/ro_ring11.extracted.spice`) with the body (4th terminal) of all 23 PMOS rewired from their 11 anonymous floating well nets to the `vddr` port node, by `build_welltied.py`, derived from the envelope's `body_bias` block. It is a counterfactual, NOT a drawn-layout result: the layout draws no n-well tie (layout/README.md), so no drawn cell has this connection. The tie is ideal (no access resistance), the best case for a tie.
- The schematic side of the comparison ties PMOS bulk to `vddr`; the floating side is the committed envelope.
- Ring1 only. Ring2, the buffers, the XOR combiner, the samplers and every inter-region net are not included.
- Parasitics captured are what `klt extract --parasitics` models for ring1 alone: device-level parasitics and the hand-routed inter-stage chain and rail straps; quasi-static lumped RC, no lateral coupling except named critical nets, no inter-region routing. See sim/characterization-post-layout-extracted.md section 7 and signoff/README.md.
- Noiseless, deterministic transient; no device mismatch; `ro` unloaded. Absolute periods differ from array-level records.
- Simulated on the batch fleet runner (ngspice-46); the figures also agree with a local single-corner probe at tt / 3.30 V / 27 C (13.65 ns). The floating/schematic figures come from the committed envelope's own run, not this job.
- The deck is self-contained: the batch backend of klt 0.6.0 uploads the testbench alone, so the netlist text is inlined into `tb_ro_ring11_pex_welltied.sp` (the separate netlist file is what `netlist.path` cites; `build_welltied.py --check` ties them).

---

Written by `sim/tb/ro-ring11-pex-welltied/write_records.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
