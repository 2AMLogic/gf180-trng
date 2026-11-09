---
record: 2026-10-28-power-switch-27
date: 2026-10-28T07:25:25Z
status: valid

testbench:
  path: sim/tb/power-switch/tb_power_switch.sp
  sha: b23081dbb36fd553e491f76dd08dfc235286cc2d
netlist:
  path: design/power_switch.spice
  sha: f14b87ff4bb74a439a5eb3cd5a2f6ffe3f616d44
repo_commit: 18d24d110c54ae2309dcd6694ec581798a7e1c62-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: tran (deterministic)
  tstop: 3.5u
  tstep: 100p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-28-power-switch-27/
  files:
    - corner.cir  sha256:44280bed84c92b3ca21b44b7b9108891d84be3da3d9b49a0024b2deec1bb3858
    - ngspice.log  sha256:549de8cb9ae50cf2a9c57a26ecae4874109b0a98bbcee846c5442cbb286d5a1c
    - report-unit.json  sha256:9d9f4b47e78660e2cb121b9685d81c095d6433072f0c3015dc9c1f1ce2edf75a
wall_time: 1.876s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.375242e-03
- `droop_v_100um_b`: 1.081161e-01
- `droop_v_200um_a`: 2.685725e-03
- `droop_v_200um_b`: 5.328000e-02
- `droop_v_400um_a`: 1.342389e-03
- `droop_v_400um_b`: 2.645249e-02
- `droop_v_800um_a`: 6.710765e-04
- `droop_v_800um_b`: 1.318020e-02
- `ron_ohm_100um_a`: 5.558678e+01
- `ron_ohm_100um_b`: 5.711363e+01
- `ron_ohm_200um_a`: 2.777378e+01
- `ron_ohm_200um_b`: 2.814580e+01
- `ron_ohm_400um_a`: 1.388200e+01
- `ron_ohm_400um_b`: 1.397385e+01
- `ron_ohm_800um_a`: 6.939778e+00
- `ron_ohm_800um_b`: 6.962598e+00
- `p_loss_w_100um_a`: 5.197859e-07
- `p_loss_w_100um_b`: 2.046638e-04
- `p_loss_w_200um_a`: 2.597096e-07
- `p_loss_w_200um_b`: 1.008590e-04
- `p_loss_w_400um_a`: 1.298091e-07
- `p_loss_w_400um_b`: 5.007456e-05
- `p_loss_w_800um_a`: 6.489310e-08
- `p_loss_w_800um_b`: 2.495011e-05
- `ileak_a_100um`: 1.319762e-10
- `ileak_a_200um`: 2.639525e-10
- `ileak_a_400um`: 5.279050e-10
- `ileak_a_800um`: 1.055810e-09
- `i_stack_a`: 5.254249e-10
- `v_stack_v`: 1.021924e-02
- `i_ungated_a`: 2.308808e-08
- `stack_reduction_x`: 4.394172e+01
- `ipk_a_50pf_10ns`: 4.567645e-02
- `t_settle_s_50pf_10ns`: 9.616645e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 8.155212e-02
- `t_settle_s_200pf_10ns`: 1.892802e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.963427e-03
- `t_settle_s_50pf_1000ns`: 3.159651e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 7.337137e-03
- `t_settle_s_200pf_1000ns`: 3.976482e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 13.97 ohm on-resistance at the 20 MHz bound load, leaks 0.528 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.525 nA (ungated reference 23.1 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/125/3.63   # single-point probe
python3 sim/tools/power_switch.py analyze DIR/grid.report.json
```

## Caveats

- Pre-layout, schematic-level: the switch is the netlist of `design/power_switch.spice`, with no extracted wiring, no well/tap resistance and no package or bond-wire inductance.
- The digital load is a leakage-equivalent off NFET (710 um = 71 x 10 um) and fixed DC currents, not the gate-level cells; the 50/200 pF rail capacitances are assumptions, not extractions. See the deck header.
- The static readings use the DC loads of the deck; instantaneous clock-edge current peaks are not modelled, so droop at a clock edge is bounded here only by the 20 MHz average load.
- Gate leakage of the digital cells and of the switch is not separated from channel leakage.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/power_switch.py record`. Append-only: never edit or delete this file.
