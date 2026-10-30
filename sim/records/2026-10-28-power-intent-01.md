---
record: 2026-10-28-power-intent-01
date: 2026-10-28T06:40:13Z
status: valid

level: gate-simulation, functional and zero-delay (the netlist is the synthesized design/trng_top/trng_top.synth.v; power is a behavioural model, not a device model)

testbench:
  path: sim/tb/power-intent/tb_power_intent.v
  sha: 32fe7bf62eecc84e4f581d4f85fd2433dc9dc712
netlist:
  path: design/trng_top/trng_top.synth.v
  sha: 3ac16fe5bbdf4f0365b1b30b753866090a5bbd8b
  note: >-
    Synthesized trng_top with its flip-flops swapped for the power-aware
    models in sim/tb/power-intent/pi_cells.v by sim/tools/power_intent_check.py;
    combinational cells are the PDK's own functional models
    (gf180mcu_fd_sc_mcu9t5v0, -DFUNCTIONAL).
repo_commit: 18d24d110c54ae2309dcd6694ec581798a7e1c62-dirty

pdk: n/a (behavioral-level record -- no device models are instantiated, per DR-0009)
pdk.models:
  - n/a (behavioral-level record)

tool:
  ngspice: "n/a (behavioral-level record -- ngspice is not invoked)"
  python: "3.12.3 (CPython)"
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

corner:
  process: n/a (behavioral-level record -- no device models, so no process corner exists; DR-0009 forbids citing this record for any P/V/T-dependent claim)
  voltage: n/a (behavioral-level record)
  temperature: n/a (behavioral-level record)

analysis:
  type: gate-level functional power-down/power-up (zero delay)
  tstop: 35 control edges; see gate_level.log
  tstep: n/a
  tmax: n/a
  noise_params: n/a (digital)
  runs: 1
seeds: tb.seed = 0x1234abcd ($random)

raw:
  path: sim/records/raw/2026-10-28-power-intent-01/
  files:
    - gate_level.log  sha256:48aa111076570f6067ec2ee860d77527a3799ab0d6b3fce01ad1bdd6fdceb95e
    - summary.json  sha256:0e27967cfea71eaf3fe028e1a329c57aafd8a49e08fd86aa14da0e24a1937eb1
wall_time: 0.0s
---

## Result

- Gate-level run of the synthesized `trng_top` across power-down and power-up
  (cold boot, a power cycle with a register read pending, a power cycle with a
  latched health-test alarm, and a back-to-back down/up):
  **10 scenario checks passed, 0 failed;
  0 X/clamp violations; 0 sequencing violations.**
- No X on any of the 66 always-on-visible output bits
  while off (all held at the clamp value 0), and no X on any of them after
  wake; sampled every clock.
- Flops: 5 retained (always-on rail), 315 gated.
- Wake latency 27 sample-clock cycles
  (13.50 ms at the ratified raw rate) on top of the
  640.5 ms digital start-up total:
  **654.0 ms** wake-to-first-valid, **provisional**
  (rail settle and decay are placeholders until #707 lands).

Deliberately broken fixtures, each of which must be (and was) reported:

| Fixture | Reported | Required |
|---|---|---|
| `no_iso` | unisolated_output | unisolated_output |
| `iso_early` | iso_release_before_rail_good, x_on_visible_output | iso_release_before_rail_good, x_on_visible_output |
| `reset_early` | reset_release_before_iso_release | reset_release_before_iso_release |
| `ret_lost` | CHECK:alarm_pin_survives, CHECK:alarm_set_pre_down, CHECK:alarm_survives_power_cycle, CHECK:ctrl_retained, CHECK:ctrl_retained_back_to_back, CHECK:ctrl_retained_with_alarm, CHECK:pre_down_cond_ready, CHECK:startup_rerun, CHECK:state_reinitialised, x_on_visible_output | CHECK:ctrl_retained |
| `ret_clk_on` | CHECK:alarm_pin_survives, CHECK:alarm_set_pre_down, CHECK:alarm_survives_power_cycle, CHECK:pre_down_cond_ready, CHECK:startup_rerun, CHECK:state_reinitialised, missing_step, x_on_visible_output | missing_step, x_on_visible_output |
| `no_decay_wait` | wake_inside_decay | wake_inside_decay |

## How to reproduce

```sh
python3 sim/tools/power_intent_check.py --check --require-tools
python3 sim/tools/power_intent_check.py --variant no_iso   # exits 1
```

## Caveats

- **No P/V/T corner.** This is a zero-delay functional simulation: it says
  nothing about leakage, switch resistance, rail settling, inrush, timing or
  any other PVT-dependent claim, and must not be cited for one. The rail model
  is two delays that are placeholders for #707's evidence.
- The power-down model is behavioural: gated flops go X and gated outputs go X
  when the rail is low. It does not model sneak paths, input-side protection
  or a partially collapsed rail.
- Only the output crossings are checked. Inputs driven into the unpowered
  domain are an open item recorded in `design/power-intent.md`.
- The retention scheme (clock-gated always-on flops) is not integrated into the
  shipped RTL, netlist or layout; the netlist here is a derived copy.

Written by `sim/tools/power_intent_check.py --write-record`. Append-only: never
edit or delete this file.
