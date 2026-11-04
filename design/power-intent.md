# Power intent for a power-gated digital section

Status: **intent and verification only.** Nothing here changes the shipped RTL,
netlist, layout or any spec row. The `Power` row's idle half and DR-0017 stand
as written; whether the row can be met this way is a decision for the operator
(see "Does idle-with-state-retained still hold?" below, routed via #700).

This document says what a power-gated `trng_top` digital section would have to
do, in a form `sim/tools/power_intent_check.py` can hold the rest of the repo to.
[DR-0017](../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md)
records that gating is the only lever left on the idle row and that the cell
library has no isolation, retention or switch cell; this file is the missing
power-intent description. The switch cell, its sizing and its numbers are #707.

## Domains

| Domain | Contents | Rail |
|---|---|---|
| **gated** | everything in `trng_top` (conditioner, health tests, ring liveness, interface, FIFOs, datapath) except the always-on set | switched (header, #707) |
| **always-on** | the retained flops below; the isolation cells on every output; the retention clock gate; the power sequencer | un-gated |

The always-on set is deliberately tiny: a retained flop leaks like any other
(12.2 nW at `ff`/+125 degC, DR-0017), so each one spends idle current.
Five flops is about 61 nW before the clamp and clock-gate cells.

## Per-element disposition

| State element (interface RTL name) | Disposition | Why |
|---|---|---|
| `ctrl_en`, `ctrl_out_mode_raw` (the `CTRL` register) | **retained**, plain flops on the always-on rail | cheap, and the host should not have to reprogram them |
| `fail_rct`, `fail_apt`, `fail_ring` (the latched alarm) | **retained** | an alarm must not be laundered by a power cycle; DR-0002 recovery stays explicit clear plus retest |
| `state` (start-up / run / failed) | **re-initialised** by the gated reset | the health-test window is gone, so a full start-up test must run |
| `ovf_data`, `ovf_raw` | re-initialised (0) | they describe FIFO contents that no longer exist |
| both output FIFOs (contents, heads, counts), `raw_shift`, `raw_bit_count` | **discarded** | 512+ flops; retaining them defeats the purpose |
| conditioner state, in-flight block | **discarded** | a block cut mid-way would be wrong, not merely incomplete |
| health-test window position, run counters, ring-liveness counters | **discarded** | restarted by the start-up test |

The retained flops are clocked by `clk_ret`, a gated copy of `clk`, and reset
only by `rst_ao_n`. Retained flops are fed by the gated domain (the `fail_*`
latches take `ht_fail_*` as input), so while the rail is down or being brought
up their clock **must be stopped**, or they would capture X. This is not
hypothetical: with the retention clock left running the gate-level run corrupts
`CTRL` on the first power cycle (fixture `ret_clk_on`).

Netlist change this implies (applied only to the derived simulation copy): the
retained flops' `CLK` pin moves to `clk_ret` and their `RN`/`SETN` to `rst_ao_n`;
`trng_interface` and `trng_top` gain those two ports.

## Isolation

Every net crossing out of the gated domain is an output port of `trng_top`
(enumerated from `design/trng_top/trng_top.v` and the synthesized netlist; the
tool fails if they disagree with the table). The library has no isolation cell,
so each is a plain AND on the always-on rail with `iso_n`; the clamp is 0.

| Output | Width | Clamp | Note |
|---|---|---|---|
| `reg_rdata` | 32 | 0 | |
| `str_data` | 32 | 0 | |
| `str_valid` | 1 | 0 | clamp 0 means no word is offered while off |
| `ht_alarm` | 1 | 0 | a latched alarm is masked while off and re-appears on wake; see open items |

66 AND2 cells in total.

## Sequences

Power-down: stop the retention clock, assert isolation, assert gated reset,
open the switch. Wake: close the switch, wait for the rail to be good (at least
`t_rail_settle`), release isolation, release gated reset, restart the retention
clock, then the start-up test runs from the gated reset values. Reset is
asserted before the rail comes up so no flop powers up unreset.

Rules (checked on the declared sequence below, and on the edge trace of the
gate-level run):

1. `ret_clk_off` before `pwr_off`; `pwr_off` only with isolation asserted.
2. `iso_release` only after `rail_good`.
3. `rst_release` only after `iso_release`.
4. `rail_good` only while reset is asserted; at least `t_rail_settle` after `pwr_on`.
5. `ret_clk_on` only after `rst_release`.
6. `pwr_on` at least `t_rail_decay` after `pwr_off`.

## Time budget and time-to-first-valid

The sequencing steps below count sample-clock cycles (the clock is the fixed
external sample clock, [DR-0012](../spec/decision-records/DR-0012-sampler-fixed-external-clock.md), so 500 us per cycle at the ratified 2000 bit/s).
The wake adds `t_rail_settle` plus the step cycles to a start-up test that
cannot be skipped, because the health-test window and the conditioner are
discarded. So every idle exit is a full start-up event: the digital total in
`sim/tools/time_to_first_valid.py` (1281 samples, 640.5 ms) plus the wake
latency the tool prints. The `check` output reports the figure; it is
**provisional** while rail settle and decay are placeholders. This does not
claim the README time-to-first-valid row is met or missed on wake; the row is
not edited.

## Does idle-with-state-retained still hold?

The README `Power` row defines idle as "register state retained". With this
scheme **configuration and the alarm are retained; data and run state are
not.** FIFO contents, conditioner state, the health-test window and the sticky
overflow flags are lost, and the section needs the full start-up test on every
wake. Whether that satisfies the row's wording is a ruling, not something this
change decides. It is raised for the operator on #700; no row, README table,
decision record or `docs/spec-row-status.md` is edited here.

## Open items (not verified here)

- **Switch parameters** (on-resistance, rail settling, decay, inrush) are
  placeholders until #707's evidence lands; the budget is provisional and this
  work is not complete until they are resolved.
- **Input side.** Only output crossings are modelled. Inputs (`reg_*`, `raw_*`,
  `ring_bit`, `str_ready`, `clk`) driven into an unpowered domain need a
  protection decision (hold low in the host, or input AND cells) that this check
  does not cover.
- **`ht_alarm` while off.** Clamped to 0; the alarm is retained and reappears on
  wake. If a visible alarm is required while off, the OR of the three retained
  latches would have to move onto the always-on rail.
- No klayout-tools verb checks power intent. `klt erc`/`klt power` are layout-only; `klt reset-coverage` is reset-only and rejects the Yosys-written netlist (escaped `$paramod` module name). The need is filed generically as 2AMLogic/klayout-tools#4479; until it lands the check here is the bespoke harness.

## Machine-readable intent

`sim/tools/power_intent_check.py` reads only this block.

```power-intent-json
{
  "netlist": "design/trng_top/trng_top.synth.v",
  "top": "trng_top",
  "retained": {
    "module": "trng_interface",
    "q_nets": ["ctrl_en", "ctrl_out_mode_raw", "fail_rct", "fail_apt", "fail_ring"]
  },
  "isolation": [
    {"port": "reg_rdata", "width": 32, "clamp": 0},
    {"port": "str_data", "width": 32, "clamp": 0},
    {"port": "str_valid", "width": 1, "clamp": 0},
    {"port": "ht_alarm", "width": 1, "clamp": 0}
  ],
  "timing": {
    "t_rail_settle_cycles": {"value": 20, "status": "placeholder", "source": "#707"},
    "t_rail_decay_cycles": {"value": 8, "status": "placeholder", "source": "#707"}
  },
  "sequence": {
    "power_down": [
      {"event": "ret_clk_off", "after_cycles": 1},
      {"event": "iso_assert", "after_cycles": 2},
      {"event": "rst_assert", "after_cycles": 2},
      {"event": "pwr_off", "after_cycles": 1}
    ],
    "wake": [
      {"event": "pwr_on", "after_cycles": 1},
      {"event": "rail_good", "after_rail_settle": true},
      {"event": "iso_release", "after_cycles": 2},
      {"event": "rst_release", "after_cycles": 2},
      {"event": "ret_clk_on", "after_cycles": 2}
    ]
  }
}
```
