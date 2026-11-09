---
record: 2026-10-28-power-switch-39
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
  path: sim/records/raw/2026-10-28-power-switch-39/
  files:
    - corner.cir  sha256:f9df6315bf7a1f42a23f9f119a31b3ea199d44aa553f0ea09e48915a6d9ffdf6
    - ngspice.log  sha256:0e1d3e5befce0d86969c5ef683de234de4f811196d3b62575374312e4ccae0fc
    - report-unit.json  sha256:65f5fc4c7eca198e9d0dda4d302ff9585e7fe331c7defb1f70d4075faa17d76b
wall_time: 1.971s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.086872e-03
- `droop_v_100um_b`: 1.024839e-01
- `droop_v_200um_a`: 2.541539e-03
- `droop_v_200um_b`: 5.045904e-02
- `droop_v_400um_a`: 1.270296e-03
- `droop_v_400um_b`: 2.504142e-02
- `droop_v_800um_a`: 6.350299e-04
- `droop_v_800um_b`: 1.247458e-02
- `ron_ohm_100um_a`: 5.260468e+01
- `ron_ohm_100um_b`: 5.413838e+01
- `ron_ohm_200um_a`: 2.628272e+01
- `ron_ohm_200um_b`: 2.665559e+01
- `ron_ohm_400um_a`: 1.313647e+01
- `ron_ohm_400um_b`: 1.322843e+01
- `ron_ohm_800um_a`: 6.567011e+00
- `ron_ohm_800um_b`: 6.589848e+00
- `p_loss_w_100um_a`: 4.919005e-07
- `p_loss_w_100um_b`: 1.940021e-04
- `p_loss_w_200um_a`: 2.457668e-07
- `p_loss_w_200um_b`: 9.551896e-05
- `p_loss_w_400um_a`: 1.228377e-07
- `p_loss_w_400um_b`: 4.740340e-05
- `p_loss_w_800um_a`: 6.140739e-08
- `p_loss_w_800um_b`: 2.361438e-05
- `ileak_a_100um`: 4.467382e-09
- `ileak_a_200um`: 8.934764e-09
- `ileak_a_400um`: 1.786953e-08
- `ileak_a_800um`: 3.573905e-08
- `i_stack_a`: 1.054516e-08
- `v_stack_v`: 1.525932e+00
- `i_ungated_a`: 2.528493e-08
- `stack_reduction_x`: 2.397775e+00
- `ipk_a_50pf_10ns`: 2.148966e-02
- `t_settle_s_50pf_10ns`: 7.516432e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 3.935180e-02
- `t_settle_s_200pf_10ns`: 1.349069e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 1.430837e-03
- `t_settle_s_50pf_1000ns`: 2.602868e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 3.624469e-03
- `t_settle_s_200pf_1000ns`: 3.245178e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 13.23 ohm on-resistance at the 20 MHz bound load, leaks 17.870 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 10.545 nA (ungated reference 25.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only sf/125/2.97   # single-point probe
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
