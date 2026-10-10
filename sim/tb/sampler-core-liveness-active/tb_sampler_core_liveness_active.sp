* sampler-core-liveness-active -- what the two shipped per-ring liveness
* samplers (xsr1, xsr2) cost while the array runs, resolved on their own
* supply branches, plus what they do to the array that drives them (issue #463).
*
* WHY THIS DECK EXISTS. The whole-block active-power ledger
* (sim/tools/power_rollup.py) accounts for the array, the raw-bit/valid sampler
* pair (xsb, xsv) and the digital section. design/sampler_core.spice also
* instantiates xsr1 and xsr2, whose D inputs are the BUFFERED ring outputs
* ro1/ro2 (DR-0016's integration amendment; #65). Those two flops had no
* evidence term. The older sim/tb/ring-liveness-tap-power/ measured a tap on the
* UNBUFFERED array at a 10 ns clock; it is not a drop-in for the shipped
* topology and is not reused here.
*
* DUT: design/sampler_core.spice (include below). The deck restates the
* sampler_core wiring -- ro_array_core plus xsb, xsv, xsr1, xsr2 with the same
* port connections -- because sampler_core has ONE vdd pin and the point of the
* deck is to put each flop on its own sense-source branch. Port-for-port the
* restated instances are the shipped ones (sim/tests pins this against the
* netlist). The array is the shipped buffered one (ro_buf on ro1/ro2).
*
* TWO ARRAYS IN ONE RUN. `xdut` is the full shipped wiring (all four flops).
* `xctl` is the same array with only xsb and xsv (the pre-integration wiring)
* and no xsr taps. Both are deterministic, start from identical initial
* conditions and see the same supply and clock, so the difference of their
* ring and tree charges is the loading the xsr taps add to the buffered ring
* outputs -- a like-for-like in-run control, not a comparison across records.
*
* WHAT IS MEASURED (raw charges; the arithmetic is sim/tools/
* liveness_sampler_power.py, so nothing is hidden in a .meas expression):
*   q_*: charge delivered on each branch between the 2nd and 6th rising ring
*        crossings of mid-supply (four ring periods), read at those crossings
*        exactly as sim/tb/ro-array-core-pvt-q/ does. xsr1 and the tree/xsb/xsv
*        use ring 1's window, xsr2 and ring 2 use ring 2's.
*   t*:  the crossing times (window length and ring frequency).
* The clock term is removed by SUBTRACTION INSIDE THE RUN: xsv's D is tied high,
* so its window charge is a pure clock-cycle charge over the same window and the
* same clock phases xsr sees. (xsr1 - xsv) is the ring-data charge. xsr's own Q
* toggles and xsv's does not; that output charge is left inside the data term,
* which over-states a per-clock-cycle cost by scaling it with the ring rate -- a
* conservative direction, stated in tb.json.
*
* WHAT IT DOES NOT ANSWER. Not a 1 MHz transient (a 1 us period would need a
* ~80x longer run for no added information: the quantities are per-event charges
* and the tool applies the declared sample-clock rate). Not leakage -- idle is
* sim/tb/sampler-core-idle-leakage/'s, which already runs on the whole
* sampler_core and therefore already contains xsr1/xsr2's leakage. Not
* post-layout. No entropy claim.
*
* Circuit body for `klt sim`: no .control/.end. klt sim appends the corner's
* .lib/.temp cards, the .meas cards from the request and the analysis. The
* supply is the DC source vsupply (klt alters it per unit).

.include "../../../design/sampler_core.spice"

.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0
.param tclk=10n tr=200p

vsupply vsup 0 dc 3.3
een en 0 vsup 0 1

* ---- measurement clock: 10 ns period, 50 % duty, from 5 ns. A LOCAL fast
* ---- clock so a few whole cycles fit in the window; NOT DR-0012's 1 MHz.
bclk clk 0 v = (time < 5n) ? 0 : v(vsup)*max(0, min(1, ((time-5n) - tclk*floor((time-5n)/tclk))/tr) - max(0, min(1, (((time-5n) - tclk*floor((time-5n)/tclk)) - tclk/2)/tr)))
brst rst_n 0 v = v(vsup)*max(0, min(1, (time - 2n)/100p))

* ---- tapped array: the full shipped wiring ------------------------------
vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0
vsb vsup vsbp dc 0
vsv vsup vsvp dc 0
vs1 vsup vs1p dc 0
vs2 vsup vs2p dc 0
xdut en en vddr1 vddr2 vdd 0 xo ro1 ro2 ro_array_core
xsb xo clk rst_n qb vsbp 0 sampler_dff
xsv vsvp clk rst_n qv vsvp 0 sampler_dff
xsr1 ro1 clk rst_n qr1 vs1p 0 sampler_dff
xsr2 ro2 clk rst_n qr2 vs2p 0 sampler_dff

* ---- control array: same array, xsb/xsv only, no xsr taps ----------------
vcr1 vsup cvddr1 dc 0
vcr2 vsup cvddr2 dc 0
vctr vsup cvdd dc 0
vcsb vsup csbp dc 0
vcsv vsup csvp dc 0
xctl en en cvddr1 cvddr2 cvdd 0 cxo cro1 cro2 ro_array_core
xcsb cxo clk rst_n cqb csbp 0 sampler_dff
xcsv csvp clk rst_n cqv csvp 0 sampler_dff

* ---- ideal charge integrators (same technique as ro-array-core-power) ----
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12
fqsb qsb 0 vsb 1
cqsb qsb 0 1n
rqsb qsb 0 1e12
fqsv qsv 0 vsv 1
cqsv qsv 0 1n
rqsv qsv 0 1e12
fqs1 qs1 0 vs1 1
cqs1 qs1 0 1n
rqs1 qs1 0 1e12
fqs2 qs2 0 vs2 1
cqs2 qs2 0 1n
rqs2 qs2 0 1e12
fcq1 cq1i 0 vcr1 1
ccq1 cq1i 0 1n
rcq1 cq1i 0 1e12
fcq2 cq2i 0 vcr2 1
ccq2 cq2i 0 1n
rcq2 cq2i 0 1e12
fcqt cqt 0 vctr 1
ccqt cqt 0 1n
rcqt cqt 0 1e12
fcsb cqsb 0 vcsb 1
ccsb cqsb 0 1n
rcsb cqsb 0 1e12
fcsv cqsv 0 vcsv 1
ccsv cqsv 0 1n
rcsv cqsv 0 1e12

bvth vth 0 v = 0.5*v(vsup)

.ic v(xdut.xr1.n1)=0
.ic v(xdut.xr2.n1)=0
.ic v(xctl.xr1.n1)=0
.ic v(xctl.xr2.n1)=0
.ic v(q1)=0 v(q2)=0 v(qt)=0 v(qsb)=0 v(qsv)=0 v(qs1)=0 v(qs2)=0
.ic v(cq1i)=0 v(cq2i)=0 v(cqt)=0 v(cqsb)=0 v(cqsv)=0
