---
record: 2026-10-28-power-switch-23
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
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
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
  path: sim/records/raw/2026-10-28-power-switch-23/
  files:
    - corner.cir  sha256:e2149a5b10806a8a27a69bdb55af51bede613e754061848c23aabe427fd39a58
    - ngspice.log  sha256:75d34efd6f16749424cc53e93cf39ad602b8f7a00903ce06fc8afc24491910bd
    - report-unit.json  sha256:4c2d83354e2dc953bf07f3985e15542a4d72dfe1e1f39cbe93465e77a0fe39c5
wall_time: 1.874s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.788141e-03
- `droop_v_100um_b`: 9.651438e-02
- `droop_v_200um_a`: 2.392252e-03
- `droop_v_200um_b`: 4.750722e-02
- `droop_v_400um_a`: 1.195672e-03
- `droop_v_400um_b`: 2.357335e-02
- `droop_v_800um_a`: 5.977228e-04
- `droop_v_800um_b`: 1.174247e-02
- `ron_ohm_100um_a`: 4.951541e+01
- `ron_ohm_100um_b`: 5.098488e+01
- `ron_ohm_200um_a`: 2.473890e+01
- `ron_ohm_200um_b`: 2.509626e+01
- `ron_ohm_400um_a`: 1.236476e+01
- `ron_ohm_400um_b`: 1.245291e+01
- `ron_ohm_800um_a`: 6.181208e+00
- `ron_ohm_800um_b`: 6.203099e+00
- `p_loss_w_100um_a`: 4.630132e-07
- `p_loss_w_100um_b`: 1.827017e-04
- `p_loss_w_200um_a`: 2.313308e-07
- `p_loss_w_200um_b`: 8.993117e-05
- `p_loss_w_400um_a`: 1.156215e-07
- `p_loss_w_400um_b`: 4.462436e-05
- `p_loss_w_800um_a`: 5.779980e-08
- `p_loss_w_800um_b`: 2.222849e-05
- `ileak_a_100um`: 3.665921e-11
- `ileak_a_200um`: 7.331841e-11
- `ileak_a_400um`: 1.466368e-10
- `ileak_a_800um`: 2.932737e-10
- `i_stack_a`: 8.756398e-11
- `v_stack_v`: 1.124525e+00
- `i_ungated_a`: 2.707304e-10
- `stack_reduction_x`: 3.091800e+00
- `ipk_a_50pf_10ns`: 3.247154e-02
- `t_settle_s_50pf_10ns`: 8.676965e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 6.041788e-02
- `t_settle_s_200pf_10ns`: 1.544409e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.190116e-03
- `t_settle_s_50pf_1000ns`: 3.506068e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 5.365516e-03
- `t_settle_s_200pf_1000ns`: 4.167470e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 12.45 ohm on-resistance at the 20 MHz bound load, leaks 0.147 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.088 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/27/3.30   # single-point probe
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
