v {xschem version=3.4.4 file_version=1.2}
G {cld=0.5f}
K {}
V {}
S {}
E {}
T {meta_inv -- plain minimum-width 3.3 V inverter, the delay element of the
metastability tap's matched strobe paths.

This is deliberately NOT ro_stage. ro_stage carries always-on series
starve devices because a ring wants nanosecond delays at minimum switched
energy; the tap's strobe paths want the OPPOSITE -- the shortest, most
sharply-defined edge the process gives, because everything the tap can be
characterized for (regeneration constant, path skew) is measured in
picoseconds against that edge. A starved cell would put the two racing
edges into a slew regime where the arbiter's input differential is set by
the ramp rather than by the delay imbalance being measured.

cld is an explicit placeholder for local interconnect load, on the same
terms as ro_stage's: an estimate, not an extracted parasitic. It is also
the tap's calibration knob -- see ro_meta_tap, where the two strobe paths
differ ONLY in this value.} -560 -420 0 0 0.25 0.25 {}
C {ipin.sym} -560 -150 0 0 {name=p1 lab=a}
C {opin.sym} -480 -150 0 0 {name=p2 lab=y}
C {iopin.sym} -560 -100 0 0 {name=p3 lab=vdd}
C {iopin.sym} -480 -100 0 0 {name=p4 lab=vss}
C {pfet_03v3.sym} 0 -200 0 0 {name=Mp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -100 0 0 {name=Mn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {capa.sym} 200 -120 0 0 {name=Cld m=1 value='cld'}
N 20 -170 20 -130 {lab=y}
N -20 -200 -20 -100 {lab=a}
N 20 -150 200 -150 {lab=y}
C {lab_pin.sym} -20 -150 0 1 {name=la lab=a}
C {lab_pin.sym} 100 -150 0 0 {name=ly lab=y}
C {lab_pin.sym} 20 -230 0 0 {name=lv1 lab=vdd}
C {lab_pin.sym} 20 -200 0 0 {name=lv2 lab=vdd}
C {lab_pin.sym} 20 -100 0 0 {name=ls1 lab=vss}
C {lab_pin.sym} 20 -70 0 0 {name=ls2 lab=vss}
C {lab_pin.sym} 200 -90 0 0 {name=ls3 lab=vss}
