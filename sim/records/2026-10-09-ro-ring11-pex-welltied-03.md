---
record: 2026-10-09-ro-ring11-pex-welltied-03
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
  - /opt/pdk/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical; fleet copy, sha256 6edba54d23b38a2c60f8ffdbaa3eb75a7568c615e4820808969bd1121b77b1aa, identical to the gf180mcuD copy this repo's harness resolves locally)

tool:
  ngspice: "ngspice-46 (AWS batch fleet runner)"
  platform: "c7i.8xlarge spot instance i-0f55e707261c6ac71, job klt-sim-aabfb69c043d; submitted from Linux-7.0.0-1013-aws-x86_64-with-glibc2.39 with klt 0.6.0"

corner:
  process: tt
  voltage: 2.970 V (nominal 3.3 V, -10%)
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
  path: sim/records/raw/2026-10-09-ro-ring11-pex-welltied-03/
  files:
    - tt_125c_2.97v.spice  sha256:639435b84286adc30fb274101eadb7b13426b329b7ed70b68da21b9dccbe719c
    - tt_125c_2.97v.log  sha256:b3847a00a9212a8d9b3beb39f0c7d462f58585fbaef4053f05d0550b9969c46a
    - tt_125c_2.97v.json  sha256:575f55b6ac4fe316960c0e5612d7c565d42dd422a53b53df3f0da7960186fb27
wall_time: 10.79s (this corner; whole 27-corner batch job 76s)
---

## Result

Well-tied extracted netlist (PMOS bodies rewired to `vddr`), this record:

- `period_s`: 2.038680e-08
- `supply_current_avg_a`: -1.053060e-05
- `ro_swing_v`: 2.9246

Same corner, not re-simulated here, from the committed envelope `signoff/evidence/post-layout/ro_ring11.pex.json` (klt pex 0.6.0, schematic DUT and extracted netlist with floating wells):

| row | schematic | extracted, wells floating | extracted, wells tied (this record) | floating vs schematic | tied vs schematic | tied vs floating |
|---|---|---|---|---|---|---|
| `period_s` | 9.625580e-09 | 1.843280e-08 | 2.038680e-08 | +91.5 % | +111.8 % | +10.6 % |
| `supply_current_avg_a` | -1.206080e-05 | -1.033300e-05 | -1.053060e-05 | -14.3 % | -12.7 % | +1.9 % |
| `ro_swing_v` | 3.06749 | 2.89625 | 2.9246 | -5.6 % | -4.7 % | +1.0 % |

Numbers only. No spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tb/ro-ring11-pex-welltied/build_welltied.py --check
uvx --from "klayout-tools==0.6.0" klt sim --backend batch -o /tmp/welltied \
    sim/tb/ro-ring11-pex-welltied/request.json --format json > /tmp/welltied/report.json
```

This record is the `tt/2.970V/125C` entry of that 27-corner request (batch job `klt-sim-aabfb69c043d`).
A single corner can be run locally by narrowing `corners` in a copy of the request.

## Caveats

- Single corner (tt / 2.97 V / 125 C). Says nothing about any other corner.
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
