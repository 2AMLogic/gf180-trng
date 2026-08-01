* sampler-dff-setup-hold -- sampler_dff alone, at the real target clock rate.
*
* DUT: the sampler_dff cell of design/sampler_core.spice, exported from
* design/xschem/sampler_dff.sch by design/netlist.py. Nothing about the
* cell is redefined here; this fragment biases it, clocks it, and drives D.
*
* Why this testbench exists. sim/tb/sampler-array-digitize/ demonstrates
* the sampler on a real, noisy analog xo swing, but at a clock frequency
* scaled up from the 1 Mbps target for transient-noise cost reasons (see
* that testbench's own header). This testbench answers the complementary,
* cheaper question DR-0012 leaves to it: does sampler_dff itself resolve
* correctly at the REAL 1 Mbps clock period, across the full PVT grid? xo
* swings rail to rail with fast edges (design/README.md), so D here is an
* ideal 1 ps digital transition -- this testbench characterizes the
* FLIP-FLOP's own setup/hold/metastability behavior in isolation from the
* ring's analog jitter physics, which is what the original issue's "the
* sampling flip-flop's metastability behavior is part of the entropy
* story, not just a hazard" note is about.
*
* Because sampler_core.clk is a fixed external clock (DR-0012), meeting
* DR-0003's raw-rate row reduces to this testbench's question: does the
* sampler resolve correctly at the target clock rate, at every corner? A
* clock with no relationship to either ring makes R_raw = f(clk) by
* construction, so no multi-cycle rate measurement is needed -- only this.
*
* ---- the seven clock edges -------------------------------------------
* Each stressed edge is preceded by a clean, generous-margin edge that
* drives Q to a KNOWN state, so that the stressed edge's outcome is
* readable as a change rather than being confounded with "Q happened to
* already be there". Without those re-arming edges a stressed edge that
* captured nothing at all would be indistinguishable from one that
* captured correctly.
*
*   edge 1 (0.3 us): D settled '1' since 0.05 us. Q: 0 -> 1.
*                    Generous margin. Gives the RISING clk-to-Q delay.
*   edge 2 (1.3 us): D settled '0' since 0.8 us. Q: 1 -> 0.
*                    Generous margin. Gives the FALLING clk-to-Q delay,
*                    and re-arms Q at 0 for edge 3.
*   edge 3 (2.3 us): D's 1 ps rise to '1' is centred exactly on the clk
*                    edge -- zero setup AND zero hold simultaneously, the
*                    classic metastability stress. Either resolution (0 or
*                    1) is a correct outcome for a flip-flop at zero
*                    margin; what this testbench asks is whether it
*                    resolves to a RAIL, and how fast.
*   edge 4 (3.3 us): D settled '0' since 2.8 us. Q -> 0.
*                    Generous margin; re-arms Q at 0 for edge 5.
*   edge 5 (4.3 us): D's 1 ps rise to '1' completes 59 ps BEFORE the edge
*                    -- a marginal but non-zero setup margin, roughly half
*                    this cell's own clk-to-Q delay, i.e. inside the region
*                    where the master latch is still resolving.
*   edge 6 (5.3 us): D settled '0' since 4.5 us. Q -> 0.
*                    Generous margin; re-arms Q at 0 for edge 7.
*   edge 7 (6.3 us): D's 1 ps rise to '1' completes 500 ps before the edge
*                    -- a comfortable but not lavish setup margin.
*
* Edges 5 and 7 together BRACKET the cell's setup time rather than merely
* probing it: whichever of them captures and whichever does not places the
* setup time inside a stated interval at that corner, which is a number
* #26 (pin/timing budget) and #13 can use. Both are recorded as raw
* voltages, so a reader draws the bracket rather than trusting a verdict
* this deck did not make.
*
* Q is read 1 ns, 10 ns and 100 ns after each stressed edge rather than
* compared against a pass/fail threshold: this testbench reports numbers,
* not a verdict (sim/README.md). A cell that failed to resolve would show
* a mid-rail value at +1 ns still mid-rail at +100 ns; one that resolved
* slowly would show the three values walking toward a rail. The recorded
* *_drift_v measurements are exactly that walk (value at +100 ns minus
* value at +1 ns), and the *_rail_dev_v measurements are the distance from
* the nearer rail at +100 ns -- a number a reader can compare against zero
* without knowing this deck's timing.
*
* bvth is a measurement-only probe: a mid-supply reference so that
* `meas ... when v(x)=v(vth)` finds a crossing at any supply without a
* hard-coded trip voltage. It is the same device sim/tb/ro-array-core-power/
* uses, and it exists because ngspice's `meas ... val=` takes a number, not
* a parameter expression -- `val='0.5*vdd_val'` is rejected outright.
*
* Print step is 100p rather than this repo's usual 1p: at a 4.5 us tstop
* (needed to fit five real 1 us clock periods) 1p would emit 45x more data
* than any existing record for no measurement benefit -- ngspice's LTE
* still takes whatever internal step the solver needs near the fast (1 ps)
* D and clk transitions regardless of the print step; only the OUTPUT
* sampling density changes.
*
* Reset: rst_n is held low until 0.1 us, so every run starts from the
* cell's defined power-on state (Q = 0) rather than from whichever way the
* DC solver happened to resolve the storage loops. q_rst_v records that
* state; a non-zero q_rst_v would mean the asynchronous reset did not take.

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 0 pulse(0 'vdd_val' 0.1u 1p 1p 10u 20u)
vclk clk 0 dc 0 pulse(0 'vdd_val' 0.3u 1p 1p 0.5u 1u)
vd d 0 dc 0 pwl(
+ 0          0
+ 0.05u      0
+ 0.050001u  'vdd_val'
+ 0.8u       'vdd_val'
+ 0.800001u  0
+ 2.2999995u 0
+ 2.3000005u 'vdd_val'
+ 2.8u       'vdd_val'
+ 2.800001u  0
+ 4.29994u   0
+ 4.299941u  'vdd_val'
+ 4.5u       'vdd_val'
+ 4.500001u  0
+ 6.299499u  0
+ 6.2995u    'vdd_val'
+ 6.5u       'vdd_val')

xdut d clk rst_n q vdd 0 sampler_dff

* mid-supply reference for the crossing measurements (measurement only)
bvth vth 0 v = 0.5*vdd_val
