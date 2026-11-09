---
record: 2026-10-28-power-switch-44
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
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-10-28-power-switch-44/
  files:
    - corner.cir  sha256:397ab7decf13b6ac41d98602597345f6a025a10afec09a1674a21f6643ff7b14
    - ngspice.log  sha256:d22e182b63ec1596f433a4e26c43a08c7a227b622b464ce4038e5429064ed4ea
    - report-unit.json  sha256:f7d0964eb4b42597633f081e58703c2bf3827d65fc4c1c876e0c0bb43e710be8
wall_time: 1.927s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.749281e-03
- `droop_v_100um_b`: 7.476461e-02
- `droop_v_200um_a`: 1.873729e-03
- `droop_v_200um_b`: 3.701643e-02
- `droop_v_400um_a`: 9.366368e-04
- `droop_v_400um_b`: 1.841897e-02
- `droop_v_800um_a`: 4.682615e-04
- `droop_v_800um_b`: 9.187445e-03
- `ron_ohm_100um_a`: 3.877229e+01
- `ron_ohm_100um_b`: 3.949530e+01
- `ron_ohm_200um_a`: 1.937672e+01
- `ron_ohm_200um_b`: 1.955437e+01
- `ron_ohm_400um_a`: 9.686006e+00
- `ron_ohm_400um_b`: 9.730044e+00
- `ron_ohm_800um_a`: 4.842415e+00
- `ron_ohm_800um_b`: 4.853378e+00
- `p_loss_w_100um_a`: 3.625554e-07
- `p_loss_w_100um_b`: 1.415294e-04
- `p_loss_w_200um_a`: 1.811896e-07
- `p_loss_w_200um_b`: 7.007210e-05
- `p_loss_w_400um_a`: 9.057278e-08
- `p_loss_w_400um_b`: 3.486711e-05
- `p_loss_w_800um_a`: 4.528089e-08
- `p_loss_w_800um_b`: 1.739183e-05
- `ileak_a_100um`: 6.880578e-11
- `ileak_a_200um`: 1.376116e-10
- `ileak_a_400um`: 2.752231e-10
- `ileak_a_800um`: 5.504462e-10
- `i_stack_a`: 1.108835e-10
- `v_stack_v`: 1.342038e+00
- `i_ungated_a`: 3.501685e-10
- `stack_reduction_x`: 3.157984e+00
- `ipk_a_50pf_10ns`: 3.851118e-02
- `t_settle_s_50pf_10ns`: 7.116568e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 7.156317e-02
- `t_settle_s_200pf_10ns`: 1.255678e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.555654e-03
- `t_settle_s_50pf_1000ns`: 2.574119e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 6.314710e-03
- `t_settle_s_200pf_1000ns`: 3.156093e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 9.73 ohm on-resistance at the 20 MHz bound load, leaks 0.275 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.111 nA (ungated reference 0.4 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only sf/27/3.63   # single-point probe
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
