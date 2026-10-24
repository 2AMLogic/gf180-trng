# `design/conditioner/` — digital conditioner (CRC-32 LFSR, K = 8)

The post-processing stage between the raw tap and the conditioned output
path. Fixed by
[`DR-0008`](../../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md);
verified at the level fixed by
[`DR-0009`](../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md).

```
                       ┌──────────────────────────────────────────┐
  raw tap (DR-0001) ──►│  32-bit Galois LFSR, poly 0xEDB88320     │──► cond_word[31:0]
  one bit per sample   │  cleared every 256 samples (K = 8)       │──► cond_valid
                       └──────────────────────────────────────────┘
                              ▲                    ▲
                          en (gate)            flush (health-test failure
                                                or OUT_MODE switch)
```

**One conditioned 32-bit word is a function of exactly 256 raw samples and
of no earlier sample.** That is what makes the SP 800-90B accounting in
DR-0008 §5 apply per block, and what makes the flush guarantee hold by
construction.

## Files

| File | What it is |
|---|---|
| `crc32_conditioner.py` | **Normative** bit-exact behavioural model. DR-0009 makes this the definition of correct behaviour. |
| `crc32_conditioner.v` | Synthesisable RTL. Checked against the model word-for-word under Icarus Verilog by `sim/tests/test_conditioner.py`. |
| `area_estimate.py` | The DR-0008 §4 gate inventory, with cell areas read from the installed PDK's own standard-cell LEF. |

Both implementations are parameterised on `K` and the polynomial; DR-0008
fixes the values.

## Interface

| Port | Dir | Meaning |
|---|---|---|
| `clk` | in | sampler clock — one raw sample per rising edge when `raw_valid` |
| `rst_n` | in | asynchronous power-on reset, active low |
| `en` | in | conditioned path enabled; while low the block is held cleared |
| `flush` | in | synchronous flush; clears the LFSR and discards the partial block |
| `raw_bit` | in | the DR-0001 raw tap |
| `raw_valid` | in | `raw_bit` carries a new sample this cycle |
| `cond_word[31:0]` | out | conditioned word; meaningful in the cycle `cond_valid` is high |
| `cond_valid` | out | one-cycle strobe |

`flush` takes priority over absorption: a raw bit presented in the same
cycle as the gate is not absorbed, because it belongs to the failing
window (DR-0002).

## K at the 2 kbps raw rate

*2026-10-11, #491.* The `Raw rate` row moved from `> 1 Mbps` to `> 2 kbps`
([`DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy`](../../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md)
§1; its §4 item 5 asks for K to be re-derived at the new rate). Re-derived
against DR-0008's own basis, **K stays 8**, and nothing in the RTL changes:

- **What sets K.** DR-0008 §5 picks K so that the non-vetted cap
  `0.85 × min(n_out, nw)` is the binding term for any input at or above the
  break-even min-entropy, with margin under the `H₀ = 0.5` design target.
  With `n_out = nw = 32` and `n_in = 32 K`, the break-even `H` per raw sample
  (`sim/tb/conditioner-crc32/sp800_90b.py`, `break_even_h_per_bit`) is
  0.4258 / 0.2129 / **0.1065** / 0.0532 for K = 2 / 4 / **8** / 16, i.e.
  margins of 1.17× / 2.35× / **4.70×** / 9.39× under `H₀ = 0.5`.
- **None of those inputs depends on the raw rate.** `n_in`, `n_out`, `nw`,
  the 0.85 cap and `H₀` are all per-sample or per-block quantities, and the
  rate decision explicitly leaves `H₀`, DR-0002 and DR-0007 §§1–2 unchanged.
  The governing inequality is therefore the same one DR-0008 solved, and it
  has the same answer. DR-0008's own "Revisit if" names a moved `R_raw` only
  insofar as it changes the margin argument against K = 2 / K = 4 — that
  argument is about `H`, which is still unmeasured (#12), so it does not move.
- **A slower raw rate is not, by itself, evidence for a different K.** It
  makes the delivered rate smaller, which makes a smaller K *tempting*, but
  trading the 4.70× entropy margin for rate is exactly the trade DR-0008 §3
  declined until `H` is measured. A different K would need its own decision
  record.

What does move is the arithmetic that is linear in the rate. At the ratified
2 kbps (`sim/tools/time_to_first_valid.py`):

| Quantity | At 2 kbps | Historical, at the original 1 Mbps |
|---|---|---|
| Delivered rate `R_cond = R_raw / K` | > 250 bps (one 32-bit word per 128 ms) | > 125 kbps (one word per 256 µs) |
| Conditioner latency, 256 samples | 0.128 s | 0.256 ms |
| Start-up health test, 1024 samples | 0.512 s | 1.024 ms |
| Arithmetic floor on time-to-first-valid (1280 samples) | 0.640 s | 1.28 ms |
| Tool total: + one sampler clock + measured oscillator start-up | 640.5 ms | 1.281 ms (#14) |

The 2 kbps column is arithmetic at a target rate, not a measurement made at
it. These are design-stage figures; none of them is an entropy claim.

## What is *not* here

The output FIFO, the `OUT_MODE` mux and bypass path, the `DATA` /
`RAW_DATA` registers, the latched `HT_FAIL_*` flags, and the generation of
`en` / `flush` are **#26's** half of the interface. The contract between
the two halves is the port list above: #26 asserts `flush` for at least one
sampler clock on a health-test-failure gate and on an `OUT_MODE` write in
either direction, and holds `en` low for the whole start-up-test window.

Bypass costs nothing here — the conditioner is not in the raw path at all
(DR-0001 §4/§5).

## Running things

```sh
# Contract tests, the SP 800-90B arithmetic, and RTL/model equivalence.
# The equivalence tests skip (they do not silently pass) without iverilog.
python3 -m unittest discover -s sim/tests -t sim/tests

# Area inventory against the installed PDK's standard-cell LEF.
python3 design/conditioner/area_estimate.py

# Demonstration run: simulated raw bitstream in, conditioned bitstream out.
python3 sim/tb/conditioner-crc32/run_demo.py --no-write
```

## Health warning

This is a **linear** conditioner. Feed it a deterministic stream and it
emits a maximal-length LFSR sequence that will pass monobit, runs, and most
of what a casual reader would try. **The appearance of the conditioned
output is not evidence about the entropy source.** That is why the health
tests run on the *raw* stream and gate this path (DR-0002), and why raw
access is unconditional (DR-0001). See DR-0008 §Consequences.
