---
record: 2026-10-28-power-switch-20
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
  path: sim/records/raw/2026-10-28-power-switch-20/
  files:
    - corner.cir  sha256:a8f0ea3deae5776c6a916843f8fe1e042bbbbc9aab201610a0b521d09c1e8f97
    - ngspice.log  sha256:2938e74f50ad20b32634afff290ad7cb067fcbbfe289f3a050894bb6bd0ce0a6
    - report-unit.json  sha256:9d2a3b40b80a70e5cf8700af26630927073481528b32772586dd79cb7eb3f1ec
wall_time: 1.887s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.200436e-03
- `droop_v_100um_b`: 1.055496e-01
- `droop_v_200um_a`: 2.597800e-03
- `droop_v_200um_b`: 5.175914e-02
- `droop_v_400um_a`: 1.298297e-03
- `droop_v_400um_b`: 2.563787e-02
- `droop_v_800um_a`: 6.489979e-04
- `droop_v_800um_b`: 1.275993e-02
- `ron_ohm_100um_a`: 5.377907e+01
- `ron_ohm_100um_b`: 5.575787e+01
- `ron_ohm_200um_a`: 2.686453e+01
- `ron_ohm_200um_b`: 2.734239e+01
- `ron_ohm_400um_a`: 1.342603e+01
- `ron_ohm_400um_b`: 1.354351e+01
- `ron_ohm_800um_a`: 6.711457e+00
- `ron_ohm_800um_b`: 6.740588e+00
- `p_loss_w_100um_a`: 5.028822e-07
- `p_loss_w_100um_b`: 1.998055e-04
- `p_loss_w_200um_a`: 2.512073e-07
- `p_loss_w_200um_b`: 9.798005e-05
- `p_loss_w_400um_a`: 1.255453e-07
- `p_loss_w_400um_b`: 4.853249e-05
- `p_loss_w_800um_a`: 6.275810e-08
- `p_loss_w_800um_b`: 2.415455e-05
- `ileak_a_100um`: 3.071972e-11
- `ileak_a_200um`: 6.143943e-11
- `ileak_a_400um`: 1.228789e-10
- `ileak_a_800um`: 2.457577e-10
- `i_stack_a`: 7.876360e-11
- `v_stack_v`: 1.011173e+00
- `i_ungated_a`: 2.392364e-10
- `stack_reduction_x`: 3.037398e+00
- `ipk_a_50pf_10ns`: 2.834518e-02
- `t_settle_s_50pf_10ns`: 9.163110e-09
- `vfin_v_50pf_10ns`: 2.970000e+00
- `ipk_a_200pf_10ns`: 5.284277e-02
- `t_settle_s_200pf_10ns`: 1.643456e-08
- `vfin_v_200pf_10ns`: 2.970000e+00
- `ipk_a_50pf_1000ns`: 1.897127e-03
- `t_settle_s_50pf_1000ns`: 3.821817e-07
- `vfin_v_50pf_1000ns`: 2.970000e+00
- `ipk_a_200pf_1000ns`: 4.669785e-03
- `t_settle_s_200pf_1000ns`: 4.508660e-07
- `vfin_v_200pf_1000ns`: 2.970000e+00

At this corner the 400 um switch has 13.54 ohm on-resistance at the 20 MHz bound load, leaks 0.123 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.079 nA (ungated reference 0.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ss/27/2.97   # single-point probe
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
