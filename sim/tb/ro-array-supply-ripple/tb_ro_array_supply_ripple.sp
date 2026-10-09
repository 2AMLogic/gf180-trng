* ro-array-supply-ripple -- deterministic supply-ripple susceptibility of the
* shipped, buffered two-ring entropy-source array (issue #414).
*
* SCHEMATIC-LEVEL, DETERMINISTIC, SYNTHETIC. The DUT is design/ro_array_core.spice
* (the DR-0018 buffered array), the same one sim/tb/ro-array-core-pvt-q/ measures.
* The only difference from that deck's stimulus is that each ring's supply pin
* now carries a declared sinusoid in series with the ideal supply. That sinusoid
* is a *synthetic* aggressor: it is not an extracted supply network, it has no
* source impedance, and nothing here models how a real neighbouring block would
* develop it. The result is a susceptibility (timing response per volt of rail
* ripple), not a prediction of any built chip's supply noise.
*
* Circuit body for `klt sim`: no .control/.end. klt sim appends the corner's
* .lib/.temp cards, the .meas cards from the request, an `alter` for every
* key of the request's corners.supply_v, and the analysis. The keys that move
* *together, by index* are the supply and the four ripple parameters below, so
* one request lists a whole (mode, amplitude) grid for one corner and one
* ripple frequency; sim/tools/supply_ripple.py writes and checks those
* requests. Nothing in this directory is run by sim/selftest.sh or CI.
*
* Ripple parameters (DC sources below; overridden per grid point by the request):
*   amp          peak amplitude of the sinusoid, volts (0 = the control)
*   frq          frequency, hertz
*   m1           1 puts the sinusoid on ring 1's supply pin (vddr1), else 0
*   m2           1 puts the sinusoid on ring 2's supply pin (vddr2), else 0
* Both pins at once use the SAME phase (common-mode ripple); the sinusoid
* starts at zero phase at t = 0, so the tone phase is referenced to t = 0.
*
* What is and is not perturbed. The ring supply pins vddr1/vddr2 are
* perturbed. The output buffers and the XOR combiner sit on `vdd` (tree),
* which is NOT perturbed here: ripple reaching them is a separate path and is
* not measured. Nothing is added to the enable, substrate or ground.
*
* Edge timing is read as absolute 50 %-of-nominal-supply rising crossings of
* v(ro1)/v(ro2) (the buffered ring outputs; vth is a fixed 0.5*v(vsup) and does
* not move with the perturbed rail, which is stated rather than hidden in the
* analysis). The edge `.meas` cards are generated into the request.

.include "../../../design/ro_array_core.spice"

* switches design.ngspice sets (its values, verbatim)
.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0

* The ripple parameters are DC sources, not .params, because the request
* sets them per grid point with ngspice `alter`, which reaches an independent
* source's value but not an already-evaluated .param (a .param-driven SIN()
* would silently stay at its deck value -- checked, issue #414). The defaults
* below are the zero-ripple control.
vamp amp 0 dc 0
vfrq frq 0 dc 2e6
vm1 m1 0 dc 0
vm2 m2 0 dc 0

vsupply vsup 0 dc 3.3
een en 0 vsup 0 1

* Series ripple: v(vddrN) - v(vsup) = m_N * amp * sin(2*pi*frq*t).
* With amp = 0 each is a zero-volt source, i.e. the unperturbed control built
* from the identical netlist, window and solver settings.
br1 vddr1 vsup v = v(amp)*v(m1)*sin(6.283185307179586*v(frq)*time)
br2 vddr2 vsup v = v(amp)*v(m2)*sin(6.283185307179586*v(frq)*time)
vtr vdd vsup dc 0

xdut en en vddr1 vddr2 vdd 0 xo ro1 ro2 ro_array_core

bvth vth 0 v = 0.5*v(vsup)

.ic v(xdut.xr1.n1)=0
.ic v(xdut.xr2.n1)=0
