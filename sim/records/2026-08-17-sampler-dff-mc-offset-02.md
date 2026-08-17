---
record: 2026-08-17-sampler-dff-mc-offset-02
date: 2026-08-17T01:17:45Z
status: valid

testbench:
  path: sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset.sp
  sha: c0286e14e6a628ae729f746ffe43dba206d90c2d
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 4da0bea1c43e66c3424fb5acd16a4cb30b538bba-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-47 : Circuit level simulation program"
  platform: macOS-26.6.1-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: mc
  tstop: n/a (op-point analysis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 30
seeds: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

raw:
  path: sim/records/raw/2026-08-17-sampler-dff-mc-offset-02/
  files:
    - ss_125c_3.63v-run0.spice  sha256:3b00ddaf219bc73185e688a78533e3f873fbc22abfdfa742ac26d5f1748cb346
    - ss_125c_3.63v-run0.log  sha256:1ff8390be508c645f333f20bc4f479d491884721101f8e2d6b94c79d5c7b7546
    - ss_125c_3.63v-run1.spice  sha256:b07b71c4d7cb7c105109a33c5ad30790908904018879d875946de410dd3eb689
    - ss_125c_3.63v-run1.log  sha256:1b8259e5fd2b7c5d63c005965f28c6318daee2c8ce79dcf0fe4208ef44c4bcb5
    - ss_125c_3.63v-run2.spice  sha256:3d975be135baa2fc8bd92177f0a13cef4d84f59301d2e2ab3eb4f5f7b612d961
    - ss_125c_3.63v-run2.log  sha256:13db35a96570d013023bfe15ddc46dd76aca4fd153cb22331fd2af7ec598287d
    - ss_125c_3.63v-run3.spice  sha256:87c2098f067c6424912eb6f81149f011a62a730c6ea57a57f5e122b7c7218381
    - ss_125c_3.63v-run3.log  sha256:edd26cddc687ebdd1eabd39299e08845b8c9412efaddfb25c200af1a0b016cfb
    - ss_125c_3.63v-run4.spice  sha256:8933a36581d97f1c66c405f05fd264abe162e31459ec509a58b3f0bb24e9c7bb
    - ss_125c_3.63v-run4.log  sha256:849c1f102d0cb2bf0aa8e4b689ec2259a58f63e52c0960775e643175482479fa
    - ss_125c_3.63v-run5.spice  sha256:2c24251f8e69e59684aa0d3b5a14681a7a7b425d29846521eeddc363a08e5633
    - ss_125c_3.63v-run5.log  sha256:504638537adb9e2c526f3b0f0a4fff96688958c161412adaf6259c1e1e862d8a
    - ss_125c_3.63v-run6.spice  sha256:633aa5261cf89395e9cd06f3aa7a0d3020114e8c3d95f8bcc6efd7e59f90f542
    - ss_125c_3.63v-run6.log  sha256:db43fe259d4e92a56bef4162bcf0e9f716f398c9d7d3e0df620401012520125e
    - ss_125c_3.63v-run7.spice  sha256:1dc9d0fe28ee8e49fb52cc4748d22d41569f3d43a6e572367805535de2c22e7c
    - ss_125c_3.63v-run7.log  sha256:373ed54ede36351c46860d34b12e6cd157286bbf771d052d43cc77107e47116c
    - ss_125c_3.63v-run8.spice  sha256:b6fe592f236ee51579b853a394c2448fb87c463e5c3d37b4ed0f83db2e86897a
    - ss_125c_3.63v-run8.log  sha256:40fa3c2c2a861193ad7f371e47a37dfb7ea5c8d000918d56b4ef22f16da5ee5b
    - ss_125c_3.63v-run9.spice  sha256:9cef39100cae8f062953ee6d4a3661f1f14f50846612b4a69663420713e83827
    - ss_125c_3.63v-run9.log  sha256:ee35a0f5c5aa036caccc1ad1c518c1b65e66fadd4912729def287e3041694d53
    - ss_125c_3.63v-run10.spice  sha256:21dec5082a12fa5ac4f80c673702973726f604ea295e7c92f89207cff5095122
    - ss_125c_3.63v-run10.log  sha256:6bd928728d3fb44458a65293ac30164c61bb40fb00d89faf42ddc2dba8c708fb
    - ss_125c_3.63v-run11.spice  sha256:ac57f11c335b613227f6926b00d5083deea96b3bd1f0ce6ab86ee3fcc27822f2
    - ss_125c_3.63v-run11.log  sha256:00a3aaf30b04985a31bdeca4b9af2a484b9d10fdda6c42ac0ffcad4e52b79fbd
    - ss_125c_3.63v-run12.spice  sha256:6bd4679f7339f992605e3037bd4ebef8ab963b70f962d90f92c8b3f112830fa2
    - ss_125c_3.63v-run12.log  sha256:6885cb5c25fa98f09018e573f4004ea54669bc791063b0c2b903e6660f946ca1
    - ss_125c_3.63v-run13.spice  sha256:d77cbe380f531de5dbfb49ff037e8469c1ed9c75adfd1e23541845a676549ec1
    - ss_125c_3.63v-run13.log  sha256:b949da82542d0b26c2718657bc63e266a4010002029f0a7d34e861782915b620
    - ss_125c_3.63v-run14.spice  sha256:7fe101cffc09682d874a6dc555ab52d1be36ba5940c88be6aa877209856e1e1d
    - ss_125c_3.63v-run14.log  sha256:4a5f08220a888fe51d5c858e613c12deca613e6ed964ffdb04f495c628215347
    - ss_125c_3.63v-run15.spice  sha256:ef5ec106925fff0f7df407402df7932406082eddc19bf1198a55461a6d9ff229
    - ss_125c_3.63v-run15.log  sha256:40bef0daedec26c68e83b04f8086adc1c653663b51724aaa5d91fff9d194869c
    - ss_125c_3.63v-run16.spice  sha256:4f13672c7dc48ef259dc1144307e9b7e1ae1124cf83f9c8450ab3fa1ae96331e
    - ss_125c_3.63v-run16.log  sha256:f2719f8e24f9c632dd5f326e785e8a59b8e841aa053486961de37542c5ae56d1
    - ss_125c_3.63v-run17.spice  sha256:cdc3cb0f063cd8c8e7c2935d8de8aff20fd82b6ad5f2e6cb02b305fef8f9132d
    - ss_125c_3.63v-run17.log  sha256:20bb9ac202f3f475382df78575b0d34a6f856b05db470ab5ce3b39582ec4b216
    - ss_125c_3.63v-run18.spice  sha256:8a2a1634c16631419227577994bae061c5c532415c779b6d03d5e2b3383b31ac
    - ss_125c_3.63v-run18.log  sha256:8accfe26b9f10d20f8a92cceee0dd650682fae2dcd7b47419b043beda7fff2bf
    - ss_125c_3.63v-run19.spice  sha256:f6d841e46dd94765e0d31f0fd5fef63d0f05d41cf4c93f802a49b871854b78d1
    - ss_125c_3.63v-run19.log  sha256:041fd0a3b947ec73b44082eacac248b7ba266334ff4ce3097d384f1dc9494757
    - ss_125c_3.63v-run20.spice  sha256:4dc9cabe2d3b972b35c39a96aee962c833be0a8bbdb1f6c71fe9e80866e97527
    - ss_125c_3.63v-run20.log  sha256:7765c67cfaf9c8babc7831ee5b9888698ab4f51e9015b9a391b797787a3f61b4
    - ss_125c_3.63v-run21.spice  sha256:65b2cc72018d6724ff613e2456faf644b09e46633d1ed4bb04a2ec9b29332314
    - ss_125c_3.63v-run21.log  sha256:d038e03b46b3a67e814579073d77f7e8b95105c24bee3a37f86bcad1032ccd90
    - ss_125c_3.63v-run22.spice  sha256:f91cd3c6646a0075484afb3b3d6836cd7870371004dcd4b21212e352b77df0ab
    - ss_125c_3.63v-run22.log  sha256:e86199166586263d3a8aca11abdda2c843e8b63b3fe035c405d893cc1f7641e1
    - ss_125c_3.63v-run23.spice  sha256:5ee559567b193f8f6b3b6625149c5f6e8addd1effc93bd445a338c2be032fae0
    - ss_125c_3.63v-run23.log  sha256:a5ee29f4f124720f0d25ac7b7d95d9393e2d38d7b3b002c321cad31731bc714e
    - ss_125c_3.63v-run24.spice  sha256:70477ce96c40212c6ea9370035c36b19c7c689de1e4dd971f433e252b99f1438
    - ss_125c_3.63v-run24.log  sha256:3de4bcc282b5fa6f8df5d9e987b6b3dbf90c2b6a33a6492b6b2e328cd262f374
    - ss_125c_3.63v-run25.spice  sha256:8d0a0e58c5120ea2125efcff2ff97aa443ed38d0281a4542ddec6be9ea2e1a31
    - ss_125c_3.63v-run25.log  sha256:df57f5a2fa66f916fb37d9b68835e41c269b44f6f0f23cf19fe5bd1bbeca2a83
    - ss_125c_3.63v-run26.spice  sha256:7bb3bf71270923039ea667b26f22b393b6cb071235490a9262ba48a89144bc59
    - ss_125c_3.63v-run26.log  sha256:815b915b30c4839b9f66e7f1b2506f124332085031d2d12bf8ec312909105024
    - ss_125c_3.63v-run27.spice  sha256:4eea6eb55c6030ce1cc47eb3a17fc9fce82240a11758cd22f73b99479e056188
    - ss_125c_3.63v-run27.log  sha256:ecc8f2418235f93ca828355fdd8b65b3902dff5c36048f4e37ea76e2b316a3a4
    - ss_125c_3.63v-run28.spice  sha256:bbe2aa0e443226a521967271e151e2e564a0cbac659c0c2b15569bbf062a815d
    - ss_125c_3.63v-run28.log  sha256:4c2be1e481d2711433373fe939b3ae1125b5a762d31808ac9071a3c53954310a
    - ss_125c_3.63v-run29.spice  sha256:c79e5a4b62ad06818eaeb08230711181d03a7839889f138dcf4c72d6f0d45ef9
    - ss_125c_3.63v-run29.log  sha256:835f5fda745fefc1383e4ddbb52dc880590a5f8e2fa2fd42d8a391120d59586a
wall_time: 19.9s
---

## Result

- `dtrip_v`: mean 1.5402 over 30 seeds (sd 0.0150188, 1.0% of mean; min 1.50582, max 1.57337)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 8 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 9 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 10 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 11 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 12 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 13 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 14 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 15 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 16 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 17 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 18 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 19 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 20 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 21 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 22 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 23 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 24 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 25 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 26 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 27 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 28 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 29 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 30 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 8); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Issue #146: two PVT points, not a full corner sweep. tt/27C/3.30V (the pre-existing nominal record) paired with ss/125C/3.63V, DR-0015's own measured entropy-binding worst corner over the array's full covered PVT grid -- see sim/tb/ro-array-core-mc-freq/'s tb.json for the identical justification (this manifest's `corners`/`temperatures_c` list the two VALUES exercised, paired, not independently swept -- not a 2x2 grid).
- The dc sweep bounds and the mid-supply comparison value are `{vdd_val}`/`{vdd_half}` format fields, substituted by sim/harness/runner.py's compose_deck (Python str.format, before ngspice ever sees the line) rather than left as ngspice-side `.param` references: ngspice's control-block `dc`/`meas dc` commands do not evaluate `.param` symbols (or curly-brace-substituted ones) in a numeric-argument position -- confirmed empirically against ngspice-47 (`Error: Bad syntax!` either way) during issue #146's bring-up of the second (ss/125C/3.63V) PVT point, which needs a sweep bound and comparison value that track vdd_val instead of the single hardcoded 3.30V/1.65V pair this manifest carried before #146.
- Until issue #146, `corner.process` was bookkeeping only for this testbench: `extra_lib_sections: ["statistical"]` unconditionally replaced whichever corner's own per-family sections would otherwise load (see sim/harness/runner.py's compose_deck), so every `corners` entry other than `tt` was silently a no-op. #146 removed `extra_lib_sections`: every gf180mcu per-corner device library already implements the identical `sw_stat_mismatch`-gated local (Pelgrom) mismatch model the `statistical` section used, so dropping `extra_lib_sections` and keeping `sw_stat_mismatch=1` lets the harness's normal per-corner `.lib` selection combine with mismatch directly.
- Measures the MASTER LATCH's own decision threshold (node xdut.mb) with clk held at 0 throughout, not a full clocked capture. It says nothing about clk-to-Q delay, setup/hold margin or metastable resolution time -- those are sim/tb/sampler-dff-setup-hold/'s job, unchanged by this run.
- The .dc sweep is quasi-static (no dV/dt): it measures the offset of the STATIC switching threshold, not a dynamic one. Converting it to a raw-bit-probability bias (issue #13's own analysis) additionally assumes the real XOR node's crossing is fast enough, and its slew rate near mid-supply steady enough, that the static and dynamic thresholds coincide to first order -- a modeling assumption stated once here rather than re-derived per record.
- 30 mismatch seeds characterizes the offset distribution's rough mean and spread, not a tail probability.
- The deterministic negative control (mismatch disabled, sw_stat_mismatch=0) is a separate testbench, sim/tb/sampler-dff-mc-offset-control/ -- tb.json's design_params are fixed per testbench, so there is no CLI flag to flip sw_stat_mismatch for a single run of this manifest.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
