---
record: 2026-10-28-power-switch-29
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
  path: sim/records/raw/2026-10-28-power-switch-29/
  files:
    - corner.cir  sha256:fd2eb8e57b1782039d9467365646db13f59fabc6a185fb5bc819d6c6341bf548
    - ngspice.log  sha256:89f4e9fa71028f2ce349b7e3f64bbafb150911aa56b1762bc3c6ba735df31ccd
    - report-unit.json  sha256:421acb434ad175b0dc055f1be88a3a1da01a73fd8f5fae7d2e5ddd2df180b126
wall_time: 1.873s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.005185e-03
- `droop_v_100um_b`: 1.013062e-01
- `droop_v_200um_a`: 2.500437e-03
- `droop_v_200um_b`: 4.975337e-02
- `droop_v_400um_a`: 1.249681e-03
- `droop_v_400um_b`: 2.466185e-02
- `droop_v_800um_a`: 6.247062e-04
- `droop_v_800um_b`: 1.227840e-02
- `ron_ohm_100um_a`: 5.175993e+01
- `ron_ohm_100um_b`: 5.351620e+01
- `ron_ohm_200um_a`: 2.585768e+01
- `ron_ohm_200um_b`: 2.628282e+01
- `ron_ohm_400um_a`: 1.292328e+01
- `ron_ohm_400um_b`: 1.302792e+01
- `ron_ohm_800um_a`: 6.460251e+00
- `ron_ohm_800um_b`: 6.486211e+00
- `p_loss_w_100um_a`: 4.840014e-07
- `p_loss_w_100um_b`: 1.917726e-04
- `p_loss_w_200um_a`: 2.417923e-07
- `p_loss_w_200um_b`: 9.418313e-05
- `p_loss_w_400um_a`: 1.208442e-07
- `p_loss_w_400um_b`: 4.668488e-05
- `p_loss_w_800um_a`: 6.040909e-08
- `p_loss_w_800um_b`: 2.324301e-05
- `ileak_a_100um`: 3.105035e-11
- `ileak_a_200um`: 6.210069e-11
- `ileak_a_400um`: 1.242014e-10
- `ileak_a_800um`: 2.484028e-10
- `i_stack_a`: 1.227785e-10
- `v_stack_v`: 1.997088e-02
- `i_ungated_a`: 4.658059e-09
- `stack_reduction_x`: 3.793871e+01
- `ipk_a_50pf_10ns`: 3.977199e-02
- `t_settle_s_50pf_10ns`: 9.894588e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 6.790027e-02
- `t_settle_s_200pf_10ns`: 1.879566e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 2.524388e-03
- `t_settle_s_50pf_1000ns`: 3.841453e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 6.276491e-03
- `t_settle_s_200pf_1000ns`: 4.618175e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 13.03 ohm on-resistance at the 20 MHz bound load, leaks 0.124 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.123 nA (ungated reference 4.7 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only fs/27/2.97   # single-point probe
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
