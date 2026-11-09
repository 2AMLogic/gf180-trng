---
record: 2026-10-28-power-switch-10
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
  path: sim/records/raw/2026-10-28-power-switch-10/
  files:
    - corner.cir  sha256:c3a2e39fdf756c1ea17cdafebaf3a537cd743427548258ca4165c7b96facdef8
    - ngspice.log  sha256:aebafb3260bcf895e8bd73247aa1ddb6b9178762013482f0caf44a33c58db111
    - report-unit.json  sha256:820ea48fa42996e7108a8703cf7dd4885443d92bcb097d29ae64f84d4505237c
wall_time: 1.868s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.431726e-03
- `droop_v_100um_b`: 6.870553e-02
- `droop_v_200um_a`: 1.714853e-03
- `droop_v_200um_b`: 3.394355e-02
- `droop_v_400um_a`: 8.571747e-04
- `droop_v_400um_b`: 1.687250e-02
- `droop_v_800um_a`: 4.285244e-04
- `droop_v_800um_b`: 8.411789e-03
- `ron_ohm_100um_a`: 3.548837e+01
- `ron_ohm_100um_b`: 3.629452e+01
- `ron_ohm_200um_a`: 1.773375e+01
- `ron_ohm_200um_b`: 1.793109e+01
- `ron_ohm_400um_a`: 8.864268e+00
- `ron_ohm_400um_b`: 8.913098e+00
- `ron_ohm_800um_a`: 4.431483e+00
- `ron_ohm_800um_b`: 4.443629e+00
- `p_loss_w_100um_a`: 3.318479e-07
- `p_loss_w_100um_b`: 1.300596e-04
- `p_loss_w_200um_a`: 1.658263e-07
- `p_loss_w_200um_b`: 6.425515e-05
- `p_loss_w_400um_a`: 8.288879e-08
- `p_loss_w_400um_b`: 3.193963e-05
- `p_loss_w_800um_a`: 4.143831e-08
- `p_loss_w_800um_b`: 1.592352e-05
- `ileak_a_100um`: 3.275241e-11
- `ileak_a_200um`: 6.550482e-11
- `ileak_a_400um`: 1.310096e-10
- `ileak_a_800um`: 2.620193e-10
- `i_stack_a`: 7.731422e-11
- `v_stack_v`: 1.039245e+00
- `i_ungated_a`: 2.385234e-10
- `stack_reduction_x`: 3.085117e+00
- `ipk_a_50pf_10ns`: 3.401660e-02
- `t_settle_s_50pf_10ns`: 7.468554e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 6.416772e-02
- `t_settle_s_200pf_10ns`: 1.261768e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 2.197506e-03
- `t_settle_s_50pf_1000ns`: 3.103246e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 5.456524e-03
- `t_settle_s_200pf_1000ns`: 3.670340e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 8.91 ohm on-resistance at the 20 MHz bound load, leaks 0.131 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.077 nA (ungated reference 0.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/-40/2.97   # single-point probe
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
