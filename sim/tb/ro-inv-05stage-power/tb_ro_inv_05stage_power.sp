* ro-inv-05stage-power -- free-running 5-stage plain-inverter ring: supply current
*
* THE SAME RING sim/tb/ro-inv-05stage-jitter/ measures the jitter of:
* identical delay cell (pfet_03v3 w=2u l=0.28u / nfet_03v3 w=1u l=0.28u,
* cload 5f), identical stage count, identical .ic start-up. The only
* difference is that the five series trnoise() sources are omitted -- they
* are ideal 0 V DC sources that inject noise but no power, so removing them
* leaves the supply current unchanged while making this run DETERMINISTIC
* (no seed needed, per sim/README.md's "no seed, no evidence" rule, which
* only binds stochastic analyses).
*
* Keeping the cell identical is the point: the per-ring active power
* recorded here has to be the power of the ring whose per-ring jitter
* budget Q1 was measured, or DR-0007's N-ring array projection would be
* multiplying two different rings together.
*
* Measurement method -- charge integration between two like-edged
* crossings of the SAME node, an exact integer number of ring periods
* apart:
*
*   fq/cq/rq   an ideal charge integrator. fq mirrors the supply source's
*              branch current into cq (1 nF), so v(q) is the charge drawn
*              from vdd since t=0, scaled by 1/cq. Taking the difference
*              of v(q) at two crossings gives the charge drawn over EXACTLY
*              32 oscillation periods, so the reported mean current has no
*              partial-cycle bias -- unlike an average over a fixed time
*              window, whose error is set by wherever the window happens to
*              cut the last cycle.
*   rq         DC path for the integrator node (a floating capacitor is a
*              singular matrix). tau = rq*cq = 1000 s, i.e. 5e-8 of the
*              measurement window: droop is not a measurable effect here.
*   .ic v(q)=0 pins the integrator node during the operating-point solve so
*              the op does not try to push the whole DC supply current
*              through rq.
*
* bxing is a pure measurement probe (behavioural, no loading): it shifts
* v(n1) so the mid-supply crossing becomes a zero crossing that
* `meas ... when v(xing)=0` finds at any supply, with no hard-coded
* supply-dependent trip voltage.
*
* .ic v(n1)=0 starts the ring from a defined state. The first two rising
* crossings are discarded (the window opens at rise=3) so that start-up
* current is not counted as steady-state oscillation current.

.subckt inv_cell a y vdd vss
xp y a vdd vdd pfet_03v3 w=2u l=0.28u
xn y a vss vss nfet_03v3 w=1u l=0.28u
cload y vss 5f
.ends

vdd vdd 0 dc vdd_val
x1 n1 n2 vdd 0 inv_cell
x2 n2 n3 vdd 0 inv_cell
x3 n3 n4 vdd 0 inv_cell
x4 n4 n5 vdd 0 inv_cell
x5 n5 n1 vdd 0 inv_cell

* charge integrator: v(q) = (1/cq) * integral of the current drawn from vdd
fq q 0 vdd 1
cq q 0 1n
rq q 0 1e12

bxing xing 0 v = v(n1) - 0.5*vdd_val
.ic v(n1)=0
.ic v(q)=0
