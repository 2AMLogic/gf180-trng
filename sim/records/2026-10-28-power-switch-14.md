---
record: 2026-10-28-power-switch-14
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
  - libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ff
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
  path: sim/records/raw/2026-10-28-power-switch-14/
  files:
    - corner.cir  sha256:28da44087f8bfcee61f84ed5442f7a45444d074d6bcd3b9334e7d383838a1443
    - ngspice.log  sha256:4ebddead92076852f1703206b9008196aca2bd8179c5ab6207fe310468120730
    - report-unit.json  sha256:34355ae87b77922f6dc8e73d20dbe232e165057b8b8731ae1b05163a42c0ea2d
wall_time: 1.919s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.819088e-03
- `droop_v_100um_b`: 7.632002e-02
- `droop_v_200um_a`: 1.908511e-03
- `droop_v_200um_b`: 3.774290e-02
- `droop_v_400um_a`: 9.539973e-04
- `droop_v_400um_b`: 1.877002e-02
- `droop_v_800um_a`: 4.769342e-04
- `droop_v_800um_b`: 9.359998e-03
- `ron_ohm_100um_a`: 3.949419e+01
- `ron_ohm_100um_b`: 4.031697e+01
- `ron_ohm_200um_a`: 1.973641e+01
- `ron_ohm_200um_b`: 1.993814e+01
- `ron_ohm_400um_a`: 9.865536e+00
- `ron_ohm_400um_b`: 9.915490e+00
- `ron_ohm_800um_a`: 4.932102e+00
- `ron_ohm_800um_b`: 4.944531e+00
- `p_loss_w_100um_a`: 3.693058e-07
- `p_loss_w_100um_b`: 1.444738e-04
- `p_loss_w_200um_a`: 1.845530e-07
- `p_loss_w_200um_b`: 7.144730e-05
- `p_loss_w_400um_a`: 9.225154e-08
- `p_loss_w_400um_b`: 3.553165e-05
- `p_loss_w_800um_a`: 4.611954e-08
- `p_loss_w_800um_b`: 1.771848e-05
- `ileak_a_100um`: 6.011240e-11
- `ileak_a_200um`: 1.202248e-10
- `ileak_a_400um`: 2.404496e-10
- `ileak_a_800um`: 4.808992e-10
- `i_stack_a`: 2.359105e-10
- `v_stack_v`: 2.022926e-02
- `i_ungated_a`: 1.267646e-08
- `stack_reduction_x`: 5.373420e+01
- `ipk_a_50pf_10ns`: 4.882373e-02
- `t_settle_s_50pf_10ns`: 8.213148e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 9.311187e-02
- `t_settle_s_200pf_10ns`: 1.508425e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 3.042564e-03
- `t_settle_s_50pf_1000ns`: 2.796104e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 7.642130e-03
- `t_settle_s_200pf_1000ns`: 3.488441e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 9.92 ohm on-resistance at the 20 MHz bound load, leaks 0.240 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.236 nA (ungated reference 12.7 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/27/3.30   # single-point probe
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
