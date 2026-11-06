* power-switch decay -- discharge of the gated rail after the PMOS header opens (issue #782).
*
* Follow-up to the wake group of tb_power_switch.sp (issue #707): the same DUT
* (design/power_switch.spice, 400 um), the same leakage-equivalent load (an off NFET of
* 710 um at L = 0.28 um, see tb_power_switch.sp), the same rail capacitances (50 pF and 200 pF,
* ASSUMPTIONS, not extracted) and the same two sleep edges (10 ns and 1 us). Here the switch
* starts ON with the rail at vdd, sleep rises 0 -> vdd starting at 100 ns, and the rail
* discharges into the load. Nothing else pulls the rail down: there is no bleeder, so the
* decay is the load's own leakage against the rail capacitance and the switch's off leakage.
*
* Measured per unit and per case: the first fall of v(vvdd) through 90 %, 50 % and 5 % of
* vdd (5 % mirrors the 95 % settle threshold of the wake group; the repo defines no other
* "rail off" level), the lowest v(vvdd) seen, and v(vvdd) near the end of the 100 s run.
* The rail does not always get down to 5 %: the load's leakage falls with its own drain bias
* until it balances the switch's off leakage, at a level that depends on the corner.
*
* Method notes:
*   - The sleep drive is a unit PWL scaled by v(vdd), so it follows the swept supply.
*   - Crossing detectors are zero when v(vvdd) equals the fraction of vdd.

.include "../../../design/power_switch.spice"

.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3 cap_mc_skew=3 fnoicor=0
.param wleak=71

vsup vdd 0 dc 3.63

vrma rma 0 pwl(0 0 100n 0 110n 1 100m 1)
vrmb rmb 0 pwl(0 0 100n 0 1.1u 1 100m 1)
bsa sla 0 v = v(vdd)*v(rma)
bsb slb 0 v = v(vdd)*v(rmb)

xd1 sla vdd vd1 power_switch wf=10u nfing=40 lsw=0.28u
cd1 vd1 0 50p
xnd1 vd1 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
xd2 sla vdd vd2 power_switch wf=10u nfing=40 lsw=0.28u
cd2 vd2 0 200p
xnd2 vd2 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
xd3 slb vdd vd3 power_switch wf=10u nfing=40 lsw=0.28u
cd3 vd3 0 50p
xnd3 vd3 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak
xd4 slb vdd vd4 power_switch wf=10u nfing=40 lsw=0.28u
cd4 vd4 0 200p
xnd4 vd4 0 0 0 nfet_03v3 w=10u l=0.28u m=wleak

* Crossing detectors: zero when v(vdK) equals the fraction of vdd. Each carries a step of -10 V
* at 99.9 s (0.999 of the 100 s run) that forces a fall through zero if the rail has not got
* there, so a threshold that is never reached still yields a number (>= 99.9 s) instead of
* failing the whole unit; sim/tools/power_switch_decay.py reads that as "not reached".
bct90_1 ct90_1 0 v = v(vd1) - 0.9*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct50_1 ct50_1 0 v = v(vd1) - 0.5*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct05_1 ct05_1 0 v = v(vd1) - 0.05*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct90_2 ct90_2 0 v = v(vd2) - 0.9*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct50_2 ct50_2 0 v = v(vd2) - 0.5*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct05_2 ct05_2 0 v = v(vd2) - 0.05*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct90_3 ct90_3 0 v = v(vd3) - 0.9*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct50_3 ct50_3 0 v = v(vd3) - 0.5*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct05_3 ct05_3 0 v = v(vd3) - 0.05*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct90_4 ct90_4 0 v = v(vd4) - 0.9*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct50_4 ct50_4 0 v = v(vd4) - 0.5*v(vdd) - (time > 99.9e3 ? 10 : 0)
bct05_4 ct05_4 0 v = v(vd4) - 0.05*v(vdd) - (time > 99.9e3 ? 10 : 0)
