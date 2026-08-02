* sampler-dff-reset-clocked -- does sampler_dff's asynchronous reset hold Q
* at 0 while the sample clock is RUNNING, not just while it is parked?
*
* Why this testbench exists (#53). sampler_dff's reset used to be brute
* force: pull devices that overrode both storage nodes whenever rst_n = 0,
* independent of clk, at the cost of a DC contention path against the input
* transmission gate (#48 measured it; see design/README.md "sampler_dff:
* why a transmission-gate master-slave DFF"). #53 replaced that with reset
* gated into the latches' own inverters, which removes the contention -- but
* moves the burden of proof: a gated reset acts through the loops, so
* whether Q stays at 0 through a clk EDGE is now a property of WHICH
* inverter is gated, not something the pull devices guaranteed outright.
* sim/tb/sampler-dff-reset-current-{xsv,xsb}/ hold clk at a DC level and so
* cannot see this; sim/tb/sampler-dff-setup-hold/ releases reset before the
* clock starts and so cannot either. This deck covers exactly that gap.
*
* Stimulus: rst_n is held LOW across three full clk periods (six edges,
* rising and falling) and released at 3.6 us, between edges. clk is the
* 1 MHz / 1 ps-edge clock sim/tb/sampler-dff-setup-hold/ uses, i.e.
* DR-0003's ratified 1 Mbps raw target.
*
* D IS HELD AT VDD, and that is the worst case for this mechanism, not a
* convenience: the disturbance to look for is the master handing the slave
* a value that disagrees with the reset state as clk rises, which requires
* the master's captured data to be 1. Tying D high forces that disagreement
* at EVERY rising edge rather than at whichever ones a toggling D happens to
* line up with. It is also literally xsv's condition in the shipped block
* (design/sampler_core.spice: `xsv vdd clk rst_n raw_valid vdd vss
* sampler_dff` -- the raw_valid path's D is wired to vdd), so the worst case
* here is also a real case, and xsb (D = xo) is bounded by it.
*
* Measured: the extreme excursion of q away from its reset value, and of the
* slave's storage node s away from its own, over the whole reset window
* (q_rst_max / s_rst_min), as an absolute voltage and as a fraction of the
* supply. Then two functional checks after release, so a cell that passed by
* being broken (stuck low, never capturing) would not pass: q must follow a
* D = 1 capture on the next rising edge (q_cap_v), and must still be at the
* reset value immediately before release (q_rel_v).

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 0 pulse(0 'vdd_val' 3.6u 1p 1p 10u 20u)
vclk clk 0 dc 0 pulse(0 'vdd_val' 0.5u 1p 1p 0.5u 1u)
vd d 0 dc 'vdd_val'

xdut d clk rst_n q vdd 0 sampler_dff

* mid-supply reference (measurement only)
bvth vth 0 v = 0.5*vdd_val
