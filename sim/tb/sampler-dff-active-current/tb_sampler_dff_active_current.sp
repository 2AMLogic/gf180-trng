* sampler-dff-active-current -- what a running sampler_dff costs, resolved
* into the two events that actually cause the cost: one `D` transition and
* one clock cycle. Both instances sampler_core wires (`xsv`, whose D is tied
* to its own vdd, and `xsb`, whose D is driven) are measured together in one
* run, on separate supply branches, so their individual and combined
* contributions come off the same PVT point.
*
* Why this testbench exists. design/README.md's "The sampler (#9)" section
* names the gap: sim/tb/sampler-dff-reset-current-{xsv,xsb}/ hold clk AND
* rst_n at fixed DC levels (they characterise the reset window, not running
* operation), and sim/tb/sampler-dff-setup-hold/ and
* sim/tb/sampler-dff-reset-clocked/ run a clock but measure propagation delay
* and reset-excursion voltage, not current. Nothing in this repository reports
* what the cell draws while it is doing its job -- clocked, reset released,
* digitising a moving input. Issue #14's active-power rollup needs that number
* rather than an assumption that it is zero.
*
* DUT: two instances of design/sampler_core.spice's `sampler_dff`, wired
* exactly as sampler_core.spice wires them -- `xsv vdd clk rst_n raw_valid vdd
* vss`, `xsb xo clk rst_n raw_bit vdd vss` -- each on its own supply branch
* (the vsup/vrN sense-source split sim/tb/ro-array-core-power/ uses to separate
* per-ring current).
*
* ---------------------------------------------------------------------------
* THE METHOD, AND WHY IT IS NOT "SIMULATE ONE CLOCK PERIOD"
* ---------------------------------------------------------------------------
*
* The obvious deck -- run one whole 1 us sample-clock period and divide the
* charge by 1 us -- was tried first and is the wrong instrument for two
* independent reasons.
*
* 1. It cannot be run. `D` here stands in for `xo`, which
*    sim/tb/ro-array-core-pvt-q/ measures at 3.1e8 to 9.6e8 transitions per
*    second across the grid. Simulating a microsecond of that is ~2000 D
*    periods inside one clock period; measured cost is minutes to hours of
*    ngspice per PVT point, for a 45-point grid.
*
* 2. Even if it could, it would bake in ONE data rate. The rate that matters
*    is corner-dependent and is already measured, per corner, by
*    sim/tb/ro-array-core-pvt-q/ (`xo_trans_per_s`). Freezing a single
*    idealised rate into this deck would conflate the CELL's PVT dependence
*    with the ARRAY's -- and, at the 2 GHz idealisation the reset-current
*    decks use, would overstate the real worst-case rate by ~4x.
*
* So this deck measures ENERGY PER EVENT and leaves the rates to the rollup.
* That is the same decomposition sim/tb/ro-array-core-power/ already uses when
* it reports `e_cycle_r1_j` and `c_eff_node_r1_f` alongside a current, and it
* is valid for the same reason: CMOS switching energy per event is set by the
* node capacitance and the supply, not by how often the event happens, once
* the node is allowed to settle between events. Every window below is at least
* two D periods long and every event in it completes inside the window.
*
* Three quantities, and why each needs its own window:
*
*   q_d_open   charge per D transition with clk LOW. The master transmission
*              gate is transparent (XMtdp's gate is clk, XMtdn's is clkb), so
*              D drives m -> mb -> mc. This is the dominant term and the
*              reason the sampler is not free: the flop burns energy at the
*              ENTROPY NODE's rate, not at the sample clock's, for the half of
*              every clock period in which its master is open.
*   q_d_shut   charge per D transition with clk HIGH. The master TG is off and
*              D only works against its own diffusion capacitance. Kept
*              separate rather than assumed negligible.
*   q_clkcyc   charge per complete clock cycle. This is the term that scales
*              with the 1 MHz sample clock rather than with xo. It is read off
*              `xsv` -- the instance whose D is tied to vdd and therefore never
*              toggles -- so it is a DIRECT measurement over exactly one clock
*              period with nothing to subtract, not a residual. The deck runs
*              the clock 500x faster than the real one purely so a whole cycle
*              fits in a short transient; that rescaling is legitimate for
*              exactly the reason above, and the rollup multiplies the result
*              by the REAL 1 MHz clock rate, never by 50 MHz.
*
* Because `xsv`'s D is static and `xsb`'s is not, the two instances are not
* redundant: `xsv` isolates the clock term and `xsb` carries the data term, and
* the real sampler_core contains one of each.
*
* Timing (all edges 1 ps, matching the existing sampler decks):
*   rst_n : 0 -> 1 at 8 ns, between clock edges, well clear of every window.
*   clk   : 21 ns period, 10 ns high. Rises at 20, 41, 62; falls at 30, 51.
*   d     : 2 ns period, 50 % duty, transitions on every HALF-integer
*           nanosecond (0.5, 1.5, 2.5, ...). 1.0e9 transitions/s --
*           deliberately just above the grid maximum xo actually reaches
*           (9.6e8/s at ff/-40 C/3.63 V per sim/tb/ro-array-core-pvt-q/), so
*           the settling assumption above is checked at a harder rate than the
*           real one. The half-nanosecond offset keeps every D edge away from
*           every clock edge: a D transition landing exactly on a capture edge
*           would put the flop in the aperture it is deliberately not being
*           asked about here (sim/tb/sampler-dff-setup-hold/ owns that).
*
* WHY THE CLOCK PERIOD IS 21 ns AND NOT 20. With a 20 ns period every rising
* edge would land at the same phase of the 2 ns D waveform, so `xsb` would
* capture the identical value forever and its output would never toggle -- the
* deck would silently never exercise, or witness, a capture. 21 ns is an odd
* number of D half-periods, so consecutive captures alternate (D is low at the
* 20 ns edge and high at the 41 ns edge) and window C below contains a real
* 0 -> 1 capture on `xsb`. The 10/21 duty that follows is NOT a claim about the
* real clock: the deck measures the open- and shut-phase D charges separately
* and the rollup weights them by the REAL 50/50 duty, so this deck's own duty
* cancels out of everything except window C's internal cross-check.
*
* Windows (every one an exact whole number of D periods, at integer
* nanoseconds, i.e. offset half a D period from every D edge so no transition
* is clipped at a boundary):
*   A  [22 ns, 28 ns]  clk HIGH, master shut     -> 6 D transitions
*   B  [32 ns, 38 ns]  clk LOW, master open      -> 6 D transitions
*   C  [32 ns, 53 ns]  exactly one clock period  -> 21 D transitions, 11 with
*                      the master open and 10 with it shut, plus one clk
*                      rising edge (41 ns) and one falling edge (51 ns), both
*                      wholly interior to the window.
*
* Every window opens at least 2 ns after the clock edge that precedes it, so
* the clock's own switching transient is not counted twice into A or B.
*
* Sign convention: fq1/fq2 are driven by the branch SENSE sources vr1/vr2, the
* construction design/README.md's "Reading the recorded currents" documents as
* reporting charge delivered INTO the branch, i.e. negative under ngspice's
* branch-current sign convention. tb.json negates so every recorded q_*/e_*
* value is a positive magnitude, consistent with every other record here.

vsup vsup 0 dc vdd_val
vclk clk 0 dc 0 pulse(0 vdd_val 20n 1p 1p 10n 21n)
vrst rst_n 0 dc 0 pulse(0 vdd_val 8n 1p 1p 10u 20u)
vd d 0 dc 0 pulse(0 vdd_val 0.5n 1p 1p 1n 2n)

vr1 vsup vddv dc 0
vr2 vsup vddb dc 0

xsv vddv clk rst_n qv vddv 0 sampler_dff
xsb d clk rst_n qb vddb 0 sampler_dff

* xsv's charge integrator: its own branch only. D and vdd are literally the
* same net on this instance (design/sampler_core.spice ties them), so whatever
* flows in through the D pin is already inside vr1.
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
.ic v(q1)=0

* xsb's charge integrator: its supply branch (vr2) PLUS its D pin (vd), summed
* into one node -- sim/tb/sampler-dff-reset-current-xsb/'s header argues why
* both are needed when D is driven from outside the branch.
fq2 q2 0 vr2 1
fq2d q2 0 vd 1
cq2 q2 0 1n
rq2 q2 0 1e12
.ic v(q2)=0
