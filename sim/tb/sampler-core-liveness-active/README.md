# sampler-core-liveness-active -- shipped liveness samplers in the active-power ledger

Issue [#463](https://github.com/2AMLogic/gf180-trng/issues/463). An **opt-in**
campaign driven through `klt sim`; it is not run by `sim/selftest.sh` or CI. Only
the offline unit tests (`sim/tests/test_liveness_sampler_power.py`) run in
ordinary CI.

| File | Role |
|---|---|
| `tb_sampler_core_liveness_active.sp` | circuit body: the tapped array (`xsb`, `xsv`, `xsr1`, `xsr2`, each on its own sense branch) beside a control array without the `xsr` taps, charge integrators |
| `request-grid.json` | the 27-unit `klt sim` request: `tt`/`ff`/`ss` x -40/27/125 C x 2.97/3.30/3.63 V (generated; do not edit) |

There is deliberately no `tb.json`: the deck is written for `klt sim`, so
`sim/run_corners.py` must not discover it and sweep it locally. Everything else
(grid, derivation, request generator, record writer) is
`sim/tools/liveness_sampler_power.py`; the summary is
[`sim/characterization-liveness-sampler-active-power.md`](../../characterization-liveness-sampler-active-power.md).

The whole grid goes to the batch fleet (`run --backend batch`). `run --backend
local` is accepted only with `--only PROCESS/TEMP/VDD`, a single debug point.
