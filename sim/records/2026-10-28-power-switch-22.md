---
record: 2026-10-28-power-switch-22
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
  path: sim/records/raw/2026-10-28-power-switch-22/
  files:
    - corner.cir  sha256:ca1263342635cbc489b8ea926c32a08a88d23dac97f6232875bde55041f2a49b
    - ngspice.log  sha256:83a33ff3f2a247157de0159e473b0bbae51bc87ff824fc783b1b15762dfe883a
    - report-unit.json  sha256:03be852501859ab9cc37e01f68557af7d30b77a7b116b4ef7b0e7409d8148873
wall_time: 1.826s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 4.024170e-03
- `droop_v_100um_b`: 8.089638e-02
- `droop_v_200um_a`: 2.010692e-03
- `droop_v_200um_b`: 3.987826e-02
- `droop_v_400um_a`: 1.004999e-03
- `droop_v_400um_b`: 1.980155e-02
- `droop_v_800um_a`: 5.024124e-04
- `droop_v_800um_b`: 9.866964e-03
- `ron_ohm_100um_a`: 4.161500e+01
- `ron_ohm_100um_b`: 4.273448e+01
- `ron_ohm_200um_a`: 2.079309e+01
- `ron_ohm_200um_b`: 2.106617e+01
- `ron_ohm_400um_a`: 1.039295e+01
- `ron_ohm_400um_b`: 1.046041e+01
- `ron_ohm_800um_a`: 5.195578e+00
- `ron_ohm_800um_b`: 5.212342e+00
- `p_loss_w_100um_a`: 3.891373e-07
- `p_loss_w_100um_b`: 1.531368e-04
- `p_loss_w_200um_a`: 1.944339e-07
- `p_loss_w_200um_b`: 7.548954e-05
- `p_loss_w_400um_a`: 9.718336e-08
- `p_loss_w_400um_b`: 3.748434e-05
- `p_loss_w_800um_a`: 4.858328e-08
- `p_loss_w_800um_b`: 1.867816e-05
- `ileak_a_100um`: 3.657419e-11
- `ileak_a_200um`: 7.314838e-11
- `ileak_a_400um`: 1.462968e-10
- `ileak_a_800um`: 2.925935e-10
- `i_stack_a`: 8.518790e-11
- `v_stack_v`: 1.183892e+00
- `i_ungated_a`: 2.350803e-10
- `stack_reduction_x`: 2.759551e+00
- `ipk_a_50pf_10ns`: 3.483254e-02
- `t_settle_s_50pf_10ns`: 8.329570e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 6.511476e-02
- `t_settle_s_200pf_10ns`: 1.417382e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.341568e-03
- `t_settle_s_50pf_1000ns`: 3.664434e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 5.706895e-03
- `t_settle_s_200pf_1000ns`: 4.263495e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 10.46 ohm on-resistance at the 20 MHz bound load, leaks 0.146 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.085 nA (ungated reference 0.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/-40/3.30   # single-point probe
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
