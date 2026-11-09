---
record: 2026-10-28-power-switch-19
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
  path: sim/records/raw/2026-10-28-power-switch-19/
  files:
    - corner.cir  sha256:73f0a1ab60ec9729762e9ae3758ba252426265fa5370ec48d246b9bc46cc0388
    - ngspice.log  sha256:138f3cd7eebc45621b57d75d8df1a1f6551a19e4d978e1d559d82fb883d313c2
    - report-unit.json  sha256:6f313d35532afe2b5e47a089319b64ea7cb5362450b8c2a95b948b0e41788744
wall_time: 1.836s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.363779e-03
- `droop_v_100um_b`: 8.827630e-02
- `droop_v_200um_a`: 2.180037e-03
- `droop_v_200um_b`: 4.336748e-02
- `droop_v_400um_a`: 1.089556e-03
- `droop_v_400um_b`: 2.149936e-02
- `droop_v_800um_a`: 5.446626e-04
- `droop_v_800um_b`: 1.070456e-02
- `ron_ohm_100um_a`: 4.512698e+01
- `ron_ohm_100um_b`: 4.663302e+01
- `ron_ohm_200um_a`: 2.254433e+01
- `ron_ohm_200um_b`: 2.290939e+01
- `ron_ohm_400um_a`: 1.126738e+01
- `ron_ohm_400um_b`: 1.135730e+01
- `ron_ohm_800um_a`: 5.632499e+00
- `ron_ohm_800um_b`: 5.654812e+00
- `p_loss_w_100um_a`: 4.219774e-07
- `p_loss_w_100um_b`: 1.671070e-04
- `p_loss_w_200um_a`: 2.108095e-07
- `p_loss_w_200um_b`: 8.209465e-05
- `p_loss_w_400um_a`: 1.053601e-07
- `p_loss_w_400um_b`: 4.069829e-05
- `p_loss_w_800um_a`: 5.266887e-08
- `p_loss_w_800um_b`: 2.026373e-05
- `ileak_a_100um`: 3.065571e-11
- `ileak_a_200um`: 6.131142e-11
- `ileak_a_400um`: 1.226228e-10
- `ileak_a_800um`: 2.452457e-10
- `i_stack_a`: 7.598205e-11
- `v_stack_v`: 1.065357e+00
- `i_ungated_a`: 2.115999e-10
- `stack_reduction_x`: 2.784868e+00
- `ipk_a_50pf_10ns`: 3.046352e-02
- `t_settle_s_50pf_10ns`: 8.819806e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 5.708813e-02
- `t_settle_s_200pf_10ns`: 1.506138e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 2.033870e-03
- `t_settle_s_50pf_1000ns`: 4.005245e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 4.972555e-03
- `t_settle_s_200pf_1000ns`: 4.626152e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 11.36 ohm on-resistance at the 20 MHz bound load, leaks 0.123 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.076 nA (ungated reference 0.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/-40/2.97   # single-point probe
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
