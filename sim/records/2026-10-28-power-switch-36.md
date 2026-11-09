---
record: 2026-10-28-power-switch-36
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
  - libs.tech/ngspice/sm141064.ngspice (sections: fs bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: fs
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
  path: sim/records/raw/2026-10-28-power-switch-36/
  files:
    - corner.cir  sha256:6e0bf54588d7059454abbad4213125c4c5f27208f0598f9d805f66fa7671c8bb
    - ngspice.log  sha256:bbc4e1737a42c396f3fa0948746773ae35d7935aad4b4362b21fd8f6272a04c3
    - report-unit.json  sha256:6f9456524d0babdcd0e06ce8d4f6644898044770821225a0357e23b6655adecc
wall_time: 2.058s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.189819e-03
- `droop_v_100um_b`: 1.041866e-01
- `droop_v_200um_a`: 2.593205e-03
- `droop_v_200um_b`: 5.139683e-02
- `droop_v_400um_a`: 1.296177e-03
- `droop_v_400um_b`: 2.553018e-02
- `droop_v_800um_a`: 6.479824e-04
- `droop_v_800um_b`: 1.272373e-02
- `ron_ohm_100um_a`: 5.366928e+01
- `ron_ohm_100um_b`: 5.503781e+01
- `ron_ohm_200um_a`: 2.681701e+01
- `ron_ohm_200um_b`: 2.715099e+01
- `ron_ohm_400um_a`: 1.340411e+01
- `ron_ohm_400um_b`: 1.348663e+01
- `ron_ohm_800um_a`: 6.700956e+00
- `ron_ohm_800um_b`: 6.721466e+00
- `p_loss_w_100um_a`: 5.018555e-07
- `p_loss_w_100um_b`: 1.972252e-04
- `p_loss_w_200um_a`: 2.507630e-07
- `p_loss_w_200um_b`: 9.729420e-05
- `p_loss_w_400um_a`: 1.253403e-07
- `p_loss_w_400um_b`: 4.832864e-05
- `p_loss_w_800um_a`: 6.265990e-08
- `p_loss_w_800um_b`: 2.408603e-05
- `ileak_a_100um`: 1.933351e-10
- `ileak_a_200um`: 3.866702e-10
- `ileak_a_400um`: 7.733404e-10
- `ileak_a_800um`: 1.546681e-09
- `i_stack_a`: 7.727171e-10
- `v_stack_v`: 3.987224e-04
- `i_ungated_a`: 1.231024e-06
- `stack_reduction_x`: 1.593111e+03
- `ipk_a_50pf_10ns`: 4.670205e-02
- `t_settle_s_50pf_10ns`: 9.395866e-09
- `vfin_v_50pf_10ns`: 3.629984e+00
- `ipk_a_200pf_10ns`: 8.531165e-02
- `t_settle_s_200pf_10ns`: 1.834203e-08
- `vfin_v_200pf_10ns`: 3.629984e+00
- `ipk_a_50pf_1000ns`: 3.011690e-03
- `t_settle_s_50pf_1000ns`: 3.054252e-07
- `vfin_v_50pf_1000ns`: 3.629984e+00
- `ipk_a_200pf_1000ns`: 7.475801e-03
- `t_settle_s_200pf_1000ns`: 3.858036e-07
- `vfin_v_200pf_1000ns`: 3.629984e+00

At this corner the 400 um switch has 13.49 ohm on-resistance at the 20 MHz bound load, leaks 0.773 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.773 nA (ungated reference 1231.0 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/125/3.63   # single-point probe
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
