v {xschem version=3.4.4 file_version=1.2}
G {wstv=0.22u lstv=2u cld=0.5f}
K {}
V {}
S {}
E {}
T {ro_stage -- series-starved minimum-width 3.3 V inverter delay cell.

Mp/Mn are the smallest inverter the gf180mcu 3.3 V core devices allow
(W = 0.44u / 0.22u at L = 0.28u). Mph/Mnt are always-on series devices
(gates tied to the opposite rail) whose W/L sets the charge/discharge
current, and therefore the stage delay, WITHOUT adding switched
capacitance to the output node y. That separation is the whole point:
per DR-0008 the entropy source's energy cost per raw bit scales as the
SQUARE of the energy switched per ring cycle, while the ring frequency
(and hence the XOR node's transition density) can be traded freely
against the ring count N at constant energy per cycle. Starving buys
frequency; it does not cost energy per cycle.

cld is an explicit placeholder for local interconnect load. It is an
estimate, not an extracted parasitic: layout (#16/#26) owes either an
extraction that lands at or below cld, or a superseding sizing pass.} -560 -420 0 0 0.25 0.25 {}
C {ipin.sym} -560 -150 0 0 {name=p1 lab=a}
C {opin.sym} -480 -150 0 0 {name=p2 lab=y}
C {iopin.sym} -560 -100 0 0 {name=p3 lab=vddr}
C {iopin.sym} -480 -100 0 0 {name=p4 lab=vss}
C {pfet_03v3.sym} 0 -300 0 0 {name=Mph L=lstv W=wstv nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {pfet_03v3.sym} 0 -200 0 0 {name=Mp L=0.28u W=0.44u nf=1 m=1 model=pfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 -100 0 0 {name=Mn L=0.28u W=0.22u nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {nfet_03v3.sym} 0 0 0 0 {name=Mnt L=lstv W=wstv nf=1 m=1 model=nfet_03v3 spiceprefix=X}
C {capa.sym} 200 -120 0 0 {name=Cld m=1 value='cld'}
N 20 -270 20 -230 {lab=py}
N 20 -170 20 -130 {lab=y}
N 20 -70 20 -30 {lab=ny}
N -20 -200 -20 -100 {lab=a}
N 20 -150 200 -150 {lab=y}
C {lab_pin.sym} 20 -250 0 0 {name=lpy lab=py}
C {lab_pin.sym} -20 -150 0 1 {name=la lab=a}
C {lab_pin.sym} 100 -150 0 0 {name=ly lab=y}
C {lab_pin.sym} 20 -50 0 0 {name=lny lab=ny}
C {lab_pin.sym} 20 -330 0 0 {name=lv1 lab=vddr}
C {lab_pin.sym} 20 -300 0 0 {name=lv2 lab=vddr}
C {lab_pin.sym} 20 -200 0 0 {name=lv3 lab=vddr}
C {lab_pin.sym} -20 0 0 1 {name=lv4 lab=vddr}
C {lab_pin.sym} -20 -300 0 1 {name=ls1 lab=vss}
C {lab_pin.sym} 20 -100 0 0 {name=ls2 lab=vss}
C {lab_pin.sym} 20 0 0 0 {name=ls3 lab=vss}
C {lab_pin.sym} 20 30 0 0 {name=ls4 lab=vss}
C {lab_pin.sym} 200 -90 0 0 {name=ls5 lab=vss}
