---
record: 2026-08-01-sampler-dff-mc-offset-01
date: 2026-08-01T23:03:22Z
status: superseded
superseded_by: 2026-08-02-sampler-dff-mc-offset-01

testbench:
  path: sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset.sp
  sha: 9f0136621801c85f642493936e1eccba5ce80866
netlist:
  path: design/sampler_core.spice
  sha: 127c7959d1940ae2898bc90a268c1b2caa40311e
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

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
  path: sim/records/raw/2026-08-01-sampler-dff-mc-offset-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:298718f2b8ddaf60b00510fd5fa51775831d9eafe781d510ae89a83331cf460a
    - tt_27c_3.30v-run0.log  sha256:96c7f5d5051ec390ddc2c8bb19da6183e621988dd4cf69de83771e84a592faa7
    - tt_27c_3.30v-run1.spice  sha256:1e02c0b434619b35da6475bcc93ea7f20aa85f427b7e6012e30bd5f19d9dbca6
    - tt_27c_3.30v-run1.log  sha256:64cfc886bffc2203bcee7bfcb39b37d28de98f041411f01d9611ef686bda3f8c
    - tt_27c_3.30v-run2.spice  sha256:35bda9f5189385343db344c086b2c31da0eacff8c2566c3e760ccb95bd03b6dc
    - tt_27c_3.30v-run2.log  sha256:a2a62dbac5bad2c511c0aaaf42162b452d4e61728e643f1eaa800b85d41283ac
    - tt_27c_3.30v-run3.spice  sha256:a8d845ba28f1da12646b52faae20e033f7948d213bd4ebca582c1e99ab61c8ea
    - tt_27c_3.30v-run3.log  sha256:3fd396dff06965ae6afa9c68c3f7bce2e79edcc837b94005ffa85a1d6c3c0a2d
    - tt_27c_3.30v-run4.spice  sha256:1312501d5e6e79aba65903d8762402eb407fdd36b8fd05bd4932886996bb0319
    - tt_27c_3.30v-run4.log  sha256:85b8f909bf77ff2409a70f86de6f0d0464928e3edc1d3f7101c9a6b6b81f8ccb
    - tt_27c_3.30v-run5.spice  sha256:eb63d32eba5870b097129bc12c3cf743498a22c44427326adffb7f64b6ad0e2c
    - tt_27c_3.30v-run5.log  sha256:44686d52859be72ba4b1939e25cc06eb9dd955adb12e2997859671579853a0fd
    - tt_27c_3.30v-run6.spice  sha256:09ed929765996d3c620d8768a70f776325862778e5a217e39080fa72464c78a3
    - tt_27c_3.30v-run6.log  sha256:f75fcd31f43bd49a1d5d6f2836999519a50bdbbebf4effeb48d125d5016989fa
    - tt_27c_3.30v-run7.spice  sha256:7bd3f10a0355a16a1414893e878c83f574ccaf3e1bdb33034c94d2231b2d1abd
    - tt_27c_3.30v-run7.log  sha256:5677ae6f860d93e5a6fea003b39098d7389c7657f66c8bb8744b4b57ddf95a07
    - tt_27c_3.30v-run8.spice  sha256:9561b61f11641afa10f82c7c8e765dce9512d82750da13b265fea9126adf9c48
    - tt_27c_3.30v-run8.log  sha256:2be9577a141d70c71de52a929c43c3df36505864d50853acbca2080424d851ab
    - tt_27c_3.30v-run9.spice  sha256:bfc73594b4d950b1f7b23b138bc96dd72b5aac7590d496c913c6b14c4ffc77a8
    - tt_27c_3.30v-run9.log  sha256:b4dfd7a067f2ca91220f534125058d9ede988304056064fe3c26d88f4382e675
    - tt_27c_3.30v-run10.spice  sha256:239c9c80bf8726f1b7ee714c2fe9214f14a7d600017d52fe674055c0d08af93e
    - tt_27c_3.30v-run10.log  sha256:0af31575e030d14ebd9fd76a5f82d723082b6a7e4c6ec1fd7d54e4a1a58043e6
    - tt_27c_3.30v-run11.spice  sha256:60e4d46e4c87b6a71058d1f20ea6351a8afcef3a279358c37f30781ccceab121
    - tt_27c_3.30v-run11.log  sha256:4b16345ea1f42c7d36e158d69962026ebb29aa30bbfb4684eff4c6519dc4ed2b
    - tt_27c_3.30v-run12.spice  sha256:4dc13965c9bb606d8d6a9924e30f4129ecee635810b30401c1c18e8f0455aefd
    - tt_27c_3.30v-run12.log  sha256:8e7e5b1817b6394c5ff2132db961b05b57ee2c67cacdd4dda3fd55d68415e1a4
    - tt_27c_3.30v-run13.spice  sha256:787501afae095660f4de4e95441c920e3f0dd265dbddc6f6758781ef60789379
    - tt_27c_3.30v-run13.log  sha256:bed2142f60dea267d1a97676a7b3ad045753e788e54cddee94f5a60ca5ca6359
    - tt_27c_3.30v-run14.spice  sha256:1c7930eed0cd3a1ead138fa6f9b6e1a721e2c69bb74e523e5e575880fae2fb7b
    - tt_27c_3.30v-run14.log  sha256:16e5a0e4893d4dec70ce3c63332c5ddf87fafbee6c7c5b87e2c88a44ff3be1c8
    - tt_27c_3.30v-run15.spice  sha256:dc4517d257ec0b237202f4868e2d4c60a87a484e5401adcaaf0cf15f6f32267d
    - tt_27c_3.30v-run15.log  sha256:d3aa95fde4c8135d47caaaa123d9bf29550bc19375fe3a6687b5e3e06ec55e50
    - tt_27c_3.30v-run16.spice  sha256:db623859b9b659d5edb32f6ee46989b647097ab9eb7343afb5e712151faa19b3
    - tt_27c_3.30v-run16.log  sha256:d569dde07467808ec81ca35cb304739e21d87e89525e02141397fc6339d6f7a4
    - tt_27c_3.30v-run17.spice  sha256:34f21303c4d2c344a323dddab62ccdd1d8ceef4bf1b76fc25f641e3bce855484
    - tt_27c_3.30v-run17.log  sha256:b981dd4acb1ddaed1b96ed18700d2fe01570e760769c62bae890d4c66abb438b
    - tt_27c_3.30v-run18.spice  sha256:ff0974043d13bb14e8a85cf2071528b54d2cb2828e0abd6dcc06844fe6c27039
    - tt_27c_3.30v-run18.log  sha256:8d90c3e1e59645d4eb38f9c9b420dee641bb98e95a192d68d3aeba2af2552393
    - tt_27c_3.30v-run19.spice  sha256:7c26109b3aca965b2f12a574c70bea569e158b6357efc591126257f4fb72fc71
    - tt_27c_3.30v-run19.log  sha256:f6e68bcd694b9bdc4832fd6485b73bc9a8fc9c362f6b1a6a88fc336884f92ac5
    - tt_27c_3.30v-run20.spice  sha256:58ce6834341e25de75e9b99716e5fa2c9457cfd131cf692ea335253140c12fde
    - tt_27c_3.30v-run20.log  sha256:a982eb91cee57f4eab70f62fb132c74a2ca3afd4808101e492a7b962c4007ea2
    - tt_27c_3.30v-run21.spice  sha256:f0c816830bfb2625c7d151dc62b72056485b0da415705ecfe371664eb3f36fc6
    - tt_27c_3.30v-run21.log  sha256:cc4eef3e307422589aa2cd82177ab9d2ab706f2b76c0130c0101eafbe140ff23
    - tt_27c_3.30v-run22.spice  sha256:a516b51e5fafd67c80a7604a46e88259d2574656b86291fa6f3f5719a6c58ecd
    - tt_27c_3.30v-run22.log  sha256:bf9739cdff3ea59f035d3737fba1965c5b2d01dee839d23e606127689cc2fa63
    - tt_27c_3.30v-run23.spice  sha256:06cce2995336cc6cb168b07d97bf14edb78a7c7965cd8eb1ee42211c06f21e26
    - tt_27c_3.30v-run23.log  sha256:df3ca928a02c000dc8c5d14302ce50d77f216d8101f6d396c9330dfc41fe224a
    - tt_27c_3.30v-run24.spice  sha256:b0ef32bc7bbe214d265d7967d649ffadca64b416c59925d0bc976adeb3ae50df
    - tt_27c_3.30v-run24.log  sha256:95f6b61e699ab02b2ab35bb9c6e8bec6fc07382c9df1d84715adddcfd2a5ba40
    - tt_27c_3.30v-run25.spice  sha256:3618d4d12b19aaa8e7ff9cea079c6db8cdea58cbd5a4da87b70bc6586ab977c1
    - tt_27c_3.30v-run25.log  sha256:a184ba0a31c924cdb1e3675884f178c73b79e2b819a128a48b842ff47cbf8527
    - tt_27c_3.30v-run26.spice  sha256:31d9e22b7afc288d65e8c05aefb898bb47b5a2508d8ea7356f0da345ed88b01a
    - tt_27c_3.30v-run26.log  sha256:3471c70edfd4933fe4d5c5172f34f3fd77c990404c641048dab222aa10062ad3
    - tt_27c_3.30v-run27.spice  sha256:5e04c91312ee030edb3a041e16aeb4f884a6de4b4cf431136efe4e465af2cd12
    - tt_27c_3.30v-run27.log  sha256:bb95b470357604ac461c389dca125a88a5706f8bebeef1e8f2f7f59342e27b4f
    - tt_27c_3.30v-run28.spice  sha256:0ffb616804770fb96bdc246a8a2ba92a9396f9ad7a85f43bf7d5cdb39b3f7897
    - tt_27c_3.30v-run28.log  sha256:0ca8fe13cf51240589ae3bad920539d2fb61f03823cae19068cecc66fc5a246b
    - tt_27c_3.30v-run29.spice  sha256:4578f9d860a7976bcd19eafd8f52c9963f9c0120651d182d225d776235147181
    - tt_27c_3.30v-run29.log  sha256:d47fc526e30147d5f1cc4f9456dbd1b260666de33723817b644852c5a6c78325
wall_time: 2.3m
---

## Result

- `dtrip_v`: mean 1.43918 over 30 seeds (sd 0.0163692, 1.1% of mean; min 1.4077, max 1.46754)

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
