* cinv-stage-noise -- device noise of candidate delay cell B (current-
* starved CMOS inverter, gf180mcu 3.3 V core devices) at its trip point.
*
* Candidate B is the current-starved inverter stage: the delay cell used
* by sim/tb/ro-cinv-*stage-jitter/. Dimensions and bias network here are
* IDENTICAL to the ones in those ring-oscillator netlists.
*
* Topology: a plain inverter with a PMOS head device (gated by pb) and an
* NMOS tail device (gated by nb) in series, so the stage's charge/
* discharge current -- and therefore its delay and its output slew rate --
* is set by a bias current rather than by the inverter's own drive. This
* is the standard way to trade oscillation frequency for slew rate, and
* slew rate is the denominator in the noise-to-jitter conversion, so it is
* the obvious knob a jitter-based entropy source would reach for.
*
* Bias: a resistor-referenced diode-connected NMOS sets nb; an NMOS/PMOS
* mirror pair sets pb. No hard-coded bias voltages, so the operating point
* re-establishes itself at every PVT point without a netlist edit. The
* mirror is deliberately simple (no cascode, no startup circuit) -- this
* is a delay-cell characterization, not a bias-generator design; the bias
* generator's own noise contribution is filtered by cfn/cfp and is
* included in what `.noise` reports here.
*
* Bias-tee (lfb/cin) trip-point technique is identical to
* sim/tb/inv-stage-noise/tb_inv_stage.sp -- see that netlist's header for
* why a resistive self-bias is not usable.

.subckt cinv_cell a y vdd vss nb pb
xph ph pb  vdd vdd pfet_03v3 w=4u l=0.5u
xp  y  a   ph  vdd pfet_03v3 w=2u l=0.28u
xn  y  a   nl  vss nfet_03v3 w=1u l=0.28u
xnl nl nb  vss vss nfet_03v3 w=2u l=0.5u
cload y vss 5f
.ends

.subckt cinv_bias vdd vss nb pb
rref vdd nb 30k
xmnb nb nb vss vss nfet_03v3 w=1u l=1u
xmn2 pb nb vss vss nfet_03v3 w=2u l=1u
xmpb pb pb vdd vdd pfet_03v3 w=4u l=1u
cfn nb vss 100f
cfp pb vss 100f
.ends

vdd vdd 0 dc vdd_val
xb vdd 0 nb pb cinv_bias
xi ing out vdd 0 nb pb cinv_cell
lfb out ing 1e12
cin src ing 1
vn src 0 dc 0 ac 1
