* sampler-core-idle-leakage -- the whole transistor-level block in the README's
* ratified IDLE state: "all ring oscillators stopped and no bits being produced,
* with the block powered and register state retained -- i.e. leakage plus static
* bias only."
*
* DUT: design/sampler_core.spice, unmodified -- ro_array_core (two 11-stage
* starved rings + the XOR combiner) plus both sampler_dff instances. That is
* everything on the analog side of the DR-0009 verification boundary, in one
* number, which is what the `< 1 uA idle` row is actually about.
*
* Why this deck exists. Every idle/leakage measurement in this repository today
* covers a PART of that:
*   - sim/tb/ro-inv-05stage-stopped-leakage/ is a STOPPED RING, but the
*     characterisation-cell 5-stage ring, not the shipped 11-stage starved one,
*     and not the XOR tree;
*   - sim/tb/device-leakage-03v3/ is bare devices;
*   - sim/tb/sampler-dff-reset-current-{xsv,xsb}/ are the two flops, but with
*     `rst_n` HELD LOW -- the reset window, not the idle state, which per the
*     README's own definition has reset released and state retained.
* Nothing measures the shipped block, stopped, with reset released. This does.
*
* ---------------------------------------------------------------------------
* WHY THIS IS A SETTLED TRANSIENT AND NOT AN OPERATING POINT
* ---------------------------------------------------------------------------
*
* sim/tb/ro-inv-05stage-stopped-leakage/ uses `op`, and its header explains why
* that is legitimate for a STOPPED RING: with the enable low the ring's loop
* gain is zero and there is exactly one stable DC solution. That argument does
* not extend to this block, and the difference is not cosmetic.
*
* `sampler_dff` contains two cross-coupled storage loops. Once `rst_n` is
* released they are bistable, so they have THREE DC solutions each -- the two
* stored states and an unstable mid-rail one -- and nothing in an `op` analysis
* prefers a stable one. Run as written, `op` lands both flops at mid-rail
* (measured: 1.543 V on a 3.63 V rail) with every latch inverter sitting at its
* own trip point, and reports 193 uA per copy. That number is crowbar current
* through a state the circuit never occupies, not leakage, and it is wrong by
* about five orders of magnitude. It is the exact failure mode
* ro-inv-05stage-stopped-leakage's header warns about for a free-running ring,
* reappearing here for a different reason.
*
* So the block is driven into idle the way a real one gets there, and the
* measurement is taken long after it arrives:
*
*   t = 0        rings clamped (en = 0), reset asserted (rst_n = 0), clk low.
*   t = 100 ns   reset released. Both flops hold their reset state.
*   t = 200 ns   ONE clock rising edge, so each flop captures its own D and the
*                block ends in a state it actually reached by running rather
*                than one the testbench asserted. xsv captures its tied-high D
*                (raw_valid -> 1); xsb captures xo, which is 0 while the rings
*                are clamped (ro1 = ro2 = 1, so the XOR output is low).
*   t = 300 ns   copy A's clock returns low and parks there. Copy B's clock
*                stays high -- see below.
*   [900 ns, 1000 ns]  measurement window: 600 ns after the last event in the
*                deck, with every node at a rail and nothing switching.
*
* Both the instantaneous branch current at 1 us and the charge integrated over
* the last 100 ns are recorded. For a genuinely static state they must agree;
* if they do not, the state was not static and the record says so on its face.
*
* WHY TWO COPIES OF THE DUT. A parked clock has two states and they are not
* equivalent for leakage: clk low leaves each flop's master transmission gate
* transparent and its slave gate shut, clk high does the reverse, so the two
* park states put different devices in different bias conditions. Which one a
* real integrator parks in is not fixed by any decision record. So the block is
* instantiated TWICE on two independently sensed supply branches -- copy A
* parked low, copy B parked high -- and both are reported at the same PVT point
* rather than assuming a park state or spending two grid sweeps. The copies
* share no signal node and the supply source is ideal, so neither perturbs the
* other's sense branch.
*
* Sign convention: vsA/vsB are 0 V sense sources in the supply leg with vsup as
* their positive node, so i(vsA) is POSITIVE for current delivered into the
* block. That is the opposite sign to the fq/cq charge-integrator construction
* used elsewhere in this repository (design/README.md, "Reading the recorded
* currents"), because the CCCS there pulls the integrator node negative for a
* positive branch current. tb.json handles each accordingly; every recorded
* current and power below is a positive magnitude.

vsup vsup 0 dc vdd_val

ven en 0 dc 0
vrst rst_n 0 dc 0 pulse(0 vdd_val 100n 1p 1p 10u 20u)
vclk0 clk0 0 dc 0 pulse(0 vdd_val 200n 1p 1p 100n 10u)
vclk1 clk1 0 dc 0 pulse(0 vdd_val 200n 1p 1p 10u 20u)

vsA vsup vddA dc 0
vsB vsup vddB dc 0

* Copy A: clock parked LOW (each flop's master TG transparent, slave TG shut).
xdutA en en vddA vddA vddA 0 clk0 rst_n rbA rvA sampler_core

* Copy B: clock parked HIGH (each flop's master TG shut, slave TG transparent).
xdutB en en vddB vddB vddB 0 clk1 rst_n rbB rvB sampler_core

* Charge integrators, one per copy: v(qN) is the charge drawn on that branch
* since t = 0, scaled by 1/cq. Differencing across the measurement window gives
* the window-average current independently of the instantaneous read.
fqA qA 0 vsA 1
cqA qA 0 1n
rqA qA 0 1e12
fqB qB 0 vsB 1
cqB qB 0 1n
rqB qB 0 1e12
.ic v(qA)=0
.ic v(qB)=0
