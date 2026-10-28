---
record: 2026-10-28-power-switch-13
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
  path: sim/records/raw/2026-10-28-power-switch-13/
  files:
    - corner.cir  sha256:ad77953d950a1534f1893c1426ae6b64f282d43c43739e437430c025f60c47a5
    - ngspice.log  sha256:382d489d1619f13f810c8313a5d2d13790bbca6fd02769ef6f578c5595e18e68
    - report-unit.json  sha256:089c6079bc643c4eff6d140b19c8f9d765a1f0bcbe78a3a7a83069c5931dacd3
wall_time: 1.869s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 3.229963e-03
- `droop_v_100um_b`: 6.442700e-02
- `droop_v_200um_a`: 1.614184e-03
- `droop_v_200um_b`: 3.189343e-02
- `droop_v_400um_a`: 8.068930e-04
- `droop_v_400um_b`: 1.586866e-02
- `droop_v_800um_a`: 4.033967e-04
- `droop_v_800um_b`: 7.915049e-03
- `ron_ohm_100um_a`: 3.340189e+01
- `ron_ohm_100um_b`: 3.403434e+01
- `ron_ohm_200um_a`: 1.669270e+01
- `ron_ohm_200um_b`: 1.684809e+01
- `ron_ohm_400um_a`: 8.344291e+00
- `ron_ohm_400um_b`: 8.382808e+00
- `ron_ohm_800um_a`: 4.171631e+00
- `ron_ohm_800um_b`: 4.181220e+00
- `p_loss_w_100um_a`: 3.123374e-07
- `p_loss_w_100um_b`: 1.219603e-04
- `p_loss_w_200um_a`: 1.560916e-07
- `p_loss_w_200um_b`: 6.037426e-05
- `p_loss_w_400um_a`: 7.802655e-08
- `p_loss_w_400um_b`: 3.003936e-05
- `p_loss_w_800um_a`: 3.900847e-08
- `p_loss_w_800um_b`: 1.498319e-05
- `ileak_a_100um`: 4.383128e-11
- `ileak_a_200um`: 8.766256e-11
- `ileak_a_400um`: 1.753251e-10
- `ileak_a_800um`: 3.506502e-10
- `i_stack_a`: 8.583979e-11
- `v_stack_v`: 1.156412e+00
- `i_ungated_a`: 2.748567e-10
- `stack_reduction_x`: 3.201973e+00
- `ipk_a_50pf_10ns`: 3.887876e-02
- `t_settle_s_50pf_10ns`: 7.080219e-09
- `vfin_v_50pf_10ns`: 3.300000e+00
- `ipk_a_200pf_10ns`: 7.306262e-02
- `t_settle_s_200pf_10ns`: 1.203983e-08
- `vfin_v_200pf_10ns`: 3.300000e+00
- `ipk_a_50pf_1000ns`: 2.528209e-03
- `t_settle_s_50pf_1000ns`: 2.846445e-07
- `vfin_v_50pf_1000ns`: 3.300000e+00
- `ipk_a_200pf_1000ns`: 6.254446e-03
- `t_settle_s_200pf_1000ns`: 3.393345e-07
- `vfin_v_200pf_1000ns`: 3.300000e+00

At this corner the 400 um switch has 8.38 ohm on-resistance at the 20 MHz bound load, leaks 0.175 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 0.086 nA (ungated reference 0.3 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/-40/3.30   # single-point probe
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
