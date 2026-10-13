---
record: 2026-10-10-sampler-array-fs-sf-02
date: 2026-10-10T08:13:21Z
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
  process: fs, sf (two units)
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: -40

analysis:
  type: tran (deterministic; no noise, no mismatch)
  tstop: 3620n
  tstep: 10p (print step; also tmax)
  runs: 2 units, one clock phase (vph = 0)
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-10-sampler-array-fs-sf-02/
  files:
    - report.json  sha256:6e0a4f6c7cf595cea6d359395ebc4be2f137c7446d17f7a628f115946a8c6128
    - fs-corner.cir  sha256:b77c1e1a89a20128f8223d34d29f1e3a397932bd228c6e54e61af8c9c9e8d339
    - fs-ngspice.log  sha256:a14d905005b82389b1a37335183a03ee1b389afb81e4749d4872f30768b0342e
    - sf-corner.cir  sha256:47a64dbcafcd84d1d88b12c9e4c687d232e6120d336e81418e23d1bed8a73441
    - sf-ngspice.log  sha256:dfc226d61ca839f43db60ffc34d9471e766f96b5e271924ecd1ba8a7fd4b0e2d
wall_time: 4m05s for 2 units
---

## Result

**A two-unit local pilot, not the campaign.** Two single-unit debug probes
(`klt sim --backend local`, one request holding both) of the committed deck, at
the cold, low-supply corner of each asymmetric process, one clock phase (0 ns).
They establish that the deck starts both rings without a noise source at `fs` and
`sf`, that the `.meas` rows and the checker work on real output, and the runtime
(about 2 minutes per unit). **2 of the 18 asymmetric PVT points were measured, at
1 of 4 phases; 16 PVT points and 3 of 4 phases at these two are UNMEASURED**
(see `2026-10-10-sampler-array-fs-sf-01` for why the batch fleet did not run).
The checker's coverage floor (6 decisive post-release samples per PVT point) is
not met by one unit, so neither point is a coverage-complete verdict.

### fs / -40 C / 2.97 V / clock phase 0 ns / vrel 5e-07 s / vthw 5e-07 s

- verdict (checker): **FLAGGED**; runtime 124 s; klt status `pass`
- ring1: period 5.965 ns, high 3.136 ns, low 2.829 ns, duty 0.5258, swing 3.059 V
- ring2: period 5.567 ns, high 2.927 ns, low 2.640 ns, duty 0.5258, swing 3.020 V
- xo: swing 3.090 V; high pulses 164 ps - 5.36 ns (n=24), low pulses 79 ps - 5.60 ns (n=23); shortest 79 ps

| edge | clock mid-crossing (us) | xo at 25/50/80 % clock (V) | sample | raw_bit +8/+50/+300 ns (V) | raw_valid +8/+50/+300 ns (V) |
|---|---|---|---|---|---|
| 0 | 0.3005 | n/a | under reset | 1.24e-07/1.49e-08/7.76e-09 | 3.06e-08/1.59e-08/1.62e-08 |
| 1 | 1.3005 | 2.990/2.971/2.969 | decisive (xo 1, captured 1) | 2.97/2.97/2.97 | 2.97/2.97/2.97 |
| 2 | 2.3005 | 2.989/2.980/0.010 | in aperture | 2.97/2.97/2.97 | 2.97/2.97/2.97 |
| 3 | 3.3005 | 3.001/1.787/2.956 | in aperture | 2.97/2.97/2.97 | 2.97/2.97/2.97 |

- checker failures: none
- informational flags: xo pulse 79 ps < 140 ps

### sf / -40 C / 2.97 V / clock phase 0 ns / vrel 5e-07 s / vthw 5e-07 s

- verdict (checker): **FLAGGED**; runtime 121 s; klt status `pass`
- ring1: period 5.967 ns, high 3.164 ns, low 2.803 ns, duty 0.5302, swing 3.072 V
- ring2: period 5.589 ns, high 2.968 ns, low 2.621 ns, duty 0.5311, swing 3.012 V
- xo: swing 3.089 V; high pulses 82 ps - 8.22 ns (n=24), low pulses 93 ps - 5.63 ns (n=23); shortest 82 ps

| edge | clock mid-crossing (us) | xo at 25/50/80 % clock (V) | sample | raw_bit +8/+50/+300 ns (V) | raw_valid +8/+50/+300 ns (V) |
|---|---|---|---|---|---|
| 0 | 0.3005 | n/a | under reset | 6.01e-08/1.31e-06/1.57e-08 | 3.61e-08/1.77e-08/1.49e-08 |
| 1 | 1.3005 | 2.983/0.641/0.001 | in aperture | 2.97/2.97/2.97 | 2.97/2.97/2.97 |
| 2 | 2.3005 | 0.004/-0.005/0.000 | decisive (xo 0, captured 0) | 7.95e-07/2.62e-07/8.95e-08 | 2.97/2.97/2.97 |
| 3 | 3.3005 | 2.987/2.985/2.975 | decisive (xo 1, captured 1) | 2.97/2.97/2.97 | 2.97/2.97/2.97 |

- checker failures: none
- informational flags: xo pulse 82 ps < 140 ps

Reading the numbers, with their limits:

- Both rings start and run without noise at `fs` and `sf`, -40 C, 2.97 V.
- Ring duty cycle is 0.526 / 0.526 (fs) and 0.530 / 0.531 (sf); the tt/27 C/3.30 V
  probe in `-03` measures 0.528 / 0.528 (a different temperature and supply, so
  it is not a like-for-like control). The buffered ring outputs show no large
  asymmetric duty skew at these two points.
- Every sample resolved to a rail within the checker's tolerances and raw_valid
  behaved as the contract requires; every decisive sample captured the level xo
  had at the edge. Three of the six post-release samples were in the edge
  aperture (xo crossing mid-supply during the clock edge) and were checked for
  resolution only.
- The XOR output carries pulses as short as ~80 ps (ring beat glitches), below
  the 140 ps informational threshold; they were not on a clock edge here. That
  is a flag, not a capture failure.
- No claim about the other 16 PVT points, the other three phases, or the tt control.

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
