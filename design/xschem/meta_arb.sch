v {xschem version=3.4.4 file_version=1.2}
G {cld=0.5f}
K {}
V {}
S {}
E {}
T {meta_arb -- the metastable element of the tap: a cross-coupled NAND2 SR
latch used as a two-input arbiter.

  sn, rn   active-low, driven by the two matched strobe paths.
  q, qn    the resolved state.

Sequence, once per xin period of ro_meta_tap:

  1. ASSERT   both sn and rn go low together -> q = qn = 1. The latch is
              driven off both of its stable states into a known, forced
              condition. This is the "forbidden" input combination of an
              SR latch, and it is entered on purpose.
  2. RELEASE  both rise, separated by dt = t(rn) - t(sn). The latch must
              choose. The input that rises FIRST pulls its own NAND output
              low: dt > 0 -> q = 0.
  3. RESOLVE  the differential grows as exp(t/tau) about the balance point.
              For |dt| >> tau the choice is made by dt and the outcome is
              deterministic. For |dt| -> 0 the starting differential is
              set by NOISE, the resolution time diverges as tau*ln(1/|dt|),
              and the outcome is random. That last regime is the entropy
              mechanism; it is also the regime a noiseless transient solver
              cannot enter, which is why this repository claims tau and not
              entropy. See DR-0011.

Why a bespoke cross-coupled NAND rather than a gf180mcu_fd_sc_mcu9t5v0
flip-flop, which the architecture survey offers as an acceptable first
pass: the open PDK ships xschem symbols for gf180mcu_fd_pr primitives
only, not for the standard-cell library, so a library FF cannot be
instantiated in this repository's schematic flow without hand-authoring a
symbol around its CDL netlist -- and the survey's own objection to that
route (section B.3) is that a library FF's setup/hold window is
characterized for being MET, not for being deliberately violated. An
arbiter built from two identical instances of one cell is symmetric by
construction, which is exactly the property being characterized.

cld is applied to BOTH halves identically. It is the arbiter's own node
load; the tap's calibration knob is in the strobe paths (ro_meta_tap),
not here, so that trimming the balance point cannot change tau.} -900 -700 0 0 0.25 0.25 {}
C {ipin.sym} -900 -420 0 0 {name=p1 lab=sn}
C {ipin.sym} -900 -380 0 0 {name=p2 lab=rn}
C {opin.sym} -800 -420 0 0 {name=p3 lab=q}
C {opin.sym} -800 -380 0 0 {name=p4 lab=qn}
C {iopin.sym} -900 -340 0 0 {name=p5 lab=vdd}
C {iopin.sym} -800 -340 0 0 {name=p6 lab=vss}
C {meta_nand2.sym} 0 0 0 0 {name=xna cld=cld}
C {meta_nand2.sym} 0 200 0 0 {name=xnb cld=cld}
C {lab_pin.sym} -40 -20 0 1 {name=lsn lab=sn}
C {lab_pin.sym} -40 20 0 1 {name=lqn1 lab=qn}
C {lab_pin.sym} 40 0 0 0 {name=lq1 lab=q}
C {lab_pin.sym} 0 -40 0 0 {name=lva lab=vdd}
C {lab_pin.sym} 0 40 0 0 {name=lsa lab=vss}
C {lab_pin.sym} -40 180 0 1 {name=lrn lab=rn}
C {lab_pin.sym} -40 220 0 1 {name=lq2 lab=q}
C {lab_pin.sym} 40 200 0 0 {name=lqn2 lab=qn}
C {lab_pin.sym} 0 160 0 0 {name=lvb lab=vdd}
C {lab_pin.sym} 0 240 0 0 {name=lsb lab=vss}
