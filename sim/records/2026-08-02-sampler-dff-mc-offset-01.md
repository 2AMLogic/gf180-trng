---
record: 2026-08-02-sampler-dff-mc-offset-01
date: 2026-08-02T02:12:54Z
status: superseded
superseded_by: 2026-08-17-sampler-dff-mc-offset-03
supersedes: 2026-08-01-sampler-dff-mc-offset-01 -- the DUT changed under it: #59 (DR-0014-sampler-reset-gated-into-the-storage-loops) replaced sampler_dff's reset structure, so the master latch's first inversion is now a reset-gated NAND2 with a width-compensated NMOS stack rather than a plain 0.44u/0.22u inverter. Same testbench, same 30 seeds, re-run against the shipped netlist (design/sampler_core.spice, sha 50bc082).

testbench:
  path: sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset.sp
  sha: 46d3dc9260921310f9427bb66b83663ac1e83bb4
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: 7afc624c35d1862a39acbcf5a4d297162b6cfc8b-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: statistical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: mc
  tstop: n/a (op-point analysis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 30
seeds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

raw:
  path: sim/records/raw/2026-08-02-sampler-dff-mc-offset-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:298718f2b8ddaf60b00510fd5fa51775831d9eafe781d510ae89a83331cf460a
    - tt_27c_3.30v-run0.log  sha256:44ef9261e4a0b0a10a693114dab2fba083b197ec4fbd4e60dff67d79cb68428e
    - tt_27c_3.30v-run1.spice  sha256:1e02c0b434619b35da6475bcc93ea7f20aa85f427b7e6012e30bd5f19d9dbca6
    - tt_27c_3.30v-run1.log  sha256:935705b61ee1622bbaa8796de78f94082bb45d533f9c2eff2d85589486a31db3
    - tt_27c_3.30v-run2.spice  sha256:35bda9f5189385343db344c086b2c31da0eacff8c2566c3e760ccb95bd03b6dc
    - tt_27c_3.30v-run2.log  sha256:0fa761a5e3231be08d11e85fb95d123486a393f60558e3d894df3c839edbc2e3
    - tt_27c_3.30v-run3.spice  sha256:a8d845ba28f1da12646b52faae20e033f7948d213bd4ebca582c1e99ab61c8ea
    - tt_27c_3.30v-run3.log  sha256:ea34f7ac5806ac78f3681f4866c7ced9001fdbc82fdb93e38193e2b4701a0502
    - tt_27c_3.30v-run4.spice  sha256:1312501d5e6e79aba65903d8762402eb407fdd36b8fd05bd4932886996bb0319
    - tt_27c_3.30v-run4.log  sha256:d2dafe38a11daaed6feab4f7c701f5d51954d6c060ff7dacf36dc2b6640454a8
    - tt_27c_3.30v-run5.spice  sha256:eb63d32eba5870b097129bc12c3cf743498a22c44427326adffb7f64b6ad0e2c
    - tt_27c_3.30v-run5.log  sha256:3589bb3ed4ec2282a29bbccb9d354300ed42f9c41baf21c42a57ceb15e525a22
    - tt_27c_3.30v-run6.spice  sha256:09ed929765996d3c620d8768a70f776325862778e5a217e39080fa72464c78a3
    - tt_27c_3.30v-run6.log  sha256:d014d3f9dfebf3a644dea3b03858c0104420a1ff27072703e6404a1954820041
    - tt_27c_3.30v-run7.spice  sha256:7bd3f10a0355a16a1414893e878c83f574ccaf3e1bdb33034c94d2231b2d1abd
    - tt_27c_3.30v-run7.log  sha256:c0250938a7a1206e2e83c9e6c5b9479022d7b70b127465b238f9ae62f92a22dd
    - tt_27c_3.30v-run8.spice  sha256:9561b61f11641afa10f82c7c8e765dce9512d82750da13b265fea9126adf9c48
    - tt_27c_3.30v-run8.log  sha256:ba9ceb006966d8b920b790a41f81a6b99cf29265be5c9051de6a4aecf53fd823
    - tt_27c_3.30v-run9.spice  sha256:bfc73594b4d950b1f7b23b138bc96dd72b5aac7590d496c913c6b14c4ffc77a8
    - tt_27c_3.30v-run9.log  sha256:3a746e70e8e2c2231e0efa41c16619fc3f16371b47461ced75d664f307277358
    - tt_27c_3.30v-run10.spice  sha256:239c9c80bf8726f1b7ee714c2fe9214f14a7d600017d52fe674055c0d08af93e
    - tt_27c_3.30v-run10.log  sha256:f6d3e5c95641193292ac7c57e46ee44da62eb6a1451532d3edceb5d7dd38c703
    - tt_27c_3.30v-run11.spice  sha256:60e4d46e4c87b6a71058d1f20ea6351a8afcef3a279358c37f30781ccceab121
    - tt_27c_3.30v-run11.log  sha256:863bfd299c83e10fcf810638db2906e5e0c69236c12c53490032b781b6ac1913
    - tt_27c_3.30v-run12.spice  sha256:4dc13965c9bb606d8d6a9924e30f4129ecee635810b30401c1c18e8f0455aefd
    - tt_27c_3.30v-run12.log  sha256:95a519c503c17f63b246803f6473de42b2136a94e8891479c9a65357a80907da
    - tt_27c_3.30v-run13.spice  sha256:787501afae095660f4de4e95441c920e3f0dd265dbddc6f6758781ef60789379
    - tt_27c_3.30v-run13.log  sha256:f285f64b8b0a6230ee11160a35929851b23d79601480f3dad27d0a287649d185
    - tt_27c_3.30v-run14.spice  sha256:1c7930eed0cd3a1ead138fa6f9b6e1a721e2c69bb74e523e5e575880fae2fb7b
    - tt_27c_3.30v-run14.log  sha256:a74c602e8e95ede1e094b824bd88c97679568a659f8a1f7b74f5186a312b1484
    - tt_27c_3.30v-run15.spice  sha256:dc4517d257ec0b237202f4868e2d4c60a87a484e5401adcaaf0cf15f6f32267d
    - tt_27c_3.30v-run15.log  sha256:7adcce745414564d78866061f4be01599822bbc9c156401d9f75a7b063f57139
    - tt_27c_3.30v-run16.spice  sha256:db623859b9b659d5edb32f6ee46989b647097ab9eb7343afb5e712151faa19b3
    - tt_27c_3.30v-run16.log  sha256:67264e09743b60f9df60c45dc0d049804473119ad2201281b7726b30c1e5e3f9
    - tt_27c_3.30v-run17.spice  sha256:34f21303c4d2c344a323dddab62ccdd1d8ceef4bf1b76fc25f641e3bce855484
    - tt_27c_3.30v-run17.log  sha256:a3ee8f23ddf3c5283c4dd9e7501200ac76e989c02c3923db6039cc0e7175c779
    - tt_27c_3.30v-run18.spice  sha256:ff0974043d13bb14e8a85cf2071528b54d2cb2828e0abd6dcc06844fe6c27039
    - tt_27c_3.30v-run18.log  sha256:749e97481c3fb362df2477eefb33fd6d05e90a578808d53c2ae53e0e68a1d654
    - tt_27c_3.30v-run19.spice  sha256:7c26109b3aca965b2f12a574c70bea569e158b6357efc591126257f4fb72fc71
    - tt_27c_3.30v-run19.log  sha256:c362c2b1a83ab955701b9d1696ffb75bf065c8f3a434ccbd4f3dc28d44669f1e
    - tt_27c_3.30v-run20.spice  sha256:58ce6834341e25de75e9b99716e5fa2c9457cfd131cf692ea335253140c12fde
    - tt_27c_3.30v-run20.log  sha256:aac537c0572039375bfa97b1a68c3eb4eb6873693749ff4b12795d900fc57a43
    - tt_27c_3.30v-run21.spice  sha256:f0c816830bfb2625c7d151dc62b72056485b0da415705ecfe371664eb3f36fc6
    - tt_27c_3.30v-run21.log  sha256:19a5ffa0c000125d9b05cd120994df54dc5ecff898a36e64bc0e49158b6944e1
    - tt_27c_3.30v-run22.spice  sha256:a516b51e5fafd67c80a7604a46e88259d2574656b86291fa6f3f5719a6c58ecd
    - tt_27c_3.30v-run22.log  sha256:3683b02089e65fd90e91ac2be68d3280aaf6d4640e61a79b1a7e2f3218ccc4b4
    - tt_27c_3.30v-run23.spice  sha256:06cce2995336cc6cb168b07d97bf14edb78a7c7965cd8eb1ee42211c06f21e26
    - tt_27c_3.30v-run23.log  sha256:bb97b75dcfc3f73367a050ae52ec703e085b7bfbb8b4d8fd4d887caf671d3763
    - tt_27c_3.30v-run24.spice  sha256:b0ef32bc7bbe214d265d7967d649ffadca64b416c59925d0bc976adeb3ae50df
    - tt_27c_3.30v-run24.log  sha256:1d72b211125bf48b6db53bba7d4b951204b12dfa4f05c5cbac47a19c26e753f6
    - tt_27c_3.30v-run25.spice  sha256:3618d4d12b19aaa8e7ff9cea079c6db8cdea58cbd5a4da87b70bc6586ab977c1
    - tt_27c_3.30v-run25.log  sha256:02659930ef9258a45830740a73e9d4d7a04174cb23f06eee6916a1c383218b64
    - tt_27c_3.30v-run26.spice  sha256:31d9e22b7afc288d65e8c05aefb898bb47b5a2508d8ea7356f0da345ed88b01a
    - tt_27c_3.30v-run26.log  sha256:db3710458abccd97e3d3c3c3655669aefa0e2146c5379c5320b7f4d200206132
    - tt_27c_3.30v-run27.spice  sha256:5e04c91312ee030edb3a041e16aeb4f884a6de4b4cf431136efe4e465af2cd12
    - tt_27c_3.30v-run27.log  sha256:6e4df89eaa8a436516f5d6c21b96dbaf8a4fb5d4d894c7aa03f5ee5a0c22272d
    - tt_27c_3.30v-run28.spice  sha256:0ffb616804770fb96bdc246a8a2ba92a9396f9ad7a85f43bf7d5cdb39b3f7897
    - tt_27c_3.30v-run28.log  sha256:609864e8cfdc56cff0f00a321efdd61cdf4da19b37c6174bf0c97bb80e2c6897
    - tt_27c_3.30v-run29.spice  sha256:4578f9d860a7976bcd19eafd8f52c9963f9c0120651d182d225d776235147181
    - tt_27c_3.30v-run29.log  sha256:458910647c05106d9965d9ceb8ed33354e6715567b24a3aa4d48c2aea23b2231
wall_time: 3.6m
---

## Result

- `dtrip_v`: mean 1.38304 over 30 seeds (sd 0.0168757, 1.2% of mean; min 1.35637, max 1.43545)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 8 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 9 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 10 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 11 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 12 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 13 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 14 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 15 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 16 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 17 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 18 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 19 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 20 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 21 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 22 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 23 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 24 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 25 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 26 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 27 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 28 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 29 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 30 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- corner.process (tt) is bookkeeping only for this testbench -- the actually-loaded model section is statistical (see pdk.models), which replaces the plain per-family corner sections.
- Nominal corner only (tt/27C/3.30V) -- see this testbench's own header for why, and sim/tb/ro-array-core-mc-freq/'s header for the identical rationale restated in the RO context.
- The dc sweep bounds (0-3.3V) and the mid-supply comparison value (1.65) in this manifest's `analyses`/`measure` are hardcoded numeric literals, not vdd_val-parameterized expressions: ngspice's control-block `dc`/`meas dc` commands rejected a parenthesized `vdd_val`-derived increment during this testbench's bring-up. Harmless only because this testbench is pinned to the single 3.30 V nominal point above -- re-parameterize before ever sweeping this testbench's voltage axis.
- Measures the MASTER LATCH's own decision threshold (node xdut.mb) with clk held at 0 throughout, not a full clocked capture. It says nothing about clk-to-Q delay, setup/hold margin or metastable resolution time -- those are sim/tb/sampler-dff-setup-hold/'s job, unchanged by this run.
- The .dc sweep is quasi-static (no dV/dt): it measures the offset of the STATIC switching threshold, not a dynamic one. Converting it to a raw-bit-probability bias (issue #13's own analysis) additionally assumes the real XOR node's crossing is fast enough, and its slew rate near mid-supply steady enough, that the static and dynamic thresholds coincide to first order -- a modeling assumption stated once here rather than re-derived per record.
- 30 mismatch seeds characterizes the offset distribution's rough mean and spread, not a tail probability.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
