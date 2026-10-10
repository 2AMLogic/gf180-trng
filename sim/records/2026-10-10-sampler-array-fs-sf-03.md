---
record: 2026-10-10-sampler-array-fs-sf-03
date: 2026-10-10T08:17:40Z
status: valid

testbench:
  path: sim/tb/sampler-array-fs-sf/tb_sampler_array_fs_sf.sp
  sha: c5dbf2351cb172a88bb46229d645e2a8ef628f12
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: cfef09511d819642ac66dcdb05c0a0ca1249eabc-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - ~/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sha256:6edba54d23b38a2c60f8ffdbaa3eb75a7568c615e4820808969bd1121b77b1aa)
tool:
  ngspice: "ngspice-42"
  klt: 0.7.0+g8eec069c7576 (--backend local)
  platform: Linux-7.0.0-1013-aws-x86_64-with-glibc2.39

corner:
  process: tt
  voltage: 3.300 V (nominal)
  temperature: 27

analysis:
  type: tran (deterministic; no noise, no mismatch)
  tstop: 3620n
  tstep: 10p (print step; also tmax)
  runs: 2 units, negative controls (vrel = 1 s; vthw = 20 ps)
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-10-sampler-array-fs-sf-03/
  files:
    - report.json  sha256:5715e37d96646432b02e2426ebf8147c542e130bb0ad9a095b7884a8bf56d757
    - reset-never-released-corner.cir  sha256:3e169d01d15c1808d56fd11512a0fe66c7554b53e3e42896b4ae2cac1bf9c5db
    - reset-never-released-ngspice.log  sha256:6bd4224825a8cba6db2444900d80b48b468b7888e84224ca893744296242d875
    - clock-high-20ps-corner.cir  sha256:3c5735fb5c5ec747ebb3e114562a631f24c8890a7790ad6663edec2fffe8540d
    - clock-high-20ps-ngspice.log  sha256:3dca0e63c3cf719a1c230ac4079abd4d4ab6f967c278be74bc1df14bde3c7651
wall_time: 4m00s for 2 units
---

## Result

**Negative-control probe: the checker caught both intentionally invalid
stimuli.** Two single-unit debug probes (`klt sim --backend local`, one request
holding both) at tt / 27 C / 3.30 V, clock phase 0:

- `reset-never-released` (`vrel` = 1 s): the checker returned `FUNCTIONAL_MISS`
  (raw_valid never rises after the post-reset edges);
- `clock-high-20ps` (`vthw` = 20 ps): the checker returned `FUNCTIONAL_MISS`
  (no mid-supply clock crossing exists; raw_valid never rises).

Neither is a measurement of the design: they show only that a stimulus or an
unresolved output that the contract forbids does not read as a pass. The
rings do not depend on the clock or reset, so these two units also yield the
**tt / 27 C / 3.30 V ring and XOR waveform** (duty, swing, pulse widths) below. The
tt *capture* control (valid reset release, normal clock, four phases) is
**UNMEASURED** -- it is the `control-tt` request's first four units, which the batch
fleet did not run (`-01`).

### tt / 27 C / 3.30 V / clock phase 0 ns / vrel 1 s / vthw 5e-07 s

- verdict (checker): **FUNCTIONAL_MISS**; runtime 119 s; klt status `pass`
- ring1: period 6.667 ns, high 3.519 ns, low 3.148 ns, duty 0.5278, swing 3.409 V
- ring2: period 6.231 ns, high 3.291 ns, low 2.940 ns, duty 0.5282, swing 3.345 V
- xo: swing 3.398 V; high pulses 60 ps - 5.95 ns (n=24), low pulses 217 ps - 6.19 ns (n=23); shortest 60 ps

