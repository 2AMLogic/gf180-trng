# ro-ring11-ring2-pex — ring2 schematic vs. extracted, as a native `klt pex` report

Issue [#423](https://github.com/2AMLogic/gf180-trng/issues/423). The ring1
comparison in [`../ro-ring11-pex/`](../ro-ring11-pex/README.md) does not
establish anything about ring2, which is a separately sized physical
oscillator (`xr2`, `wstv=0.240u`, versus ring1's `wstv=0.220u` in
`design/ro_array_core.spice`). This is the same comparison, paired, over
`layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds`.

**Status: measured and published.** The 27-corner paired comparison ran on the
batch fleet and is committed under
[`signoff/evidence/post-layout/ring2/`](../../../signoff/evidence/post-layout/ring2/)
(native envelope, extracted netlist, `publication.json`; `producer_build` 0.9.2,
`body_bias.status` `biased`). Across the grid the extracted period is
113.7-130.8 % above the schematic's, average supply current 12.2-14.8 %, and
output swing -6.1 to -4.9 %; the envelope's `body_bias.status` is `biased`
because ring2's layout carries the #705 well and substrate ties, so the
floating-PMOS-well counterfactual does not apply to it. This is a diagnostic
under ring2's own isolation, unloaded output and determinism disclosures (see
"What this does not claim"); it is not a manifest citation and makes no
silicon, entropy or timing claim. The full record, including fleet job ids and
the discarded first submission, is
[`sim/records/2026-11-15-ro-ring11-ring2-pex-attempt-03.md`](../../records/2026-11-15-ro-ring11-ring2-pex-attempt-03.md).

History: the first submission attempt (two tries, `klayout-tools==0.6.0`; klt-pin: historical)
was refused by the fleet for capacity (`8 instance(s) already running + 1
requested exceeds BATCH_MAX_CONCURRENT_INSTANCES=8`, then `no capacity in any
of the 30 pools`). The grid was deliberately not run locally.

A second attempt (#476, 2026-10-10, same pin) got past capacity. Both fleet
jobs ran, but all 54 grid units (27 corners x 2 sides) errored with no
measurement. The 0.6.0 batch client uploads only the testbench body and the
request, not the DUT the body `.include`s, so on the fleet neither side has a
`ro_ring11_ring2` subcircuit. The fleet runner also reports klt 0.5.0. A
client that stages includes (0.7.0) is refused by that runner, and the
publisher then accepted only the 0.6.0 pin. Nothing was published. The jobs, logs,
errored envelope and one single-corner local debug probe (showing the fixture
simulates) are in
[`sim/records/2026-10-10-ro-ring11-ring2-pex-attempt-01.md`](../../records/2026-10-10-ro-ring11-ring2-pex-attempt-01.md).
A third attempt (2026-11-05, klt 0.9.0 client against the klt 0.9.0 fleet
runner) measured the whole 27-corner grid on both sides (81 delta rows, none
errored), but stayed unpublished: the publisher then still accepted only the
0.6.0 pin, and which pin covers a ring2 result was an open operator decision
(DR-0026). That envelope also described the pre-#826 floating-well layout,
which the current inputs no longer contain. The record is
[`sim/records/2026-11-05-ro-ring11-ring2-pex-attempt-02.md`](../../records/2026-11-05-ro-ring11-ring2-pex-attempt-02.md).
DR-0026's 2026-11-09 amendment settled the pin question (no single producer
of record; each record names its release), leaving the publication to the
2026-11-15 run above.

| File | Role |
|---|---|
| `request.json` | the `klt sim` request: byte-for-byte ring1's apart from the testbench name (27 corners, `tran 10p 1300n`, the same three `.meas` rows); `signoff/check.py` enforces that |
| `tb_ro_ring11_ring2_pex.sp` | the circuit body; its `xdut` line carries ring2's own extraction port order |
| `ro_ring11_ring2_schematic.spice` | generated schematic DUT: `ro_ring11` at the `xr2` sizing, under ring2's extraction header, subcircuit `ro_ring11_ring2` |
| `../ro-ring11-pex/build_dut.py --ring ring2` | generates / `--check`s / `--check-source`s / `--verify-netlist`s the DUT |

Ring2's extracted port order is not ring1's (the ring output is the first
port, not the twelfth), so the testbench and DUT header are derived from ring2's
own extracted device geometry, not copied. The DUT sizing is read from the
`xr2` instance, and `build_dut.py` refuses a DUT, header, instance or restated
sizing that would make ring2 carry ring1's widths, an extraction whose
`.SUBCKT` is not `ro_ring11_ring2`, a port that drives no gate, or two ports
tied on position.

## Reproducing the run

```bash
# The fleet's klayout-tools release, in a throwaway environment (do not
# install it on a shared host). Unpinned by convention (DR-0026, 2026-11-09
# amendment: no producer pin; each record names its release -- attempt 03
# used the 0.9.2 release).
export KLT="uvx --from klayout-tools --with klayout==0.30.10 klt"

python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check-source   # offline
python3 sim/tb/ro-ring11-pex/build_dut.py --ring ring2 --check          # re-extracts (klt extract only)

# 27 corners x 2 sides: a SPICE grid, so submit it to the batch backend.
# pass --backend explicitly; the request already declares capacity_wait_s.
python3 signoff/publish_item7_analog.py --ring ring2 --backend batch
# in an environment whose `klt` is the 0.8.0 grader pin (check.py --write re-pins
# the item 1/2/9/10 inventories when tracked docs move)
python3 signoff/check.py
```

The publisher refuses to publish a stale fixture, a response that does not
name a tagged klt release, a pin-count or flat-DUT mismatch, or an
`incomplete` verdict (a declared corner/row unmeasured) unless
`--allow-incomplete` is given. It
publishes to `signoff/evidence/post-layout/ring2/` (native envelope byte for
byte, the extracted netlist, `publication.json` pinning input hashes, the
consumed-source identity, the port map, the verdict and the body-bias status).
A failing run is published as it stands. `signoff/check.py` recomputes the recorded verdict from
the envelope and request on every run and checks ring2 independently of ring1.

## What this does not claim

- **Not a manifest citation.** T1 item 7's `7.analog` stays ring1's; the
  manifest is never touched by `--ring ring2`, and `check.py` fails if it cites
  ring2 evidence. A separately reviewed change would be needed to cite it.
- **Isolation, unloaded output.** One ring on its own supply with `en` tied to it;
  `ro` carries no buffer or load, and nothing couples to ring1 or any block.
- **Deterministic.** Noiseless transient, no mismatch. The rows (period, average
  supply current, output swing) carry no limits; a row's `pass` means "measured
  on both sides". Nothing here estimates entropy, bias or jitter, and nothing is a
  full-chip timing or silicon-performance claim.
- **Bodies.** Since #705 ring2's layout carries the same well and substrate taps
  as ring1's, so every bulk in the extraction ties to a supply (`vddr`/`vss`), as the
  schematic side does, and the extraction promotes no `vsubs` port. The envelope's
  `body_bias.status` is recorded in `publication.json`. The testbench holds the
  netlist's `.GLOBAL` substrate reference `vsubs` at 0 V.
