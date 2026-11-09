---
record: 2026-10-28-power-switch-41
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
  - libs.tech/ngspice/sm141064.ngspice (sections: sf bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: sf
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran (deterministic)
  tstop: 3.5u
  tstep: 100p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-28-power-switch-41/
  files:
    - corner.cir  sha256:c775da68e0ebf3195873bf604456ac13aa5c98ec201f7640237bb0052002f428
    - ngspice.log  sha256:1638d824edd7616aeb87c350b9a52f2b811cc72c8e773ce97b6fcec9a9f0d818
    - report-unit.json  sha256:9677a2b53097a04db0ed8327f5c5e6eb0b52468116a3f41f0f69316d00af4a99
wall_time: 1.92s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.955575e-03
- `droop_v_100um_b`: 7.912777e-02
- `droop_v_200um_a`: 1.976666e-03
- `droop_v_200um_b`: 3.911002e-02
- `droop_v_400um_a`: 9.880531e-04
- `droop_v_400um_b`: 1.944480e-02
- `droop_v_800um_a`: 4.939566e-04
- `droop_v_800um_b`: 9.695238e-03
- `ron_ohm_100um_a`: 4.090564e+01
- `ron_ohm_100um_b`: 4.180020e+01
- `ron_ohm_200um_a`: 2.044122e+01
- `ron_ohm_200um_b`: 2.066034e+01
- `ron_ohm_400um_a`: 1.021772e+01
- `ron_ohm_400um_b`: 1.027195e+01
- `ron_ohm_800um_a`: 5.108135e+00
- `ron_ohm_800um_b`: 5.121626e+00
- `p_loss_w_100um_a`: 3.825041e-07
- `p_loss_w_100um_b`: 1.497889e-04
- `p_loss_w_200um_a`: 1.911436e-07
- `p_loss_w_200um_b`: 7.403527e-05
- `p_loss_w_400um_a`: 9.554474e-08
- `p_loss_w_400um_b`: 3.680901e-05
- `p_loss_w_800um_a`: 4.776561e-08
- `p_loss_w_800um_b`: 1.835309e-05
- `ileak_a_100um`: 4.865133e-11
- `ileak_a_200um`: 9.730267e-11
- `ileak_a_400um`: 1.946053e-10
- `ileak_a_800um`: 3.892107e-10
- `i_stack_a`: 1.008270e-10
- `v_stack_v`: 1.219117e+00
- `i_ungated_a`: 3.041218e-10
- `stack_reduction_x`: 3.016275e+00
- `ipk_a_50pf_10ns`: 3.412091e-02
- `t_settle_s_50pf_10ns`: 7.445657e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 6.357286e-02
- `t_settle_s_200pf_10ns`: 1.308112e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.246768e-03
- `t_settle_s_50pf_1000ns`: 2.773933e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 5.575779e-03
- `t_settle_s_200pf_1000ns`: 3.375837e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 10.27 ohm on-resistance at the 20 MHz bound load, leaks 0.195 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.101 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only sf/27/3.30   # single-point probe
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
