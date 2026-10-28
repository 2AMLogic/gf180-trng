# `sim/tb/power-intent/` — gate-level power-down / power-up check

Gate-level, zero-delay functional simulation of the synthesized `trng_top`
across a power cycle, for the power intent in
[`design/power-intent.md`](../../../design/power-intent.md) (#708). Like the other
non-ngspice testbenches it has no `tb.json` and is invisible to
`sim/run_corners.py`; it is driven by `sim/tools/power_intent_check.py`.

```sh
python3 sim/tools/power_intent_check.py --check --require-tools   # good design + every broken fixture
python3 sim/tools/power_intent_check.py --variant no_iso          # one broken fixture, exits 1
python3 sim/tools/power_intent_check.py --write-record            # mint an evidence record
```

## Files

| File | Role |
|---|---|
| `tb_power_intent.v` | rail model, AND-cell isolation, retention clock gate, sequencer, scenarios, monitors |
| `pi_cells.v` | power-aware flip-flop models (X when the rail is down) the tool swaps into the netlist |

The tool writes a derived copy of `design/trng_top/trng_top.synth.v` to a
scratch directory; the committed netlist is never modified.

## Scenarios

Cold boot through the wake sequence; a power cycle at an arbitrary point in a
conditioner block with a register read held pending across it; a power cycle
with a latched health-test alarm; a back-to-back down/up (the sequencer waits
out the rail decay).

## Broken fixtures

`no_iso` (an output without a clamp), `iso_early` (isolation released before the
rail is good), `reset_early` (gated reset released before isolation),
`ret_lost` (a retained flop on the gated rail), `ret_clk_on` (retention clock not
stopped) and `no_decay_wait` (switch re-closed inside the decay). Each must be
reported; the check fails if one is not.

## Limits

No P/V/T corner exists here and no timing, leakage or switch claim follows from
a run. Rail settle and decay are placeholders until #707. Only output crossings
are modelled.
