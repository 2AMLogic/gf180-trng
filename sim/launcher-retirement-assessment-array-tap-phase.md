# Retiring `run_array_liveness_tap_phase.py`: assessment (#663)

Issue #663 asked whether [`sim/tools/run_array_liveness_tap_phase.py`](tools/run_array_liveness_tap_phase.py) can be
removed in favour of the existing request-based runner (`klt sim`, via
`sim/harness/klt_request.py`). Retirement was authorized only **after** the
replacement is shown to cover what the launcher was kept for. This document is
that comparison. **Result: not retired.** The launcher stays, and the gaps
below are what would have to be closed first. No simulation was run and no
record or raw file was touched to reach this conclusion.

What the launcher does for the four-deck family (`array-liveness-tap-phase-
{clocked,static,xsb-clocked,xsb-static}`, seeds 1-4, `tt/27/3.30`), and what
exists today:

| Launcher behaviour | Existing facility | Established? |
|---|---|---|
| Fixed experiment identity: four decks, seeds 1-4, `tt`/27 °C/3.30 V, no supply tolerance | `sim/run_corners.py <deck> --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 2 3 4` is the same invocation; the launcher only wraps it. A `klt sim` request for these decks does not exist: `git ls-files 'sim/tb/array-liveness-tap-phase-*'` holds only `tb.json` and the `.sp` deck | Only via `run_corners.py` |
| Per-seed noise independence (DR-0031: ngspice-46 seeds `trnoise` from the process id, not `.option seed`; the harness checks completed runs for duplicated noise) | Enforced inside the harness runner. A `klt sim` unit is a PVT/Monte Carlo sample, not a harness seed, and nothing shows that its per-corner processes give four independent noise streams or reproduce the harness's `.option seed` identity | **No** |
| Evidence is a harness record (`sim/records/*.md` with `raw.files` checksums, `seeds`, `sigma_1`) that `array_liveness_tap_phase_variants.py` reads | `run_corners.py` mints it. `klt sim` writes a klt response; no minting step exists for this family (cf. `liveness_sampler_power.py record` for another family) | **No** |
| Skip a deck whose newest `tt/27/3.30` record has `sigma_1` from all four seeds (`deck_status`: complete / incomplete / missing; stale and other-corner records ignored; newest stem wins) | `klt sim --resume` resumes from `--outdir/checkpoint.json` within one request; it does not look at `sim/records/` and cannot bind completion to a harness record's corner and seed count | **No** |
| Remove an incomplete record and orphaned `raw/<stem>/` before a retry, never a complete or other-corner one, never an unparseable one (`clean_stale`) | `klt_request.py` refuses to reuse an occupied output namespace (exit 3), which protects evidence but does not clear a stale reservation | **No** |
| Survive the launching session ending (`start_new_session=True`, log + pidfile) | `klt sim --submit-only` / `--attach` / `--job-status` give a detached batch job; whether the fleet executor holds a run of ~75-90 CPU-minutes per seed, with the 86400 s per-run bound, has not been exercised for these decks | **Unverified** (needs a live run) |
| Concurrency: one seed at a time (`DEFAULT_JOBS = 1`) because one ngspice of these decks measured ~7.6 cores of CPU per second of wall clock, and `-j 4`/`-j 8` collapsed throughput ~50x ([`characterization-shipped-array-tap-phase.md`](characterization-shipped-array-tap-phase.md), "What the runs cost") | Local: `run_corners.py -j`. Fleet: `--max-in-flight` / `--max-concurrent-jobs`, with no measurement of these decks on that backend | **Unverified**; the measured one-job default must not be carried over to another backend, nor raised, without evidence |
| Bounded retry (`--max-attempts 5`) and per-run timeout (`--timeout 86400`) | `run_corners.py --timeout`; `--capacity-retries` retries only fleet-capacity refusals | Timeout yes, per-deck retry **no** |

The offline tests that already pin the launcher's evidence handling are
[`sim/tests/test_run_array_liveness_tap_phase.py`](tests/test_run_array_liveness_tap_phase.py): `DeckStatusTests` (missing,
complete, three-seed partial, no `sigma_1`, other corner, other deck, newest
stem and newest date win) and `CleanStaleTests` (incomplete record and raw
removed, complete record untouched, other corner and other deck untouched,
orphan raw directory removed but a raw directory with a record kept, a file
named like a raw directory kept, an unparseable record left alone). They stub
the records directory and never run `clean_stale` against `sim/records/`. A
replacement would need an equivalent suite; none exists, so none was deleted.

Missing capability, to be reported rather than built around: **a request-based
runner that (a) takes a harness testbench slug with a seed list, (b) mints the
same harness record and `raw.files` checksums, and (c) can skip a unit whose
valid record already exists for the exact deck, corner and seed set.** Until
that exists, and until a live run on the chosen backend has shown the
session-lifetime and concurrency behaviour above, re-running this family at
another corner or after an interruption goes through the launcher:
`python3 sim/tools/run_array_liveness_tap_phase.py --status` to see which decks
have a clean record, then `python3 sim/tools/run_array_liveness_tap_phase.py
--decks <deck> ...` to resume. Do not run the launcher without an
operator-approved simulation budget; this document authorizes none.
