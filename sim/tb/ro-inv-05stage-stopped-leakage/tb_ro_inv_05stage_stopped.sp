* ro-inv-05stage-stopped-leakage -- one STOPPED ring oscillator: static current
*
* The README's ratified definition of "idle" is: all ring oscillators
* stopped, no bits produced, block powered with register state retained --
* i.e. leakage plus static bias only. This testbench measures the entropy
* source's share of that: the DC operating-point current of one ring held
* stopped, with the supply up.
*
* WHY THIS RING IS NOT THE PLAIN ro-inv-05stage RING. A ring of five plain
* inverters has no enable, so it cannot be stopped at all -- and its only DC
* operating point is the unstable one with every stage sitting at its trip
* point, drawing hundreds of microamps of crowbar current through every
* stage. An operating-point analysis of the plain ring therefore does NOT
* measure leakage; it measures a state the ring never occupies. A stoppable
* ring is a prerequisite for the idle measurement, so this netlist adds the
* minimum thing that makes one: stage 1 becomes a 2-input NAND whose second
* input is the enable.
*
*   en = 0  ->  y(nand) forced high, ring latched in a unique static state
*               (n1=1, n2=0, n3=1, n4=0, n5=1), every stage at a rail, no
*               crowbar path: this is the idle state, and the measured
*               supply current is leakage plus static bias only.
*   en = 1  ->  the NAND degenerates to an inverter and the ring oscillates
*               (not exercised here; this testbench runs `op` only).
*
* The four inverter stages are the IDENTICAL candidate-A delay cell used by
* sim/tb/ro-inv-05stage-jitter/ and sim/tb/ro-inv-05stage-power/. The NAND
* stage is sized for the same drive as that inverter (series NMOS doubled to
* 2u each, parallel PMOS 2u each), so the enable costs drive strength
* nothing and the ring's period is not materially perturbed.
*
* This is a MEASUREMENT construct, not a design decision: #7 owns how the
* array's rings are actually stopped (NAND stage, supply gating, or
* otherwise). What is recorded here is what an un-power-gated stopped ring
* leaks, which is the pessimistic case any gating scheme improves on.
*
* The node voltages are reported alongside the current so the record proves
* the ring really is latched in the expected static state rather than
* sitting somewhere ambiguous.

.subckt inv_cell a y vdd vss
xp y a vdd vdd pfet_03v3 w=2u l=0.28u
xn y a vss vss nfet_03v3 w=1u l=0.28u
cload y vss 5f
.ends

.subckt nand2_cell a b y vdd vss
xpa y a vdd vdd pfet_03v3 w=2u l=0.28u
xpb y b vdd vdd pfet_03v3 w=2u l=0.28u
xna y a mid vss nfet_03v3 w=2u l=0.28u
xnb mid b vss vss nfet_03v3 w=2u l=0.28u
cload y vss 5f
.ends

vdd vdd 0 dc vdd_val
ven en 0 dc en_val

x1 en n5 n1 vdd 0 nand2_cell
x2 n1 n2 vdd 0 inv_cell
x3 n2 n3 vdd 0 inv_cell
x4 n3 n4 vdd 0 inv_cell
x5 n4 n5 vdd 0 inv_cell
