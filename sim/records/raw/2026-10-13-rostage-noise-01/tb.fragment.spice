* rostage-noise -- device noise of the SHIPPED entropy-source delay cell.
*
* DUT: the ro_stage cell of design/ro_array_core.spice, exported from
* design/xschem/ro_stage.sch by design/netlist.py. Nothing about the cell
* is redefined here; this fragment only biases it and drives it.
*
* Why this testbench has to exist. sim/tb/ro-inv-05stage-jitter/ and the
* array jitter testbench next door inject a FIXED per-stage noise density
* (1e-08 V/sqrt(Hz)) so that what varies corner to corner is the circuit's
* noise-to-jitter conversion rather than the stimulus. Recovering physical
* jitter from those runs needs the real device-noise density of the cell
* under test, at the same PVT point. sim/tb/inv-stage-noise/ supplies that
* for candidate A (the plain inverter of the ratified characterization) and
* sim/tb/cinv-stage-noise/ for candidate B. The array's cell is neither:
* it is a minimum-width inverter with always-on series starve devices, so
* it needs its own noise figures.
*
* Bias point: the trip point (v_in = v_out), which is where a ring stage
* sits while it is crossing threshold -- the instant at which noise turns
* into timing jitter. The bias tee below establishes it at every PVT point
* with no netlist edit:
*
*   lfb  (1e12 H)  DC short -> forces v(out) = v(ing): exact trip point
*                  AC open  -> the small-signal measurement sees the OPEN
*                              loop stage, not a unity-gain follower
*   cin  (1 F)     DC open  -> vn does not disturb the bias
*                  AC short -> vn drives the gate directly
*
* This is the identical technique sim/tb/inv-stage-noise/tb_inv_stage.sp
* uses; see that netlist's header for why a resistive self-bias silently
* corrupts inoise_spectrum and must not be substituted.
*
* Device sizes come from the schematic, so only the per-instance starve
* geometry is named here. wstv = 0.220u is ring 1 of the array -- the
* slowest, most heavily starved of the four skewed rings, i.e. the ring
* whose gain and swing margin are worst. gain_1g is reported for that
* reason: a starved stage that has lost small-signal gain at the
* oscillation frequency is the failure mode this cell is closest to.

vdd vdd 0 dc vdd_val
xi ing out vdd 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
lfb out ing 1e12
cin src ing 1
vn src 0 dc 0 ac 1
