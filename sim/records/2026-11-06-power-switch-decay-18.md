---
record: 2026-11-06-power-switch-decay-18
date: 2026-11-06T18:43:34Z
status: valid

testbench:
  path: sim/tb/power-switch/tb_power_switch_decay.sp
  sha: a13466445b3a69d4f1ab1f90ee71906b582ddcf0
netlist:
  path: design/power_switch.spice
  sha: f14b87ff4bb74a439a5eb3cd5a2f6ffe3f616d44
repo_commit: 2f15801a85b8f86f5b09a2d8f7b5dbcfe3b4d31d-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  klt: 0.9.2.dev103+g9f4cec35997a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: tran (deterministic)
  tstop: 100000
  tstep: 100 (print step; the solver steps adaptively)
  tmax: default
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-11-06-power-switch-decay-18/
  files:
    - corner.cir  sha256:0d97b2d3baa5854ced9784279e7592a431fd06478deceafe79d5c9fcf4af27f1
    - ngspice.log  sha256:c81ca534c533b296d2f250c1064f13297d2c993ed2e47686ca8220d05a29477c
    - report-unit.json  sha256:1c6f4b684f3fd4e109d242289c562736c80056f6e91a72847ea820f07a058744
wall_time: 1.117s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-4e9ae62ec34f, klt-sim-ebb0911800c8, klt-sim-26acdf91779c). The switch starts on with the rail at vdd; sleep rises at 100 ns. Times are from the start of the sleep rise, in seconds, and are the first fall through 90 %, 50 % and 5 % of vdd. A `reached_t05` of 0 means the rail never fell to 5 % of vdd within the 100000 s run, and the matching `t_decay_s_t05` is then the run length, not a crossing. `vmin_v` is the lowest rail voltage seen; `vfin_v` the rail at 99000 s. Case suffix is rail capacitance and sleep rise time.

- `t_decay_s_t90_50pf_10ns`: 1.003972e-05
- `t_decay_s_t50_50pf_10ns`: 9.258184e-05
- `t_decay_s_t05_50pf_10ns`: 4.262172e-04
- `reached_t90_50pf_10ns`: 1.000000e+00
- `reached_t50_50pf_10ns`: 1.000000e+00
- `reached_t05_50pf_10ns`: 1.000000e+00
- `vmin_v_50pf_10ns`: 1.370714e-02
- `vfin_v_50pf_10ns`: 1.454575e-02
- `t_decay_s_t90_200pf_10ns`: 3.936450e-05
- `t_decay_s_t50_200pf_10ns`: 3.651381e-04
- `t_decay_s_t05_200pf_10ns`: 1.787121e-03
- `reached_t90_200pf_10ns`: 1.000000e+00
- `reached_t50_200pf_10ns`: 1.000000e+00
- `reached_t05_200pf_10ns`: 1.000000e+00
- `vmin_v_200pf_10ns`: 2.480511e-03
- `vfin_v_200pf_10ns`: 1.454575e-02
- `t_decay_s_t90_50pf_1000ns`: 1.076879e-05
- `t_decay_s_t50_50pf_1000ns`: 9.339473e-05
- `t_decay_s_t05_50pf_1000ns`: 4.273968e-04
- `reached_t90_50pf_1000ns`: 1.000000e+00
- `reached_t50_50pf_1000ns`: 1.000000e+00
- `reached_t05_50pf_1000ns`: 1.000000e+00
- `vmin_v_50pf_1000ns`: 1.367069e-02
- `vfin_v_50pf_1000ns`: 1.454575e-02
- `t_decay_s_t90_200pf_1000ns`: 3.995898e-05
- `t_decay_s_t50_200pf_1000ns`: 3.657523e-04
- `t_decay_s_t05_200pf_1000ns`: 1.787568e-03
- `reached_t90_200pf_1000ns`: 1.000000e+00
- `reached_t50_200pf_1000ns`: 1.000000e+00
- `reached_t05_200pf_1000ns`: 1.000000e+00
- `vmin_v_200pf_1000ns`: 2.462871e-03
- `vfin_v_200pf_1000ns`: 1.454575e-02

Numbers only. No spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch_decay.py emit --check
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend batch
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend local --only ff/125/3.63   # single-point probe
python3 sim/tools/power_switch_decay.py analyze DIR/grid.report.json
```

## Caveats

- Pre-layout, schematic-level: the netlist of `design/power_switch.spice`, no extracted wiring.
- The rail is discharged only by a leakage-equivalent off NFET (710 um) and the switch's own off leakage; no bleeder, no cell switching current and no isolation or pad structure. The decay is therefore a leakage-limited bound, not a prediction of the real gated section.
- The 50/200 pF rail capacitances are the assumptions of the wake group, not extractions.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/power_switch_decay.py record`. Append-only: never edit or delete this file.
