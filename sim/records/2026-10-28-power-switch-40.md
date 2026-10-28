---
record: 2026-10-28-power-switch-40
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
  path: sim/records/raw/2026-10-28-power-switch-40/
  files:
    - corner.cir  sha256:730ba0b2a9c8a1a9057a4270422998ee192d2bbcad73fd0269200ee6ebd36852
    - ngspice.log  sha256:105f3b06bc03fa570c756709b77b6c07c9d50a493a3826db746011fa15c424e6
    - report-unit.json  sha256:f26c183e5fc90241cff1e3af4b74f62bb534e42b3dd754368dc862d9929c1ad5
wall_time: 1.883s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.338837e-03
- `droop_v_100um_b`: 6.665870e-02
- `droop_v_200um_a`: 1.668556e-03
- `droop_v_200um_b`: 3.298220e-02
- `droop_v_400um_a`: 8.340625e-04
- `droop_v_400um_b`: 1.640654e-02
- `droop_v_800um_a`: 4.169774e-04
- `droop_v_800um_b`: 8.182397e-03
- `ron_ohm_100um_a`: 3.452779e+01
- `ron_ohm_100um_b`: 3.521326e+01
- `ron_ohm_200um_a`: 1.725497e+01
- `ron_ohm_200um_b`: 1.742324e+01
- `ron_ohm_400um_a`: 8.625258e+00
- `ron_ohm_400um_b`: 8.666951e+00
- `ron_ohm_800um_a`: 4.312072e+00
- `ron_ohm_800um_b`: 4.322450e+00
- `p_loss_w_100um_a`: 3.228655e-07
- `p_loss_w_100um_b`: 1.261849e-04
- `p_loss_w_200um_a`: 1.613493e-07
- `p_loss_w_200um_b`: 6.243531e-05
- `p_loss_w_400um_a`: 8.065384e-08
- `p_loss_w_400um_b`: 3.105758e-05
- `p_loss_w_800um_a`: 4.032172e-08
- `p_loss_w_800um_b`: 1.548928e-05
- `ileak_a_100um`: 4.117011e-11
- `ileak_a_200um`: 8.234021e-11
- `ileak_a_400um`: 1.646804e-10
- `ileak_a_800um`: 3.293608e-10
- `i_stack_a`: 8.476105e-11
- `v_stack_v`: 1.184958e+00
- `i_ungated_a`: 2.351397e-10
- `stack_reduction_x`: 2.774147e+00
- `ipk_a_50pf_10ns`: 3.782326e-02
- `t_settle_s_50pf_10ns`: 7.237654e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 7.108096e-02
- `t_settle_s_200pf_10ns`: 1.228061e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.474547e-03
- `t_settle_s_50pf_1000ns`: 2.952922e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 6.107355e-03
- `t_settle_s_200pf_1000ns`: 3.506217e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 8.67 ohm on-resistance at the 20 MHz bound load, leaks 0.165 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.085 nA (ungated reference 0.2 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only sf/-40/3.30   # single-point probe
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
