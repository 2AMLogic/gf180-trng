---
record: 2026-10-28-power-switch-03
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
  - libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.8.1.dev511+gbbe05037064a (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: tt
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
  path: sim/records/raw/2026-10-28-power-switch-03/
  files:
    - corner.cir  sha256:28671ad85477541b0796b5925d225847f0e13baf877e954baa34fbdba5c3fe02
    - ngspice.log  sha256:6b062f871a230b5568115c3d7e22423ab3b0a6b19bf20b4e26e2bdd2f1fd103a
    - report-unit.json  sha256:0a3e27717f791ff09254f6449f3e94edb2834eb1b37a0061bab02de2127fb062
wall_time: 1.92s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.536132e-03
- `droop_v_100um_b`: 1.119271e-01
- `droop_v_200um_a`: 2.765761e-03
- `droop_v_200um_b`: 5.500288e-02
- `droop_v_400um_a`: 1.382305e-03
- `droop_v_400um_b`: 2.727184e-02
- `droop_v_800um_a`: 6.910090e-04
- `droop_v_800um_b`: 1.357976e-02
- `ron_ohm_100um_a`: 5.725059e+01
- `ron_ohm_100um_b`: 5.912683e+01
- `ron_ohm_200um_a`: 2.860145e+01
- `ron_ohm_200um_b`: 2.905593e+01
- `ron_ohm_400um_a`: 1.429478e+01
- `ron_ohm_400um_b`: 1.440668e+01
- `ron_ohm_800um_a`: 7.145905e+00
- `ron_ohm_800um_b`: 7.173669e+00
- `p_loss_w_100um_a`: 5.353439e-07
- `p_loss_w_100um_b`: 2.118780e-04
- `p_loss_w_200um_a`: 2.674490e-07
- `p_loss_w_200um_b`: 1.041204e-04
- `p_loss_w_400um_a`: 1.336689e-07
- `p_loss_w_400um_b`: 5.162559e-05
- `p_loss_w_800um_a`: 6.682057e-08
- `p_loss_w_800um_b`: 2.570648e-05
- `ileak_a_100um`: 7.219274e-10
- `ileak_a_200um`: 1.443855e-09
- `ileak_a_400um`: 2.887710e-09
- `ileak_a_800um`: 5.775419e-09
- `i_stack_a`: 2.880714e-09
- `v_stack_v`: 7.382295e-03
- `i_ungated_a`: 1.348743e-07
- `stack_reduction_x`: 4.681975e+01
- `ipk_a_50pf_10ns`: 3.735246e-02
- `t_settle_s_50pf_10ns`: 9.715816e-09
- `vfin_v_50pf_10ns`: 2.969998e+00
- `ipk_a_200pf_10ns`: 6.690860e-02
- `t_settle_s_200pf_10ns`: 1.912212e-08
- `vfin_v_200pf_10ns`: 2.969998e+00
- `ipk_a_50pf_1000ns`: 2.340418e-03
- `t_settle_s_50pf_1000ns`: 3.208134e-07
- `vfin_v_50pf_1000ns`: 2.969998e+00
- `ipk_a_200pf_1000ns`: 5.903360e-03
- `t_settle_s_200pf_1000ns`: 4.043834e-07
- `vfin_v_200pf_1000ns`: 2.969998e+00

At this corner the 400 um switch has 14.41 ohm on-resistance at the 20 MHz bound load, leaks 2.888 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 2.881 nA (ungated reference 134.9 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only tt/125/2.97   # single-point probe
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
