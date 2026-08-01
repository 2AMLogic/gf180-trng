v {xschem version=3.4.4 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {xor2 -- minimum-width static CMOS 2-input XOR (12 devices).

  pull-down  : (a AND b) OR (an AND bn)     -> y low when a == b
  pull-up    : (a NOR b) NOR-dual, i.e.
               [Mp1 || Mp2] in series with [Mp3 || Mp4]
  inverters  : an = NOT a, bn = NOT b

Fully static and fully complementary on purpose. A pass-transistor XOR
would be smaller, but it leaves the combining node undriven for part of
the input space, and the combining node is the ONLY node the sampler
observes (DR-0001 keeps the raw tap at the sampler output). A source of
randomness must not be built on a node whose drive strength depends on
its own data.

Series devices are doubled (NMOS 0.44u, PMOS 0.88u) so a two-high stack
has roughly the drive of the single 0.22u/0.44u devices used elsewhere.
The tree is powered from vdd -- the BLOCK supply -- not from any ring's
vddr, so the rings' supply pins stay clean per-ring observation points.} -900 -800 0 0 0.25 0.25 {}
C {ipin.sym} -900 -420 0 0 {name=p1 lab=a}
C {ipin.sym} -900 -380 0 0 {name=p2 lab=b}
C {opin.sym} -800 -420 0 0 {name=p3 lab=y}
C {iopin.sym} -900 -340 0 0 {name=p4 lab=vdd}
C {iopin.sym} -800 -340 0 0 {name=p5 lab=vss}
C {pfet_03v3.sym} -600 -300 0 0 {name=MpiA L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} -600 -200 0 0 {name=MniA L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} -350 -300 0 0 {name=MpiB L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} -350 -200 0 0 {name=MniB L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 0 -500 0 0 {name=Mp1 L=0.28u W=0.88u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 200 -500 0 0 {name=Mp2 L=0.28u W=0.88u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 0 -400 0 0 {name=Mp3 L=0.28u W=0.88u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 200 -400 0 0 {name=Mp4 L=0.28u W=0.88u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -300 0 0 {name=Mn1 L=0.28u W=0.44u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -200 0 0 {name=Mn2 L=0.28u W=0.44u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 200 -300 0 0 {name=Mn3 L=0.28u W=0.44u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 200 -200 0 0 {name=Mn4 L=0.28u W=0.44u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
N -580 -270 -580 -230 {lab=an}
N -330 -270 -330 -230 {lab=bn}
N 20 -470 20 -430 {lab=mid}
N 20 -450 220 -450 {lab=mid}
N 220 -470 220 -450 {lab=mid}
N 220 -450 220 -430 {lab=mid}
N 20 -370 20 -330 {lab=y}
N 220 -370 220 -330 {lab=y}
N 20 -350 220 -350 {lab=y}
N 20 -270 20 -230 {lab=s1}
N 220 -270 220 -230 {lab=s2}
C {lab_pin.sym} -580 -250 0 0 {name=lan lab=an}
C {lab_pin.sym} -330 -250 0 0 {name=lbn lab=bn}
C {lab_pin.sym} 20 -450 0 0 {name=lmid lab=mid}
C {lab_pin.sym} 120 -350 0 0 {name=ly lab=y}
C {lab_pin.sym} 20 -250 0 0 {name=ls1 lab=s1}
C {lab_pin.sym} 220 -250 0 0 {name=ls2 lab=s2}
C {lab_pin.sym} -620 -300 0 1 {name=la1 lab=a}
C {lab_pin.sym} -620 -200 0 1 {name=la2 lab=a}
C {lab_pin.sym} -20 -500 0 1 {name=la3 lab=a}
C {lab_pin.sym} -20 -300 0 1 {name=la4 lab=a}
C {lab_pin.sym} -370 -300 0 1 {name=lb1 lab=b}
C {lab_pin.sym} -370 -200 0 1 {name=lb2 lab=b}
C {lab_pin.sym} 180 -500 0 1 {name=lb3 lab=b}
C {lab_pin.sym} -20 -200 0 1 {name=lb4 lab=b}
C {lab_pin.sym} -20 -400 0 1 {name=lan2 lab=an}
C {lab_pin.sym} 180 -300 0 1 {name=lan3 lab=an}
C {lab_pin.sym} 180 -400 0 1 {name=lbn2 lab=bn}
C {lab_pin.sym} 180 -200 0 1 {name=lbn3 lab=bn}
C {lab_pin.sym} -580 -330 0 0 {name=lp1 lab=vdd}
C {lab_pin.sym} -580 -300 0 0 {name=lp2 lab=vdd}
C {lab_pin.sym} -330 -330 0 0 {name=lp3 lab=vdd}
C {lab_pin.sym} -330 -300 0 0 {name=lp4 lab=vdd}
C {lab_pin.sym} 20 -530 0 0 {name=lp5 lab=vdd}
C {lab_pin.sym} 20 -500 0 0 {name=lp6 lab=vdd}
C {lab_pin.sym} 220 -530 0 0 {name=lp7 lab=vdd}
C {lab_pin.sym} 220 -500 0 0 {name=lp8 lab=vdd}
C {lab_pin.sym} 20 -400 0 0 {name=lp9 lab=vdd}
C {lab_pin.sym} 220 -400 0 0 {name=lp10 lab=vdd}
C {lab_pin.sym} -580 -170 0 0 {name=lq1 lab=vss}
C {lab_pin.sym} -580 -200 0 0 {name=lq2 lab=vss}
C {lab_pin.sym} -330 -170 0 0 {name=lq3 lab=vss}
C {lab_pin.sym} -330 -200 0 0 {name=lq4 lab=vss}
C {lab_pin.sym} 20 -300 0 0 {name=lq5 lab=vss}
C {lab_pin.sym} 20 -200 0 0 {name=lq6 lab=vss}
C {lab_pin.sym} 20 -170 0 0 {name=lq7 lab=vss}
C {lab_pin.sym} 220 -300 0 0 {name=lq8 lab=vss}
C {lab_pin.sym} 220 -200 0 0 {name=lq9 lab=vss}
C {lab_pin.sym} 220 -170 0 0 {name=lq10 lab=vss}