| edge | clock mid-crossing (us) | xo at 25/50/80 % clock (V) | sample | raw_bit +8/+50/+300 ns (V) | raw_valid +8/+50/+300 ns (V) |
|---|---|---|---|---|---|
| 0 | 0.3005 | n/a | under reset | 4.28e-08/2.08e-08/1.84e-08 | 4.19e-08/2.07e-08/1.84e-08 |
| 1 | 1.3005 | 3.345/0.036/1.047 | in aperture | 5.52e-08/1.35e-06/8.18e-08 | 4.19e-08/2.07e-08/1.84e-08 |
| 2 | 2.3005 | 0.003/-0.010/2.615 | in aperture | 1.32e-06/2.14e-08/5.43e-07 | 3.6e-08/2.07e-08/1.84e-08 |
| 3 | 3.3005 | 3.307/3.157/3.292 | decisive (xo 1, captured 0) | 9.29e-07/2.26e-08/1.85e-08 | 4.18e-08/2.07e-08/1.84e-08 |

- checker failures: edge1: raw_valid 4.19e-08 V not high (+8 ns); edge1: raw_valid 2.07e-08 V not high (+50 ns); edge1: raw_valid 1.84e-08 V not high (+300 ns); edge2: raw_valid 3.6e-08 V not high (+8 ns); edge2: raw_valid 2.07e-08 V not high (+50 ns); edge2: raw_valid 1.84e-08 V not high (+300 ns) ...
- informational flags: xo pulse 60 ps < 140 ps

### tt / 27 C / 3.30 V / clock phase 0 ns / vrel 5e-07 s / vthw 2e-11 s

- verdict (checker): **FUNCTIONAL_MISS**; runtime 121 s; klt status `error`
- ring1: period 6.667 ns, high 3.519 ns, low 3.148 ns, duty 0.5278, swing 3.409 V
- ring2: period 6.231 ns, high 3.291 ns, low 2.940 ns, duty 0.5282, swing 3.345 V
- xo: swing 3.398 V; high pulses 60 ps - 5.95 ns (n=24), low pulses 217 ps - 6.19 ns (n=23); shortest 60 ps

| edge | clock mid-crossing (us) | xo at 25/50/80 % clock (V) | sample | raw_bit +8/+50/+300 ns (V) | raw_valid +8/+50/+300 ns (V) |
|---|---|---|---|---|---|
| 0 | n/a | n/a | under reset | 1.85e-08/9.09e-09/8.46e-08 | 1.82e-08/1.84e-08/2e-08 |
| 1 | n/a | n/a | n/a | 1.96e-08/9.89e-07/3.49e-06 | 1.88e-08/1.85e-08/1.85e-08 |
| 2 | n/a | n/a | n/a | 1.88e-08/2.88e-06/7.42e-06 | 1.88e-08/1.85e-08/1.85e-08 |
| 3 | n/a | n/a | n/a | 2.15e-08/8.57e-06/3.38e-05 | 1.88e-08/1.85e-08/1.85e-08 |

- checker failures: edge0: no clock crossing measured; edge1: no clock crossing measured; edge1: raw_valid 1.88e-08 V not high (+8 ns); edge1: raw_valid 1.85e-08 V not high (+50 ns); edge1: raw_valid 1.85e-08 V not high (+300 ns); edge1: xo not measured at the clock edge ...
- informational flags: xo pulse 60 ps < 140 ps

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

The probes were run from a scratch copy of the deck whose only change is the
`.include` path made absolute (so the request could live outside the tree), with
`klt sim --backend local` and an **absolute** `-o` directory:

```sh
# from the repository root, after `python3 sim/tools/fs_sf_capture.py emit --check`
REPO=$(git rev-parse --show-toplevel)
mkdir -p /tmp/probe && cd /tmp/probe
sed "s#../../../design/sampler_core.spice#$REPO/design/sampler_core.spice#" \
    $REPO/sim/tb/sampler-array-fs-sf/tb_sampler_array_fs_sf.sp > deck.sp
# edit request-<name>.json: netlist -> deck.sp; keep only the units named above
klt sim /tmp/probe/req.json --backend local -o /tmp/probe/out --format json > report.json
python3 $REPO/sim/tools/fs_sf_capture.py analyze report.json
```

The `report.json` and per-unit `corner.cir` / `ngspice.log` committed alongside
are the raw output; `environment.netlist_sha256` in the report is the scratch
copy's hash (the repository deck's git blob hash is the `testbench.sha` above).
Each unit takes about 2 minutes on one dispatch worker.
