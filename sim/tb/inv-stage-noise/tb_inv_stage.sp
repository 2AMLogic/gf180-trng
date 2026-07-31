* inv-stage-noise -- device noise of candidate delay cell A (plain CMOS
* inverter, gf180mcu 3.3 V core devices) biased at its own trip point.
*
* Candidate A is the plain inverter stage: the delay cell used by
* sim/tb/ro-inv-*stage-jitter/. Its dimensions here are IDENTICAL to the
* ones in those ring-oscillator netlists, so the noise figures recorded
* here are the noise figures of the exact cell whose jitter is measured
* there.
*
* Bias point: the trip point (v_in = v_out), which is where a ring
* oscillator stage sits when it is crossing threshold -- i.e. the instant
* at which noise is converted into timing jitter. A noise figure taken at
* any other bias point would not be the one that matters.
*
* The trip point is established by an IDEAL BIAS TEE rather than by a
* hard-coded DC source, so that it re-establishes itself correctly at
* every process/voltage/temperature point with no manual netlist edit:
*
*   lfb  (1e12 H)  DC short  -> forces v(out) = v(ing): exact trip point
*                  AC open   -> feedback removed above ~1 mHz, so the
*                               small-signal measurement sees the OPEN
*                               loop stage, not a unity-gain follower
*   cin  (1 F)     DC open   -> vn does not disturb the bias
*                  AC short  -> vn drives the gate directly
*
* A plain resistive self-bias (out--R--in) does NOT work here: the gate
* capacitance and R form a divider that collapses the drive from vn at
* high frequency, which silently inflates inoise_spectrum by orders of
* magnitude. The bias tee avoids that failure mode entirely.

.subckt inv_cell a y vdd vss
xp y a vdd vdd pfet_03v3 w=2u l=0.28u
xn y a vss vss nfet_03v3 w=1u l=0.28u
cload y vss 5f
.ends

vdd vdd 0 dc vdd_val
xi ing out vdd 0 inv_cell
lfb out ing 1e12
cin src ing 1
vn src 0 dc 0 ac 1
