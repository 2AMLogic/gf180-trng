---
record: 2026-10-28-power-switch-28
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
  temperature: -40

analysis:
  type: tran (deterministic)
  tstop: 3.5u
  tstep: 100p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-28-power-switch-28/
  files:
    - corner.cir  sha256:f869cdf8a72fcacb82697d65f109497eea3f082a0cbaa71c3e1f90140c9902eb
    - ngspice.log  sha256:9d388253f9eb29b4c62c3ed5097a15cf49437e095efd6f72e1ac9405cd7f8ae6
    - report-unit.json  sha256:25550ad48c5074d2ce99e3d36dcc3ce6ca0e55dc077a85712bfab750b755e5c1
wall_time: 1.872s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.205804e-03
- `droop_v_100um_b`: 8.486491e-02
- `droop_v_200um_a`: 2.101250e-03
- `droop_v_200um_b`: 4.174918e-02
- `droop_v_400um_a`: 1.050213e-03
- `droop_v_400um_b`: 2.071062e-02
- `droop_v_800um_a`: 5.250035e-04
- `droop_v_800um_b`: 1.031512e-02
- `ron_ohm_100um_a`: 4.349332e+01
- `ron_ohm_100um_b`: 4.483091e+01
- `ron_ohm_200um_a`: 2.172958e+01
- `ron_ohm_200um_b`: 2.205451e+01
- `ron_ohm_400um_a`: 1.086053e+01
- `ron_ohm_400um_b`: 1.094063e+01
- `ron_ohm_800um_a`: 5.429198e+00
- `ron_ohm_800um_b`: 5.449088e+00
- `p_loss_w_100um_a`: 4.067012e-07
- `p_loss_w_100um_b`: 1.606493e-04
- `p_loss_w_200um_a`: 2.031909e-07
- `p_loss_w_200um_b`: 7.903120e-05
- `p_loss_w_400um_a`: 1.015556e-07
- `p_loss_w_400um_b`: 3.920520e-05
- `p_loss_w_800um_a`: 5.076784e-08
- `p_loss_w_800um_b`: 1.952653e-05
- `ileak_a_100um`: 3.095986e-11
- `ileak_a_200um`: 6.191972e-11
- `ileak_a_400um`: 1.238394e-10
- `ileak_a_800um`: 2.476789e-10
- `i_stack_a`: 7.675421e-11
- `v_stack_v`: 1.053623e+00
- `i_ungated_a`: 2.226098e-10
- `stack_reduction_x`: 2.900295e+00
- `ipk_a_50pf_10ns`: 3.122574e-02
- `t_settle_s_50pf_10ns`: 8.622018e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 5.857218e-02
- `t_settle_s_200pf_10ns`: 1.464919e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 2.071906e-03
- `t_settle_s_50pf_1000ns`: 3.886779e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 5.078666e-03
- `t_settle_s_200pf_1000ns`: 4.498911e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 10.94 ohm on-resistance at the 20 MHz bound load, leaks 0.124 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.077 nA (ungated reference 0.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/-40/2.97   # single-point probe
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
