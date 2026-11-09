---
record: 2026-10-28-power-switch-05
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
  - libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: tt
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
  path: sim/records/raw/2026-10-28-power-switch-05/
  files:
    - corner.cir  sha256:05d07a8b34621090355f7569f6758f661bc06ab38e4e1f5c1f3eb12f1ea7f640
    - ngspice.log  sha256:a2e31814ba235863de9caf4bd2c3dbc763069a121c5e4f67b74e88ad48dbb67f
    - report-unit.json  sha256:a88a9217eff8ff7f511618a3ea783d3800ea8b6aa65ae9de9b329f1778803066
wall_time: 1.874s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.274748e-03
- `droop_v_100um_b`: 8.571414e-02
- `droop_v_200um_a`: 2.136034e-03
- `droop_v_200um_b`: 4.231147e-02
- `droop_v_400um_a`: 1.067683e-03
- `droop_v_400um_b`: 2.102370e-02
- `droop_v_800um_a`: 5.337579e-04
- `droop_v_800um_b`: 1.047936e-02
- `ron_ohm_100um_a`: 4.420628e+01
- `ron_ohm_100um_b`: 4.527953e+01
- `ron_ohm_200um_a`: 2.208929e+01
- `ron_ohm_200um_b`: 2.235154e+01
- `ron_ohm_400um_a`: 1.104119e+01
- `ron_ohm_400um_b`: 1.110602e+01
- `ron_ohm_800um_a`: 5.519730e+00
- `ron_ohm_800um_b`: 5.535850e+00
- `p_loss_w_100um_a`: 4.133681e-07
- `p_loss_w_100um_b`: 1.622569e-04
- `p_loss_w_200um_a`: 2.065545e-07
- `p_loss_w_200um_b`: 8.009561e-05
- `p_loss_w_400um_a`: 1.032449e-07
- `p_loss_w_400um_b`: 3.979787e-05
- `p_loss_w_800um_a`: 5.161438e-08
- `p_loss_w_800um_b`: 1.983743e-05
- `ileak_a_100um`: 3.988161e-11
- `ileak_a_200um`: 7.976322e-11
- `ileak_a_400um`: 1.595264e-10
- `ileak_a_800um`: 3.190529e-10
- `i_stack_a`: 1.101977e-10
- `v_stack_v`: 6.411437e-01
- `i_ungated_a`: 8.648517e-10
- `stack_reduction_x`: 7.848186e+00
- `ipk_a_50pf_10ns`: 4.003194e-02
- `t_settle_s_50pf_10ns`: 8.429323e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 7.534706e-02
- `t_settle_s_200pf_10ns`: 1.520063e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.589812e-03
- `t_settle_s_50pf_1000ns`: 3.154258e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 6.421153e-03
- `t_settle_s_200pf_1000ns`: 3.830260e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 11.11 ohm on-resistance at the 20 MHz bound load, leaks 0.160 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.110 nA (ungated reference 0.9 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only tt/27/3.30   # single-point probe
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
