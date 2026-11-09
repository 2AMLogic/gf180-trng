---
record: 2026-11-06-power-switch-decay-28
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
  - libs.tech/ngspice/sm141064.ngspice (sections: fs bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.9.2.dev103+g9f4cec35997a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: fs
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: -40

analysis:
  type: tran (deterministic)
  tstop: 100000
  tstep: 100 (print step; the solver steps adaptively)
  tmax: default
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-11-06-power-switch-decay-28/
  files:
    - corner.cir  sha256:31ae454dbf363c4b285ac2c03e0d630dc0f4b02901b80a8fc2fbc8814ec24fee
    - ngspice.log  sha256:93f50dfa23cf6fb1ab2c5a58d77c260e0cb72d20268dac0d585405189536fd70
    - report-unit.json  sha256:0a8a0664f53f257e324646326e940b8bbdad57ad69cbd27f68480708a9d3c790
wall_time: 0.968s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-4e9ae62ec34f, klt-sim-ebb0911800c8, klt-sim-26acdf91779c). The switch starts on with the rail at vdd; sleep rises at 100 ns. Times are from the start of the sleep rise, in seconds, and are the first fall through 90 %, 50 % and 5 % of vdd. A `reached_t05` of 0 means the rail never fell to 5 % of vdd within the 100000 s run, and the matching `t_decay_s_t05` is then the run length, not a crossing. `vmin_v` is the lowest rail voltage seen; `vfin_v` the rail at 99000 s. Case suffix is rail capacitance and sleep rise time.

- `t_decay_s_t90_50pf_10ns`: 7.582871e-02
- `t_decay_s_t50_50pf_10ns`: 6.926040e-01
- `t_decay_s_t05_50pf_10ns`: 1.000000e+05
- `reached_t90_50pf_10ns`: 1.000000e+00
- `reached_t50_50pf_10ns`: 1.000000e+00
- `reached_t05_50pf_10ns`: 0.000000e+00
- `vmin_v_50pf_10ns`: 1.048216e+00
- `vfin_v_50pf_10ns`: 1.054309e+00
- `t_decay_s_t90_200pf_10ns`: 2.953432e-01
- `t_decay_s_t50_200pf_10ns`: 2.703643e+00
- `t_decay_s_t05_200pf_10ns`: 1.000000e+05
- `reached_t90_200pf_10ns`: 1.000000e+00
- `reached_t50_200pf_10ns`: 1.000000e+00
- `reached_t05_200pf_10ns`: 0.000000e+00
- `vmin_v_200pf_10ns`: 1.053960e+00
- `vfin_v_200pf_10ns`: 1.054184e+00
- `t_decay_s_t90_50pf_1000ns`: 7.431496e-02
- `t_decay_s_t50_50pf_1000ns`: 6.911460e-01
- `t_decay_s_t05_50pf_1000ns`: 1.000000e+05
- `reached_t90_50pf_1000ns`: 1.000000e+00
- `reached_t50_50pf_1000ns`: 1.000000e+00
- `reached_t05_50pf_1000ns`: 0.000000e+00
- `vmin_v_50pf_1000ns`: 1.048240e+00
- `vfin_v_50pf_1000ns`: 1.054309e+00
- `t_decay_s_t90_200pf_1000ns`: 2.932181e-01
- `t_decay_s_t50_200pf_1000ns`: 2.702359e+00
- `t_decay_s_t05_200pf_1000ns`: 1.000000e+05
- `reached_t90_200pf_1000ns`: 1.000000e+00
- `reached_t50_200pf_1000ns`: 1.000000e+00
- `reached_t05_200pf_1000ns`: 0.000000e+00
- `vmin_v_200pf_1000ns`: 1.053960e+00
- `vfin_v_200pf_1000ns`: 1.054184e+00

Numbers only. No spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch_decay.py emit --check
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend batch
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend local --only fs/-40/2.97   # single-point probe
python3 sim/tools/power_switch_decay.py analyze DIR/grid.report.json
```

## Caveats

- Pre-layout, schematic-level: the netlist of `design/power_switch.spice`, no extracted wiring.
- The rail is discharged only by a leakage-equivalent off NFET (710 um) and the switch's own off leakage; no bleeder, no cell switching current and no isolation or pad structure. The decay is therefore a leakage-limited bound, not a prediction of the real gated section.
- The 50/200 pF rail capacitances are the assumptions of the wake group, not extractions.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/power_switch_decay.py record`. Append-only: never edit or delete this file.
