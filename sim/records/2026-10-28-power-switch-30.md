---
record: 2026-10-28-power-switch-30
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
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
  path: sim/records/raw/2026-10-28-power-switch-30/
  files:
    - corner.cir  sha256:b02c69808ee1ff0e40e78a9f4ba3f9b6ed5cd3313725bff7ce8c2812fe3df517
    - ngspice.log  sha256:0ee2efb6799b1235fd78a3a9321df81799f501238dccf5e85e94fdd0f0934800
    - report-unit.json  sha256:6e9fbdffae6929509346a1da217ef72a4ee8114f3b3dcce839269ad2dabba929
wall_time: 1.872s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 6.028869e-03
- `droop_v_100um_b`: 1.224501e-01
- `droop_v_200um_a`: 3.011583e-03
- `droop_v_200um_b`: 6.002266e-02
- `droop_v_400um_a`: 1.505081e-03
- `droop_v_400um_b`: 2.972583e-02
- `droop_v_800um_a`: 7.523628e-04
- `droop_v_800um_b`: 1.479329e-02
- `ron_ohm_100um_a`: 6.234611e+01
- `ron_ohm_100um_b`: 6.468574e+01
- `ron_ohm_200um_a`: 3.114357e+01
- `ron_ohm_200um_b`: 3.170769e+01
- `ron_ohm_400um_a`: 1.556443e+01
- `ron_ohm_400um_b`: 1.570303e+01
- `ron_ohm_800um_a`: 7.780380e+00
- `ron_ohm_800um_b`: 7.814733e+00
- `p_loss_w_100um_a`: 5.829916e-07
- `p_loss_w_100um_b`: 2.317980e-04
- `p_loss_w_200um_a`: 2.912201e-07
- `p_loss_w_200um_b`: 1.136229e-04
- `p_loss_w_400um_a`: 1.455413e-07
- `p_loss_w_400um_b`: 5.627099e-05
- `p_loss_w_800um_a`: 7.275348e-08
- `p_loss_w_800um_b`: 2.800370e-05
- `ileak_a_100um`: 1.481813e-10
- `ileak_a_200um`: 2.963626e-10
- `ileak_a_400um`: 5.927252e-10
- `ileak_a_800um`: 1.185450e-09
- `i_stack_a`: 5.927251e-10
- `v_stack_v`: 3.053991e-04
- `i_ungated_a`: 7.453696e-07
- `stack_reduction_x`: 1.257530e+03
- `ipk_a_50pf_10ns`: 3.626848e-02
- `t_settle_s_50pf_10ns`: 1.028371e-08
- `vfin_v_50pf_10ns`: 2.969988e+00
- `ipk_a_200pf_10ns`: 6.059355e-02
- `t_settle_s_200pf_10ns`: 2.064172e-08
- `vfin_v_200pf_10ns`: 2.969988e+00
- `ipk_a_50pf_1000ns`: 2.300966e-03
- `t_settle_s_50pf_1000ns`: 3.554514e-07
- `vfin_v_50pf_1000ns`: 2.969988e+00
- `ipk_a_200pf_1000ns`: 5.767195e-03
- `t_settle_s_200pf_1000ns`: 4.417104e-07
- `vfin_v_200pf_1000ns`: 2.969988e+00

At this corner the 400 um switch has 15.70 ohm on-resistance at the 20 MHz bound load, leaks 0.593 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.593 nA (ungated reference 745.4 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/125/2.97   # single-point probe
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
