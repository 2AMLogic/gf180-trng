* sampler-array-fs-sf -- the shipped ring array, XOR and sampler under the
* asymmetric MOS corners (fs, sf), deterministic, at the 1 Mbps target clock
* (issue #472).
*
* DUT: design/sampler_core.spice, instantiated WHOLE as `sampler_core` (the
* two buffered ring_ro11 rings, the XOR, and the four sampler_dff cells). Unlike
* sim/tb/sampler-array-digitize/ -- whose per-stage trnoise injection forced it
* to restate an older, un-buffered array wiring -- this deck needs no series
* noise source, so nothing is restated: the cell under test is the shipped one.
*
* WHAT THIS ANSWERS. DR-0006 dropped fs/sf from the jitter campaign because
* nothing downstream was sensitive to ring duty cycle. The edge-triggered
* sampler now is, and sim/tb/sampler-dff-setup-hold/ covers it only in
* isolation (ideal data edges, no ring, no XOR). This deck puts the ring
* array's real, corner-skewed waveform on the sampler's D input and asks, at
* each PVT point and at several clock phases:
*   - ring high/low durations and duty cycles (ro1, ro2: the buffered outputs
*     the XOR and the liveness samplers actually see);
*   - XOR swing and the high/low pulse widths that reach D;
*   - reset: raw_valid and raw_bit held low through reset, including across a
*     clock edge that arrives while reset is still asserted;
*   - raw_valid: low through reset, high from the first edge after release;
*   - capture: the level of D (xo) at the clock edge, and the settled raw_bit
*     at +8 ns, +50 ns and +300 ns after the edge.
*
* WHAT IT DOES NOT ANSWER. It is deterministic: no noise, no mismatch, so a
* bit pattern here is NOT randomness and is never read as such. It makes no
* entropy, jitter, silicon or post-layout claim. The decision thresholds and
* the checker are in sim/tools/fs_sf_capture.py and were fixed before any run.
*
* Circuit body for `klt sim`: no .control/.end. klt sim appends the corner's
* .lib/.temp cards, the .meas cards from the request, an `alter` for every
* key of the request's corners.supply_v, and the analysis. The keys that move
* together BY INDEX are DC sources (alter reaches a source's value, not an
* already-evaluated .param), all named in the request:
*   vsupply  the supply, volts
*   vph      clock phase offset, seconds (the reproducible phase sweep)
*   vrel     reset-release time, seconds (default 0.5 us; the negative control
*            sets it far beyond tstop so reset is never released)
*   vthw     clock high time, seconds (default 0.5 us = 50 % duty; the second
*            negative control sets 20 ps so the clock never swings far enough
*            to operate the sampler's transmission gates)
*
* Stimulus timeline at the defaults (period 1 us = 1 Mbps, edge 1 ns):
*   0       rings enabled (enable tied high; each ring's first node kicked by
*           .ic -- no noise source exists to start them)
*   0.3 us  clock edge 0 + vph: reset still asserted (reset must dominate)
*   0.5 us  reset releases
*   1.3, 2.3, 3.3 us  clock edges 1..3: captures after release
* The clock is a B-source (not a PULSE card) so that its phase is a per-unit
* DC value; the transmission-gate edges are 1 ns trapezoids resolved by the
* request's 10 ps tmax.

.include "../../../design/sampler_core.spice"

* switches design.ngspice sets (its values, verbatim)
.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0
.param tclk=1u tclk0=0.3u tr=1n

vsupply vsup 0 dc 3.3
vph ph 0 dc 0
vrel rel 0 dc 0.5u
vthw thw 0 dc 0.5u

een en 0 vsup 0 1
vtr vdd vsup dc 0
vr1 vddr1 vsup dc 0
vr2 vddr2 vsup dc 0

xs en en vddr1 vddr2 vdd 0 clk rst_n raw_bit raw_valid ring_bit1 ring_bit2 sampler_core

* external fixed-rate clock, phase-shiftable per unit (max/min clamps: ngspice's
* limit() in a B-source is not a clamp): trapezoid, rises at
* tclk0 + vph + k*tclk, high for vthw, edge time tr.
bclk clk 0 v = (time >= tclk0 + v(ph)) ? v(vsup)*(max(0,min(1,((time - tclk0 - v(ph)) - tclk*floor((time - tclk0 - v(ph))/tclk))/tr)) - max(0,min(1,(((time - tclk0 - v(ph)) - tclk*floor((time - tclk0 - v(ph))/tclk)) - v(thw))/tr))) : 0
brst rst_n 0 v = v(vsup)*max(0, min(1, (time - v(rel))/100p))

* measurement-only probes: mid-supply, and the 25 % / 80 % supply levels that
* bracket the clock edge's transit through the transmission gates' switching
* region (xo is read at all three clock levels).
bvth vth 0 v = 0.5*v(vsup)
bvlo vlo 0 v = 0.25*v(vsup)
bvhi vhi 0 v = 0.80*v(vsup)

.ic v(xs.xdut.xr1.n1)=0
.ic v(xs.xdut.xr2.n1)=0
