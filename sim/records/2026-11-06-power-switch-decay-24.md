---
record: 2026-11-06-power-switch-decay-24
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
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.9.2.dev103+g9f4cec35997a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-11-06-power-switch-decay-24/
  files:
    - corner.cir  sha256:9bc5d9762e24c497036e44ce0dae9f3fe20af025375eac447b420fe1a737c77c
    - ngspice.log  sha256:c733eccc70d253e281525043288c313f6a4695e09cc09c4e2a219bb035a88859
    - report-unit.json  sha256:d44f2f5c2e795c670cacb2fbae09701511406d93857296e3026bfef165037076
wall_time: 0.996s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-4e9ae62ec34f, klt-sim-ebb0911800c8, klt-sim-26acdf91779c). The switch starts on with the rail at vdd; sleep rises at 100 ns. Times are from the start of the sleep rise, in seconds, and are the first fall through 90 %, 50 % and 5 % of vdd. A `reached_t05` of 0 means the rail never fell to 5 % of vdd within the 100000 s run, and the matching `t_decay_s_t05` is then the run length, not a crossing. `vmin_v` is the lowest rail voltage seen; `vfin_v` the rail at 99000 s. Case suffix is rail capacitance and sleep rise time.

- `t_decay_s_t90_50pf_10ns`: 1.036379e-03
- `t_decay_s_t50_50pf_10ns`: 8.049790e-03
- `t_decay_s_t05_50pf_10ns`: 2.797295e-02
- `reached_t90_50pf_10ns`: 1.000000e+00
- `reached_t50_50pf_10ns`: 1.000000e+00
- `reached_t05_50pf_10ns`: 1.000000e+00
- `vmin_v_50pf_10ns`: 5.877606e-03
- `vfin_v_50pf_10ns`: 8.690630e-03
- `t_decay_s_t90_200pf_10ns`: 4.058287e-03
- `t_decay_s_t50_200pf_10ns`: 3.106108e-02
- `t_decay_s_t05_200pf_10ns`: 1.106253e-01
- `reached_t90_200pf_10ns`: 1.000000e+00
- `reached_t50_200pf_10ns`: 1.000000e+00
- `reached_t05_200pf_10ns`: 1.000000e+00
- `vmin_v_200pf_10ns`: 7.589845e-04
- `vfin_v_200pf_10ns`: 8.690623e-03
- `t_decay_s_t90_50pf_1000ns`: 1.021595e-03
- `t_decay_s_t50_50pf_1000ns`: 8.034439e-03
- `t_decay_s_t05_50pf_1000ns`: 2.794645e-02
- `reached_t90_50pf_1000ns`: 1.000000e+00
- `reached_t50_50pf_1000ns`: 1.000000e+00
- `reached_t05_50pf_1000ns`: 1.000000e+00
- `vmin_v_50pf_1000ns`: 5.800351e-03
- `vfin_v_50pf_1000ns`: 8.690630e-03
- `t_decay_s_t90_200pf_1000ns`: 4.029379e-03
- `t_decay_s_t50_200pf_1000ns`: 3.103284e-02
- `t_decay_s_t05_200pf_1000ns`: 1.105920e-01
- `reached_t90_200pf_1000ns`: 1.000000e+00
- `reached_t50_200pf_1000ns`: 1.000000e+00
- `reached_t05_200pf_1000ns`: 1.000000e+00
- `vmin_v_200pf_1000ns`: 7.547675e-04
- `vfin_v_200pf_1000ns`: 8.690637e-03

Numbers only. No spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch_decay.py emit --check
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend batch
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend local --only ss/125/3.30   # single-point probe
python3 sim/tools/power_switch_decay.py analyze DIR/grid.report.json
```

## Caveats

- Pre-layout, schematic-level: the netlist of `design/power_switch.spice`, no extracted wiring.
- The rail is discharged only by a leakage-equivalent off NFET (710 um) and the switch's own off leakage; no bleeder, no cell switching current and no isolation or pad structure. The decay is therefore a leakage-limited bound, not a prediction of the real gated section.
- The 50/200 pF rail capacitances are the assumptions of the wake group, not extractions.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/power_switch_decay.py record`. Append-only: never edit or delete this file.
