---
record: 2026-08-17-sampler-dff-mc-offset-03
date: 2026-08-17T01:19:01Z
status: valid
supersedes: 2026-08-02-sampler-dff-mc-offset-01

testbench:
  path: sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset.sp
  sha: c0286e14e6a628ae729f746ffe43dba206d90c2d
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 4da0bea1c43e66c3424fb5acd16a4cb30b538bba-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-47 : Circuit level simulation program"
  platform: macOS-26.6.1-arm64-arm-64bit-Mach-O

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
  path: sim/records/raw/2026-08-17-sampler-dff-mc-offset-03/
  files:
    - tt_27c_3.30v-run0.spice  sha256:1438cb093fd7966b1ccd1396a73fa32fc28d5365388bd8fb02f9df502a09b2c1
    - tt_27c_3.30v-run0.log  sha256:9b0e27536c1aa11f0ddcb2bd1949a67ff5fa4a700d2040cfe168ae8df3f5b519
    - tt_27c_3.30v-run1.spice  sha256:06ec5d68ef9c01364a31e6350307917c130825bdf591f14643566e330241b792
    - tt_27c_3.30v-run1.log  sha256:ca9c0c5211d8a49478b1c0479781f19d8a7763373c504968758c3e944ee16091
    - tt_27c_3.30v-run2.spice  sha256:11911a2b70dbc8bf5af676063101819d26ca9a3a414770c404dd39a74197c7ea
    - tt_27c_3.30v-run2.log  sha256:631045016f66bf847857c0fb4c6153e490637200c0bf41dbc0dac01bacc6f3b6
    - tt_27c_3.30v-run3.spice  sha256:6fed18a00e2f43cb87e1eb589762a2baeadc0b4952ce3ab63c0184f926ec6ff0
    - tt_27c_3.30v-run3.log  sha256:ffacf2642cef9cef58518d99b481cf4fcaa09144375a1d5f90705596e581977a
    - tt_27c_3.30v-run4.spice  sha256:8051c8b78c1b6d6e29605af035d1669153bce1a354041b15307fa4430e2ed61c
    - tt_27c_3.30v-run4.log  sha256:1d5505ec47d3bb0cc05de7a02589b22bb68421643530214473701b622bf138c8
    - tt_27c_3.30v-run5.spice  sha256:5116bdc22fe19906e16696edd610f8226a83dad0717dd89aa02505036a855ada
    - tt_27c_3.30v-run5.log  sha256:fc0e59648614c86b607d371e1adf6f8336272d0177300cae069a7efd771cb31e
    - tt_27c_3.30v-run6.spice  sha256:fee311ef507a4542a346d68a29f3866eaee7742fe03d40acbba43615ef1c3461
    - tt_27c_3.30v-run6.log  sha256:263c33f65f4f0380ad10a6f9666f8f2679caf7f5c4032454c8fd95a8b3325aec
    - tt_27c_3.30v-run7.spice  sha256:8e5c64489fe66e064643a40e7868ca82e55fa4ed1ffbe13f1072a7170151ef5c
    - tt_27c_3.30v-run7.log  sha256:1929030ec91e863b51e601e203e84051a4b5492f7439fb12a74773b1d018e96a
    - tt_27c_3.30v-run8.spice  sha256:6234933a66e4f70e4186212681e0d39d9dca25368d2785a2c591119d3bb85bbf
    - tt_27c_3.30v-run8.log  sha256:bcda0d292f3c28213c44314228b3771f49005b5a2e4d247398af1d513231e885
    - tt_27c_3.30v-run9.spice  sha256:0d48c77288777b9e7eb642e684b9d3d7e50c287f5c6553b7d3c1b42cafc21785
    - tt_27c_3.30v-run9.log  sha256:a9ef5328ea566f5f6db5d3b6f9d4e0eb802ef06045ce9346165115e0dc88452b
    - tt_27c_3.30v-run10.spice  sha256:d1f8e0b8615d208748d759a01f539496c26216041bf76dbe4a020e2b2ffcfb59
    - tt_27c_3.30v-run10.log  sha256:d3635c97a80f9db2a43edc8cde2d0fe09461ce387910816fb16378095d1ce717
    - tt_27c_3.30v-run11.spice  sha256:a9fe6dbff1e61ae2127bae4a5999d0893dc81d3284fe687cbd4cb8fd8a9b8e7a
    - tt_27c_3.30v-run11.log  sha256:472fb00e6c57b1c5c1273a41a7f7c7fd12609ac37577c2d5012559315c6e59f5
    - tt_27c_3.30v-run12.spice  sha256:50b64e4dd898852f372f8a56d32896dc3824be3d1e0e830b10784b89631bfb3d
    - tt_27c_3.30v-run12.log  sha256:5ab0e68a1eaafe0197c4c6ce130fa8047464e756aaeb7feb4a4659c0b9249c33
    - tt_27c_3.30v-run13.spice  sha256:3e010ab9315bb77f7bc1741fcc1008f6c8cd20ecaaea52b170fe36cf363dc11a
    - tt_27c_3.30v-run13.log  sha256:cd49363161f04c885868862acdc4a546fb0c2cd0c85ad511fdf9cc53a03a9263
    - tt_27c_3.30v-run14.spice  sha256:41b3506c0ab1cb4d19204d00e6a93ea43925275a58dbce4a36d8894b1eedb7ca
    - tt_27c_3.30v-run14.log  sha256:5e32731aa54421becc245a9ebf1391fb3885c72852c2a2a17a0915df246c0246
    - tt_27c_3.30v-run15.spice  sha256:4103bf03bd9a18e1bf17c194ff1f7d6caad2904e933588f739aac9c74fa652da
    - tt_27c_3.30v-run15.log  sha256:61bd69bfb1414ba8a5b6eb16994b9e2fce007e200d967355b583bed47a820bba
    - tt_27c_3.30v-run16.spice  sha256:2f2626b741b02c7d168fd92cf3e47c430312c229fdbf551fb657917dd34aef83
    - tt_27c_3.30v-run16.log  sha256:5b3a18887bde862502b687f3b686d359854cd1f225879f5d04c4b12457e3003d
    - tt_27c_3.30v-run17.spice  sha256:7abb3eca46a2819087497df15c0617ddb1c7da2bdc135d77b21f21f5c8ff2465
    - tt_27c_3.30v-run17.log  sha256:a8ea3b0c234c8ff01ab74441144bafbd1141e9bd0ff90621162b329c3435ed31
    - tt_27c_3.30v-run18.spice  sha256:cb2819289c5fb02a2e6a7915294b9a655759386662a14c56a097bbcbe80b2cb0
    - tt_27c_3.30v-run18.log  sha256:3a9746155d9723a49ac5f607f9936e51776e3ef09546cf039cd0f443e603186c
    - tt_27c_3.30v-run19.spice  sha256:3fd16045a55d89790a14ebefe53a7d884a9063fcf1c2064267841b370697ca71
    - tt_27c_3.30v-run19.log  sha256:8c2dd410d91a3b9ba2debfe343b7b8ee5caa7cf6cd590194faaa06d7ffabea24
    - tt_27c_3.30v-run20.spice  sha256:582a144466a0fabc8e8c0307aeb3622c10683d462722866ee414a24636347703
    - tt_27c_3.30v-run20.log  sha256:12b57f875bea40fc8416f2c3abeb524451c8857febb814dcb9a22e064795744b
    - tt_27c_3.30v-run21.spice  sha256:75cacd5a7209d48f2dfbc3c7e4bbadc671120719b66d6928d7be31f7881d3f97
    - tt_27c_3.30v-run21.log  sha256:bfa99cec2750b57b269887f2337e5aad00fa3ed4a9fcb329338f858cd12ddf47
    - tt_27c_3.30v-run22.spice  sha256:4ed3e86f7cfac2d9ce27cac87b05d8e3754a0dfbfaedb8c2183db8d819d6cda0
    - tt_27c_3.30v-run22.log  sha256:4d5d88b849c96c465099fc110112508569d8fea1c1378c5d783e22528c2adcf3
    - tt_27c_3.30v-run23.spice  sha256:783296cd18bfd087f4515869c66b1befde55e9235391c2ead7353e6a45904474
    - tt_27c_3.30v-run23.log  sha256:ca475025a12815874bbefdab1a22a9e6ee0994ff543d50bfed3653f95b30a345
    - tt_27c_3.30v-run24.spice  sha256:494ae0c08d75b4a83fa5c2217de792de00615304c810f84c2939dd579bbcee21
    - tt_27c_3.30v-run24.log  sha256:74feababb35d1373c82defadeb9c0c014a19f8384c60628ad197f38f8f1f9bab
    - tt_27c_3.30v-run25.spice  sha256:102a92945ffce371b76289d9d67b00fa1eccc7be63645c7f53ba27915cde9d00
    - tt_27c_3.30v-run25.log  sha256:32da9987992d7acf164230ecb82366d23e394cfb5c7274c41991be3bdbc7b1f4
    - tt_27c_3.30v-run26.spice  sha256:d4bd06de6056c7f0e06962a6d337f6e184c723c63b2f3b3dd4b31be5971e9efe
    - tt_27c_3.30v-run26.log  sha256:74b2c84d35c9969a5a741a26b488b076400807600c0694dfade880381562f8c9
    - tt_27c_3.30v-run27.spice  sha256:e6f019f7b80735b369fc031f1f5eda9b73a3cc806eb51d0a10427a67ca65338c
    - tt_27c_3.30v-run27.log  sha256:d4568c460755eb265599348f9d548def066ca6df831526ca70eb0affa3ab6ea8
    - tt_27c_3.30v-run28.spice  sha256:70efccda0466e7288a2c522da5922bd0762c5bcd0b5348319c0bad99fe8d09c9
    - tt_27c_3.30v-run28.log  sha256:9aabb33d350a72b503a6a9ea95161cdf6a84bf21a217bc442503aa1fcf35aceb
    - tt_27c_3.30v-run29.spice  sha256:f52dd9bfeb6342bd6fd6d37312add3c68c321fda122ce925531798b2f21034f0
    - tt_27c_3.30v-run29.log  sha256:8a5caa1553e06e62ba94f38babb2242049b08d6bcfabb1320aa27d6c3927e907
wall_time: 39.0s
---

## Result

- `dtrip_v`: mean 1.38482 over 30 seeds (sd 0.0147787, 1.1% of mean; min 1.35061, max 1.41775)

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
