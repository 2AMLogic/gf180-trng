---
record: 2026-10-09-ro-ring11-pex-welltied-24
date: 2026-10-09T17:08:44Z
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
  platform: "c7i.8xlarge spot instance i-0f55e707261c6ac71, job klt-sim-aabfb69c043d; submitted from Linux-7.0.0-1013-aws-x86_64-with-glibc2.39 with klt 0.6.0"

corner:
  process: ss
  voltage: 3.300 V (nominal 3.3 V, nominal)
  temperature: 125

analysis:
  type: tran
  tstop: 1300n
  tstep: 10p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-10-09-ro-ring11-pex-welltied-24/
  files:
    - ss_125c_3.30v.spice  sha256:1bf9aaad9b5d863d5ced6339f6d13036d0c48518ec204f4d07b7d1b701dea772
    - ss_125c_3.30v.log  sha256:a6e2d794a304a1b037ffb16719f4ae3c865510b8bf691be220aa92cb3c8a4228
    - ss_125c_3.30v.json  sha256:ce71c5c103f474f8c95c56f79a36dc749addce4517d4e2cf9f6491f75f810055
wall_time: 11.09s (this corner; whole 27-corner batch job 76s)
---

## Result

Well-tied extracted netlist (PMOS bodies rewired to `vddr`), this record:

- `period_s`: 2.177290e-08
- `supply_current_avg_a`: -1.054090e-05
- `ro_swing_v`: 3.26999

Same corner, not re-simulated here, from the committed envelope `signoff/evidence/post-layout/ro_ring11.pex.json` (klt pex 0.6.0, schematic DUT and extracted netlist with floating wells):

| row | schematic | extracted, wells floating | extracted, wells tied (this record) | floating vs schematic | tied vs schematic | tied vs floating |
|---|---|---|---|---|---|---|
| `period_s` | 1.030180e-08 | 1.974970e-08 | 2.177290e-08 | +91.7 % | +111.4 % | +10.2 % |
| `supply_current_avg_a` | -1.196790e-05 | -1.035350e-05 | -1.054090e-05 | -13.5 % | -11.9 % | +1.8 % |
| `ro_swing_v` | 3.42866 | 3.23917 | 3.26999 | -5.5 % | -4.6 % | +1.0 % |

Numbers only. No spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tb/ro-ring11-pex-welltied/build_welltied.py --check
uvx --from "klayout-tools==0.6.0" klt sim --backend batch -o /tmp/welltied \
    sim/tb/ro-ring11-pex-welltied/request.json --format json > /tmp/welltied/report.json
```

This record is the `ss/3.300V/125C` entry of that 27-corner request (batch job `klt-sim-aabfb69c043d`).
A single corner can be run locally by narrowing `corners` in a copy of the request.

## Caveats

- Single corner (ss / 3.30 V / 125 C). Says nothing about any other corner.
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
