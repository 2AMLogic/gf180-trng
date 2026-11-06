---
record: 2026-11-06-power-switch-decay-06
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
  - libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.9.2.dev103+g9f4cec35997a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: tt
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
  path: sim/records/raw/2026-11-06-power-switch-decay-06/
  files:
    - corner.cir  sha256:efbb06bb35776474af6b17564519a34eb8853e9f5a88ad8e42af8bf162d5f580
    - ngspice.log  sha256:4a3e07b1936c61d3e98ab8cab9b57ac5918eea7891a3438dbbd154a1b6b760a0
    - report-unit.json  sha256:097c66246cfe45dafcdfd5659fee85f83be86f8c83a26e495608656c3cc006f0
wall_time: 1.423s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-4e9ae62ec34f, klt-sim-ebb0911800c8, klt-sim-26acdf91779c). The switch starts on with the rail at vdd; sleep rises at 100 ns. Times are from the start of the sleep rise, in seconds, and are the first fall through 90 %, 50 % and 5 % of vdd. A `reached_t05` of 0 means the rail never fell to 5 % of vdd within the 100000 s run, and the matching `t_decay_s_t05` is then the run length, not a crossing. `vmin_v` is the lowest rail voltage seen; `vfin_v` the rail at 99000 s. Case suffix is rail capacitance and sleep rise time.

- `t_decay_s_t90_50pf_10ns`: 1.149163e-04
- `t_decay_s_t50_50pf_10ns`: 9.364866e-04
- `t_decay_s_t05_50pf_10ns`: 3.555423e-03
- `reached_t90_50pf_10ns`: 1.000000e+00
- `reached_t50_50pf_10ns`: 1.000000e+00
- `reached_t05_50pf_10ns`: 1.000000e+00
- `vmin_v_50pf_10ns`: 1.291014e-03
- `vfin_v_50pf_10ns`: 8.323297e-03
- `t_decay_s_t90_200pf_10ns`: 4.510376e-04
- `t_decay_s_t50_200pf_10ns`: 3.622379e-03
- `t_decay_s_t05_200pf_10ns`: 1.495452e-02
- `reached_t90_200pf_10ns`: 1.000000e+00
- `reached_t50_200pf_10ns`: 1.000000e+00
- `reached_t05_200pf_10ns`: 1.000000e+00
- `vmin_v_200pf_10ns`: 4.633727e-03
- `vfin_v_200pf_10ns`: 8.323297e-03
- `t_decay_s_t90_50pf_1000ns`: 1.144830e-04
- `t_decay_s_t50_50pf_1000ns`: 9.360357e-04
- `t_decay_s_t05_50pf_1000ns`: 3.554997e-03
- `reached_t90_50pf_1000ns`: 1.000000e+00
- `reached_t50_50pf_1000ns`: 1.000000e+00
- `reached_t05_50pf_1000ns`: 1.000000e+00
- `vmin_v_50pf_1000ns`: 1.300568e-03
- `vfin_v_50pf_1000ns`: 8.323297e-03
- `t_decay_s_t90_200pf_1000ns`: 4.489454e-04
- `t_decay_s_t50_200pf_1000ns`: 3.620375e-03
- `t_decay_s_t05_200pf_1000ns`: 1.495170e-02
- `reached_t90_200pf_1000ns`: 1.000000e+00
- `reached_t50_200pf_1000ns`: 1.000000e+00
- `reached_t05_200pf_1000ns`: 1.000000e+00
- `vmin_v_200pf_1000ns`: 4.616774e-03
- `vfin_v_200pf_1000ns`: 8.323297e-03

Numbers only. No spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch_decay.py emit --check
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend batch
python3 sim/tools/power_switch_decay.py run --outdir DIR --backend local --only tt/125/3.30   # single-point probe
python3 sim/tools/power_switch_decay.py analyze DIR/grid.report.json
```

## Caveats

- Pre-layout, schematic-level: the netlist of `design/power_switch.spice`, no extracted wiring.
- The rail is discharged only by a leakage-equivalent off NFET (710 um) and the switch's own off leakage; no bleeder, no cell switching current and no isolation or pad structure. The decay is therefore a leakage-limited bound, not a prediction of the real gated section.
- The 50/200 pF rail capacitances are the assumptions of the wake group, not extractions.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/power_switch_decay.py record`. Append-only: never edit or delete this file.
