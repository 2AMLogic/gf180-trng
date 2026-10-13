* ro-ring11-ring2-pex -- ring2 (ro_ring11_ring2) free-running, for `klt pex` (issue #423).
*
* A circuit body for `klt sim`: no .control/.end. klt sim appends the corner's
* .lib/.temp cards, the .meas cards from request.json, `alter vsupply=<V>`
* for the supply corner, and the analysis. The one .include below is the
* schematic DUT; `klt pex` re-points exactly that line at the netlist it
* extracts from layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds for the extracted-side
* run, and reuses everything else here byte for byte on both sides.
*
* The xdut line follows klt extract's fifteen-port order for that layout (ring2's own,
* which is NOT ring1's: here the ring output is the first port)
* (ring nodes first, as positioned in the layout, then en vddr vss vsubs);
* build_dut.py generates the schematic header to match and fails if this
* line drifts from it.
*
* Stimulus: the ring's own supply `vddr` swept by the request's supply axis,
* `en` held at that same supply (ring enabled from t=0), vss and vsubs at
* 0 V. One .ic kick breaks the all-equal operating point so the ring starts.
* Nothing loads any ring node: `ron` is a behavioural, supply-normalised copy
* of `ro` for the 50 % crossings, and draws no current from the ring.

.include "ro_ring11_ring2_schematic.spice"

* switches design.ngspice sets (its values, verbatim)
.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0

vsupply vddr 0 dc 3.3
een en 0 vddr 0 1
vvss vss 0 dc 0
vvsubs vsubs 0 dc 0

xdut ro n1 n2 n3 n4 n5 n6 n7 n8 n9 n10 en vddr vss vsubs ro_ring11_ring2

bron ron 0 v='v(ro)/v(vddr)'

.ic v(n1)=0
