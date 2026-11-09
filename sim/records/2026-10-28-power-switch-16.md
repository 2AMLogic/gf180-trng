---
record: 2026-10-28-power-switch-16
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
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-10-28-power-switch-16/
  files:
    - corner.cir  sha256:e991ade0ee84b02c8261c4942ef90d4236c4eb0495e2df5ce8cc679ced0168a6
    - ngspice.log  sha256:f1f7d1d3ebc8f825aa38ffb6918bd7f711f10babbb27dd70354676a05072024d
    - report-unit.json  sha256:6c69d759a992daf083225cb24adb52f1d42879d28b4db4c5ef7b02f862c73b8e
wall_time: 1.828s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.079163e-03
- `droop_v_100um_b`: 6.125520e-02
- `droop_v_200um_a`: 1.538928e-03
- `droop_v_200um_b`: 3.036684e-02
- `droop_v_400um_a`: 7.693005e-04
- `droop_v_400um_b`: 1.511959e-02
- `droop_v_800um_a`: 3.846095e-04
- `droop_v_800um_b`: 7.544004e-03
- `ron_ohm_100um_a`: 3.184243e+01
- `ron_ohm_100um_b`: 3.235879e+01
- `ron_ohm_200um_a`: 1.591445e+01
- `ron_ohm_200um_b`: 1.604165e+01
- `ron_ohm_400um_a`: 7.955538e+00
- `ron_ohm_400um_b`: 7.987106e+00
- `ron_ohm_800um_a`: 3.977347e+00
- `ron_ohm_800um_b`: 3.985211e+00
- `p_loss_w_100um_a`: 2.977551e-07
- `p_loss_w_100um_b`: 1.159561e-04
- `p_loss_w_200um_a`: 1.488143e-07
- `p_loss_w_200um_b`: 5.748443e-05
- `p_loss_w_400um_a`: 7.439136e-08
- `p_loss_w_400um_b`: 2.862139e-05
- `p_loss_w_800um_a`: 3.719173e-08
- `p_loss_w_800um_b`: 1.428080e-05
- `ileak_a_100um`: 6.714449e-11
- `ileak_a_200um`: 1.342890e-10
- `ileak_a_400um`: 2.685780e-10
- `ileak_a_800um`: 5.371559e-10
- `i_stack_a`: 9.431437e-11
- `v_stack_v`: 1.274110e+00
- `i_ungated_a`: 3.202620e-10
- `stack_reduction_x`: 3.395686e+00
- `ipk_a_50pf_10ns`: 4.370109e-02
- `t_settle_s_50pf_10ns`: 6.754160e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 8.200420e-02
- `t_settle_s_200pf_10ns`: 1.157970e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.865597e-03
- `t_settle_s_50pf_1000ns`: 2.634369e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 7.068815e-03
- `t_settle_s_200pf_1000ns`: 3.164076e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 7.99 ohm on-resistance at the 20 MHz bound load, leaks 0.269 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.094 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/-40/3.63   # single-point probe
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
