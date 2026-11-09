---
record: 2026-10-28-power-switch-attempt-01
date: 2026-10-28T07:24:07Z
status: valid

testbench:
  path: sim/tb/power-switch/tb_power_switch.sp
  sha: b23081dbb36fd553e491f76dd08dfc235286cc2d
netlist:
  path: design/power_switch.spice
  sha: f14b87ff4bb74a439a5eb3cd5a2f6ffe3f616d44
repo_commit: 18d24d110c54ae2309dcd6694ec581798a7e1c62-dirty

tool:
  klt: 0.8.1.dev511+gbbe05037064a

raw:
  path: sim/records/raw/2026-10-28-power-switch-attempt-01/
  files:
    - report-errored.json  sha256:6a2a66a404ff3088c579ce946eef9e8c67e2a8c8f114b51900725aca01a54338
---

## Result

UNMEASURED: 45 unit(s) produced no usable readings; no number is claimed.

Attempt, not a measurement. All 45 units hit the 120 s per-unit timeout on the batch fleet (ngspice-46 workers): this deck runs in about 1.5 s on a local ngspice-42 and on the workers it did not finish in 120 s. The next run adds ngspice_init 'set num_threads=1' to the request and completes all 45 units; that points at ngspice threading on the workers (a 1 us run went from 6.2 s to 0.37 s with it), which was not isolated further. The workers' ngspice banner is in the raw report. The deck at the time of this attempt is the one committed; only the request differed.

---

Written by `sim/tools/power_switch.py record`. Append-only.
