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
