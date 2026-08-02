* sampler-dff-reset-current-xsb -- mean supply current of sampler_dff's
* xsb instance (design/sampler_core.spice: raw_bit path, D = xo, the
* entropy source's oscillating XOR node) while reset is asserted and clk
* sits at the phase that leaves the input path conducting.
*
* Mechanism this stimulus exists to interrogate (#48, design/README.md
* "sampler_dff: why a transmission-gate master-slave DFF"): whenever
* rst_n = 0 AND clk = 0, sampler_dff's input transmission gate
* (XMtdp/XMtdn) is transparent. In the cell as #48 measured it, an
* async-reset pulldown (XMrm) was ON at the same time, so whatever drives D
* had a resistive path to vss. xsb's D is xo, which toggles continuously
* (1.03-2.30 GHz over the measured PVT grid,
* sim/characterization-supply-current-and-leakage.md), so unlike xsv (D held
* at vdd, sim/tb/sampler-dff-reset-current-xsv/) that path conducted only
* for roughly the fraction of each xo period that D was high, not
* continuously.
*
* #53 removed that path -- reset is now gated into the two latches' own
* inverters (NAND2s taking rst_n), with no reset device on a storage node
* at all. At this bias the post-#53 cell therefore has no DC path from D to
* vss, AND its master forward gate output mb is held HIGH by reset, so D's
* toggling no longer switches an internal node either: node m still follows
* D through the transparent input TG, but that charge comes from and
* returns to the same source (vd, integrated here alongside vdd), so it
* nets out over a period. The testbench is UNCHANGED across that fix --
* deliberately, so the before/after record sets are the same measurement on
* two cells rather than a comparison of methods.
*
* D is driven here by an IDEAL square wave, not the real ro_array_core --
* deliberately, for two reasons. First, xo's frequency is itself a
* function of PVT, so tying this testbench to "the" xo frequency would
* conflate two different PVT dependences (the path's own conduction, and
* the ring's oscillation speed) in one number. Second, and more directly:
* the current the pre-#53 path drew was set by D's INSTANTANEOUS logic
* level, not by how fast D got there. The input TG's and reset pulldown's
* ON resistances are a few kOhm at most and node m carries only device
* parasitic capacitance (no explicit load, unlike a ring stage) -- that RC
* is far below any period this repo's rings run at, so the mean current
* over a half-period is the same as the DC current at that D level
* regardless of drive frequency. That was checked, not assumed: on the
* pre-#53 cell the record's first- and second-half currents
* (i_reset_xsb_first_a vs i_reset_xsb_last_a) agree to the precision
* ngspice's charge integrator carries, which is what "no start-up
* transient, no frequency dependence" looks like in the numbers. A
* representative 500 ps period (2 GHz, inside the measured xo range) is
* used at every corner instead of that corner's own ring frequency.
*
* On the post-#53 cell that first-half/second-half agreement is NOT a
* meaningful check any more and must not be read as one: with the
* conduction path gone, the total is nanoamp-scale, so the two halves
* differ by a large FRACTION of a very small number (the integrator's own
* numerical residue, not a physical transient). The magnitude is the
* result there; the halves' ratio is not.
*
* WHY BOTH `vdd` AND `vd` ARE INTEGRATED. On the pre-#53 cell, when D was
* high, current flowed IN through the `d` pin (from whatever drives it),
* through the input TG, into the reset pulldown, to vss -- it did NOT
* return through the DUT's own `vdd` pin. (Post-#53 there is no such path,
* but counting both branches is still the only way to see that: a
* measurement that ignored `vd` could not tell "no current" from "current
* that left through the other source".) In the real chip D = xo is driven by xor2's output stage
* (design/sampler_core.spice: `xa1 ro1 ro2 xo vdd vss xor2`), which is
* powered from the SAME vdd rail this cell is, so that current is real
* vdd-rail current even though it does not cross this cell's own vdd pin.
* Modeling D with an ideal source `vd` disconnected from `vdd` reproduces
* the D=vdd waveform without reproducing that shared rail -- so `vd`'s own
* branch current has to be counted alongside `vdd`'s to get the total
* current this mechanism draws from the rail, or the D-high-phase
* contribution would be silently attributed to `vd` and vanish from the
* measurement (checked: without it, this record read ~30x low against
* sim/tb/sampler-dff-reset-current-xsv/'s directly-tied-to-vdd case, for
* exactly this reason). This is the ideal-buffer approximation for xo's
* driver named in the tb.json caveats: zero source impedance, powered from
* vdd, which is what an unloaded static CMOS output stage looks like to
* first order.
*
* clk and rst_n are held low for the ENTIRE window: the worst-case
* (maximum-duration) phase relationship #48 describes, not a claim about
* how long reset is actually asserted in any power-on sequence (#26's
* question, not this testbench's).
*
* Method: the same charge-integration technique sim/tb/ro-inv-05stage-power/
* uses, with TWO current-mirror sources (fq/fqd) both accumulating into the
* SAME integrator node, so v(qint) is the charge drawn from vdd+vd combined
* since t=0, scaled by 1/cq; rq gives the integrator node a DC path
* (tau = 1000 s, i.e. droop is not a measurable effect over this window).
* The integrator node is named "qint", NOT "q" -- sampler_dff's own output
* pin is already called `q` (see `xdut` below), and reusing that name for
* the integrator would silently short the two nodes together instead of
* erroring, corrupting every measurement in this deck. The window is nine
* 500 ps periods; the first is discarded as settling (D's own edge is
* 1 ps, and the TG/pulldown path has no meaningful start-up of its own,
* but the first period is dropped anyway for the same reason
* ro-inv-05stage-power drops its first two ring periods -- so this record
* is not the one place in the repo that skips the convention).

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 0
vclk clk 0 dc 0
vd d 0 dc 0 pulse(0 'vdd_val' 0 1p 1p 250p 500p)

xdut d clk rst_n q vdd 0 sampler_dff

* charge integrator: v(qint) = (1/cq) * integral of (current drawn from
* vdd) + (current drawn from vd) -- see header for why both are needed.
fq qint 0 vdd 1
fqd qint 0 vd 1
cq qint 0 1n
rq qint 0 1e12
.ic v(qint)=0
