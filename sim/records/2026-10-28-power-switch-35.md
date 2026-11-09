---
record: 2026-10-28-power-switch-35
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
  path: sim/records/raw/2026-10-28-power-switch-35/
  files:
    - corner.cir  sha256:545cedc9f2c89b976033de94892b564e17b2cbba40a81ad318ffeec01b3b5e87
    - ngspice.log  sha256:b08be9fe3cbb3cfbafce201ba7ac1e2fdbf2f3ac488cd774e6ff5d0e991b6b50
    - report-unit.json  sha256:37b83a92344f2ffcce7e1b90eafe82dd2a5cbf17d1dfc2ae68e1b810dc2c9b0e
wall_time: 2.056s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.334686e-03
- `droop_v_100um_b`: 8.680769e-02
- `droop_v_200um_a`: 2.166053e-03
- `droop_v_200um_b`: 4.288028e-02
- `droop_v_400um_a`: 1.082704e-03
- `droop_v_400um_b`: 2.131319e-02
- `droop_v_800um_a`: 5.412717e-04
- `droop_v_800um_b`: 1.062533e-02
- `ron_ohm_100um_a`: 4.482612e+01
- `ron_ohm_100um_b`: 4.585721e+01
- `ron_ohm_200um_a`: 2.239972e+01
- `ron_ohm_200um_b`: 2.265202e+01
- `ron_ohm_400um_a`: 1.119653e+01
- `ron_ohm_400um_b`: 1.125895e+01
- `ron_ohm_800um_a`: 5.597433e+00
- `ron_ohm_800um_b`: 5.612956e+00
- `p_loss_w_100um_a`: 4.191642e-07
- `p_loss_w_100um_b`: 1.643270e-04
- `p_loss_w_200um_a`: 2.094573e-07
- `p_loss_w_200um_b`: 8.117237e-05
- `p_loss_w_400um_a`: 1.046975e-07
- `p_loss_w_400um_b`: 4.034586e-05
- `p_loss_w_800um_a`: 5.234098e-08
- `p_loss_w_800um_b`: 2.011374e-05
- `ileak_a_100um`: 5.062963e-11
- `ileak_a_200um`: 1.012593e-10
- `ileak_a_400um`: 2.025185e-10
- `ileak_a_800um`: 4.050370e-10
- `i_stack_a`: 1.944300e-10
- `v_stack_v`: 3.998285e-02
- `i_ungated_a`: 8.589897e-09
- `stack_reduction_x`: 4.417989e+01
- `ipk_a_50pf_10ns`: 5.087475e-02
- `t_settle_s_50pf_10ns`: 8.987101e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 9.472779e-02
- `t_settle_s_200pf_10ns`: 1.671805e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 3.273599e-03
- `t_settle_s_50pf_1000ns`: 3.271653e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 8.089130e-03
- `t_settle_s_200pf_1000ns`: 3.997161e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 11.26 ohm on-resistance at the 20 MHz bound load, leaks 0.203 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.194 nA (ungated reference 8.6 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/27/3.63   # single-point probe
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
