v {xschem version=3.4.4 file_version=1.2}
G {wf=10u nfing=40 lsw=0.28u}
K {}
V {}
S {}
E {}
T {power_switch -- PMOS header (high-side power switch) for the digital section (issue #707, child of #700).

One 3.3 V core PFET between the always-on supply vdd and the gated
virtual rail vvdd that feeds the conditioner, health tests and interface.
The standard-cell library ships no header, footer, retention or isolation
cell (DR-0017, One hard constraint on the obvious fix), so this is the
custom cell that DR-0017 option A said would be needed.

sleep high turns the switch OFF (vvdd floats down and the digital
leakage collapses); sleep low turns it ON. The control is a plain
logic-level input driven from the always-on domain, so no level shifter
is needed. Total width is nfing x wf, built as nfing parallel
fingers of width wf so the layout cell (one 10u finger per gate) and this
netlist describe the same device. Default 40 x 10u = 400u at the minimum
0.28u length,
chosen by the width sweep in sim/characterization-power-switch.md.

Header and not footer: a footer would put the switch in the return path
that the analog taps share through the common vss trunk
(sim/characterization-vss-trunk-ir-drop.md), so its on-resistance would
lift the analog reference. A header leaves vss untouched. The PFET bulk
is tied to vdd, not to vvdd.

Nothing here retains state or isolates the outputs of the gated domain:
that is issue #708.} -700 -650 0 0 0.25 0.25 {}
C {ipin.sym} -560 -150 0 0 {name=p1 lab=sleep}
C {iopin.sym} -560 -100 0 0 {name=p2 lab=vdd}
C {iopin.sym} -480 -100 0 0 {name=p3 lab=vvdd}
C {pfet_03v3.sym} 0 -200 0 0 {name=Mp L=lsw W=wf nf=1 m=nfing model=pfet_03v3 spiceprefix=X}
N 20 -170 20 -130 {lab=vvdd}
C {lab_pin.sym} -20 -200 0 1 {name=ls lab=sleep}
C {lab_pin.sym} 20 -230 0 0 {name=lv1 lab=vdd}
C {lab_pin.sym} 20 -200 0 0 {name=lvb lab=vdd}
C {lab_pin.sym} 20 -130 0 0 {name=lo lab=vvdd}
