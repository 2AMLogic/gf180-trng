---
record: 2026-10-28-power-switch-26
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
  path: sim/records/raw/2026-10-28-power-switch-26/
  files:
    - corner.cir  sha256:d67c90c3c4e90d2af2d2c30fa6b372baa71d0659de2245e9fde19fa426842f5f
    - ngspice.log  sha256:e2021a1047053b456382c6a449e4a4a4ddcc5d2482a82b134c6f9ef39b9600f1
    - report-unit.json  sha256:a2e57c8c7fb3271eeb29df0eceb429b228f0d16ad56222e3eec188f96303b760
wall_time: 1.829s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.479257e-03
- `droop_v_100um_b`: 8.985804e-02
- `droop_v_200um_a`: 2.238196e-03
- `droop_v_200um_b`: 4.434571e-02
- `droop_v_400um_a`: 1.118741e-03
- `droop_v_400um_b`: 2.203169e-02
- `droop_v_800um_a`: 5.592811e-04
- `droop_v_800um_b`: 1.098111e-02
- `ron_ohm_100um_a`: 4.632117e+01
- `ron_ohm_100um_b`: 4.746859e+01
- `ron_ohm_200um_a`: 2.314577e+01
- `ron_ohm_200um_b`: 2.342615e+01
- `ron_ohm_400um_a`: 1.156919e+01
- `ron_ohm_400um_b`: 1.163851e+01
- `ron_ohm_800um_a`: 5.783672e+00
- `ron_ohm_800um_b`: 5.800906e+00
- `p_loss_w_100um_a`: 4.331442e-07
- `p_loss_w_100um_b`: 1.701013e-04
- `p_loss_w_200um_a`: 2.164336e-07
- `p_loss_w_200um_b`: 8.394642e-05
- `p_loss_w_400um_a`: 1.081822e-07
- `p_loss_w_400um_b`: 4.170600e-05
- `p_loss_w_800um_a`: 5.408248e-08
- `p_loss_w_800um_b`: 2.078725e-05
- `ileak_a_100um`: 4.739950e-11
- `ileak_a_200um`: 9.479900e-11
- `ileak_a_400um`: 1.895980e-10
- `ileak_a_800um`: 3.791960e-10
- `i_stack_a`: 9.606358e-11
- `v_stack_v`: 1.240006e+00
- `i_ungated_a`: 3.056176e-10
- `stack_reduction_x`: 3.181410e+00
- `ipk_a_50pf_10ns`: 3.666686e-02
- `t_settle_s_50pf_10ns`: 8.269117e-09
- `vfin_v_50pf_10ns`: 3.630000e+00
- `ipk_a_200pf_10ns`: 6.802529e-02
- `t_settle_s_200pf_10ns`: 1.467977e-08
- `vfin_v_200pf_10ns`: 3.630000e+00
- `ipk_a_50pf_1000ns`: 2.488378e-03
- `t_settle_s_50pf_1000ns`: 3.245047e-07
- `vfin_v_50pf_1000ns`: 3.630000e+00
- `ipk_a_200pf_1000ns`: 6.073609e-03
- `t_settle_s_200pf_1000ns`: 3.884719e-07
- `vfin_v_200pf_1000ns`: 3.630000e+00

At this corner the 400 um switch has 11.64 ohm on-resistance at the 20 MHz bound load, leaks 0.190 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.096 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/27/3.63   # single-point probe
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
