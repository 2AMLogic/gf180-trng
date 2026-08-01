v {xschem version=3.4.4 file_version=1.2}
G {cld=0.5f}
K {}
V {}
S {}
E {}
T {meta_nand2 -- plain minimum-width static CMOS NAND2, the half-cell of the
metastability tap's arbiter (meta_arb).

Not ro_nand2: that cell carries the ring's always-on series starve devices
and exists to stop a ring. This one is unstarved, because the quantity the
tap is characterized for -- the arbiter's regeneration time constant
tau = C_node / g_m_eff -- is a property of THIS cell's drive and node
capacitance, and starving it would make tau a function of the starve
device rather than of the latch.

The series NMOS pair is widened to 0.44u so the stack's pull-down drive
matches a 0.22u single NMOS, the same convention ro_nand2 and xor2 use.
Both halves of meta_arb instantiate this cell with identical parameters:
the arbiter's symmetry is structural, not a sizing coincidence.} -700 -700 0 0 0.25 0.25 {}
C {ipin.sym} -700 -420 0 0 {name=p1 lab=a}
C {ipin.sym} -700 -380 0 0 {name=p2 lab=b}
C {opin.sym} -620 -420 0 0 {name=p3 lab=y}
C {iopin.sym} -700 -340 0 0 {name=p4 lab=vdd}
C {iopin.sym} -620 -340 0 0 {name=p5 lab=vss}
C {pfet_03v3.sym} 0 -400 0 0 {name=Mpa L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 200 -400 0 0 {name=Mpb L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -300 0 0 {name=Mna L=0.28u W=0.44u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -200 0 0 {name=Mnb L=0.28u W=0.44u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {capa.sym} 400 -320 0 0 {name=Cld m=1 value='cld'}
N 20 -370 20 -330 {lab=y}
N 20 -350 220 -350 {lab=y}
N 220 -370 220 -350 {lab=y}
N 220 -350 400 -350 {lab=y}
N 20 -270 20 -230 {lab=nm}
C {lab_pin.sym} 100 -350 0 0 {name=ly lab=y}
C {lab_pin.sym} 20 -250 0 0 {name=lnm lab=nm}
C {lab_pin.sym} -20 -400 0 1 {name=la1 lab=a}
C {lab_pin.sym} -20 -300 0 1 {name=la2 lab=a}
C {lab_pin.sym} 180 -400 0 1 {name=lb1 lab=b}
C {lab_pin.sym} -20 -200 0 1 {name=lb2 lab=b}
C {lab_pin.sym} 20 -430 0 0 {name=lv1 lab=vdd}
C {lab_pin.sym} 20 -400 0 0 {name=lv2 lab=vdd}
C {lab_pin.sym} 220 -430 0 0 {name=lv3 lab=vdd}
C {lab_pin.sym} 220 -400 0 0 {name=lv4 lab=vdd}
C {lab_pin.sym} 20 -300 0 0 {name=ls1 lab=vss}
C {lab_pin.sym} 20 -200 0 0 {name=ls2 lab=vss}
C {lab_pin.sym} 20 -170 0 0 {name=ls3 lab=vss}
C {lab_pin.sym} 400 -290 0 0 {name=ls4 lab=vss}
