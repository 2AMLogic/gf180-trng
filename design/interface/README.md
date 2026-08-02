# `design/interface/` — register file, output FIFOs, `OUT_MODE` mux, gate/flush

The block between the datapath and the outside world: the four registers, the
two output FIFOs, the streaming port, and the state machine that gates the
conditioned path. Fixed by
[`DR-0013`](../../spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md),
which derives its contract from
[`DR-0001`](../../spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md)
and
[`DR-0002`](../../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md),
extended by
[`DR-0016`](../../spec/decision-records/DR-0016-per-ring-liveness-monitor.md)
with a third source of that same latch;
verified at the level fixed by
[`DR-0009`](../../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md).

```
                       ┌───────────────────────────────────────────────┐
  raw_bit/raw_valid ──►│ pack 32 samples LSB-first ──► raw FIFO  ──────┼──► RAW_DATA
  (DR-0001 raw tap)    │                                  │            │    (never gated)
                       │                                  ├──[OUT_MODE]┼──► str_data/valid/ready
  cond_word/valid  ───►│ conditioned FIFO ────────────────┘            │
  (from #8)            │        ▲                                      ├──► DATA (gated)
                       │  cond_en / cond_flush                         │
  ht_fail_rct/apt  ───►│  latch ──► ht_alarm, gate ──► startup_req ────┼──► ht_alarm
  ht_fail_ring (#65)───►│    ▲                                          │
                       └────┼──────────────────────────────────────────┘
                            └─ three sources, ONE latch: RCT and APT watch the
                               combined raw tap, ring watches each ring's own
                               digitized sample (DR-0016)
```

**A health-test failure never reaches the raw path.** That is the one property
worth reading twice, and it is why there are two flush signals rather than one
— see DR-0013 §4. It holds identically for `ht_fail_ring`: a dead ring is
exactly the situation in which an integrator most needs the raw stream to
diagnose with.

## Files

| File | What it is |
|---|---|
| `regmap.py` | **Normative** register map and port map, and the generator for the two artifacts below. `--check` is the staleness guard. |
| `trng_regmap.vh` | **Generated.** Verilog header of addresses, bit positions and reset values, `` `include``d by the RTL. Never edit. |
| `REGMAP.md` | **Generated.** The integrator-facing register/port tables, including the top-level pinout contribution #16 needs. Never edit. |
| `trng_interface.py` | **Normative** bit-exact, cycle-accurate behavioural model. DR-0009 rule 5 makes this the definition of correct behaviour. |
| `trng_interface.v` | Synthesisable RTL. Checked against the model cycle-for-cycle under Icarus Verilog by `sim/tests/test_interface.py`. |

## Interface

The full table is in [`REGMAP.md`](REGMAP.md) (generated). In summary:

| Word | Register | Access | Purpose |
|---|---|---|---|
| 0 | `CTRL` | RW | `EN` (reset 1), `OUT_MODE` (reset `conditioned`), `SOFT_RESET` |
| 1 | `STATUS` | RO + W1C | `HT_FAIL_RCT`/`HT_FAIL_APT`/`HT_FAIL_RING`, `HT_ALARM`, `STARTUP`, `COND_READY`, `DATA_AVAIL`/`RAW_AVAIL`, `OVF_DATA`/`OVF_RAW`, FIFO levels |
| 2 | `DATA` | RO | conditioned FIFO; a read pops; gated by health-test state |
| 3 | `RAW_DATA` | RO | raw FIFO, 32 raw samples per word LSB first; a read pops; **never** gated |

The streaming port (`str_data[31:0]` / `str_valid` / `str_ready`) draws from
whichever FIFO `CTRL.OUT_MODE` selects, and transfers on `valid && ready`.

## The four states, and why `STARTUP` is its own bit

| State | `STARTUP` | `HT_ALARM` | `COND_READY` | Meaning |
|---|---|---|---|---|
| idle | 0 | 0 | 0 | `CTRL.EN` = 0 |
| startup | **1** | 0 | 0 | DR-0002 start-up test running; nothing has failed |
| run | 0 | 0 | **1** | conditioned path ungated |
| failed | 0 | **1** | 0 | a latched `HT_FAIL_*` (RCT, APT **or** ring) gates it |

Startup and failure both gate the conditioned path, so `COND_READY` alone
cannot tell them apart — and DR-0002's recovery path is meaningless if
software cannot tell that intervention is needed rather than patience. Hence
two bits.

## The contract with the conditioner (#8)

[`design/conditioner/README.md`](../conditioner/README.md) states it from the
other side: *"#26 asserts `flush` for at least one sampler clock on a
health-test-failure gate and on an `OUT_MODE` write in either direction, and
holds `en` low for the whole start-up-test window."* This block does exactly
that, and `sim/tests/test_interface.py` asserts each clause of it directly.

`cond_en`/`cond_flush` are **combinational** on the cycle's events, so the
conditioner sees the flush in the same cycle as the register write that caused
it. A registered flush would let the conditioner complete one more block in
the intervening cycle and push a pre-switch word into an already-flushed FIFO.
Independently, this block drops any `cond_valid` presented in a flush cycle,
so the guarantee survives a conditioner that reacts a cycle late.

## Running things

```sh
# Register-map staleness guard: fails if the generated header or REGMAP.md
# disagree with regmap.py. Also runs inside the unit-test set below.
python3 design/interface/regmap.py --check
python3 design/interface/regmap.py            # regenerate both artifacts

# Contract tests, the register map's own consistency, and RTL/model
# equivalence. The equivalence tests skip (they do not silently pass)
# without iverilog.
python3 -m unittest discover -s sim/tests -t sim/tests

# Demonstration run: the real conditioner model and this block wired
# together, across the start-up, gate, mode-switch and overrun scenarios.
python3 sim/tb/interface-regfile/run_demo.py --no-write
```

## What is *not* here

- **The health tests, and the per-ring liveness monitor.** RCT/APT, their
  cutoffs, the 1024-sample start-up window and DR-0016's per-ring RCT are
  #11's and #44's. This block consumes `ht_fail_rct`/`ht_fail_apt`/
  `ht_fail_ring`/`ht_startup_pass` and produces `startup_req`. It does not
  know how many rings there are: `ht_fail_ring` is one wire, and
  `STATUS.HT_FAIL_RING` is one bit, precisely so that the published register
  map does not depend on `N_RINGS`.
- **A bus protocol and any clock-domain crossing.** The register bus is a
  bare synchronous interface in the sampler clock domain (DR-0012). APB/AHB/
  Wishbone adaptation and CDC are #27's wrapper, deliberately not baked in
  here.
- **Timing closure.** Nothing in this directory shows this block closes
  timing at `ss` / −10 % / +125 °C. DR-0009 rule 6 says that gap is real and
  unowned.

## Health warning

`STATUS` reports what the *health tests* concluded; it does not conclude
anything itself. A clear `HT_ALARM` means no RCT or APT window tripped its
cutoff and no ring held a constant digitized value for `C_LIVE` samples — at
cutoffs derived from an **assumed** H₀ = 0.5 (DR-0002/DR-0016), which no
measurement has yet replaced. `COND_READY` means the block is not gating; it
does not mean the bits are good.
