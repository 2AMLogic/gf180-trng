---
record: 2026-10-28-power-switch-06
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-10-28-power-switch-06/
  files:
    - corner.cir  sha256:8c743eb565505b6fe44b58c1a305625bcd090c08757e62be2dae0e7746204035
    - ngspice.log  sha256:d338bb8d8bacb7a27f640e72cf99e3b2f9df8bd2270153d749ff6a1e1adb4252
    - report-unit.json  sha256:4748a5d253cdf006a191337447dbe85279e9eb3143c962425302d30a8f135a49
wall_time: 1.927s
---

## Result

Executed by batch fleet through klt sim (jobs klt-sim-88348d7ff6c8, klt-sim-1d495bf31dde, klt-sim-d4b75b4fbb20). Raw readings are taken at 2.9 us (static groups) and over the wake edge; the quantities below are `sim/tools/power_switch.py`'s arithmetic on them. Loads: a = 96.7 uA, b = 1.893 mA (deck header). Settling is the time from the start of the sleep fall to vvdd = 95 % of vdd.

- `droop_v_100um_a`: 5.133472e-03
- `droop_v_100um_b`: 1.031975e-01
- `droop_v_200um_a`: 2.564962e-03
- `droop_v_200um_b`: 5.087070e-02
- `droop_v_400um_a`: 1.282038e-03
- `droop_v_400um_b`: 2.525989e-02
- `droop_v_800um_a`: 6.409085e-04
- `droop_v_800um_b`: 1.258685e-02
- `ron_ohm_100um_a`: 5.308658e+01
- `ron_ohm_100um_b`: 5.451529e+01
- `ron_ohm_200um_a`: 2.652494e+01
- `ron_ohm_200um_b`: 2.687306e+01
- `ron_ohm_400um_a`: 1.325789e+01
- `ron_ohm_400um_b`: 1.334384e+01
- `ron_ohm_800um_a`: 6.627803e+00
- `ron_ohm_800um_b`: 6.649157e+00
- `p_loss_w_100um_a`: 4.964067e-07
- `p_loss_w_100um_b`: 1.953528e-04
- `p_loss_w_200um_a`: 2.480318e-07
- `p_loss_w_200um_b`: 9.629824e-05
- `p_loss_w_400um_a`: 1.239731e-07
- `p_loss_w_400um_b`: 4.781697e-05
- `p_loss_w_800um_a`: 6.197585e-08
- `p_loss_w_800um_b`: 2.382692e-05
- `ileak_a_100um`: 8.078471e-10
- `ileak_a_200um`: 1.615694e-09
- `ileak_a_400um`: 3.231388e-09
- `ileak_a_800um`: 6.462777e-09
- `i_stack_a`: 3.221816e-09
- `v_stack_v`: 8.323297e-03
- `i_ungated_a`: 1.687980e-07
- `stack_reduction_x`: 5.239219e+01
- `ipk_a_50pf_10ns`: 4.263958e-02
- `t_settle_s_50pf_10ns`: 9.273363e-09
- `vfin_v_50pf_10ns`: 3.299998e+00
- `ipk_a_200pf_10ns`: 7.911586e-02
- `t_settle_s_200pf_10ns`: 1.803980e-08
- `vfin_v_200pf_10ns`: 3.299998e+00
- `ipk_a_50pf_1000ns`: 2.698583e-03
- `t_settle_s_50pf_1000ns`: 2.966414e-07
- `vfin_v_50pf_1000ns`: 3.299998e+00
- `ipk_a_200pf_1000ns`: 6.767891e-03
- `t_settle_s_200pf_1000ns`: 3.771081e-07
- `vfin_v_200pf_1000ns`: 3.299998e+00

At this corner the 400 um switch has 13.34 ohm on-resistance at the 20 MHz bound load, leaks 3.231 nA off with the full supply across it, and with the leakage-equivalent digital load behind it the gated domain draws 3.222 nA (ungated reference 168.8 nA).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only tt/125/3.30   # single-point probe
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
