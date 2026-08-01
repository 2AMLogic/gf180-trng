v {xschem version=3.4.4 file_version=1.2}
G {cta=2f ctb=2f cld=0.5f}
K {}
V {}
S {}
E {}
T {ro_meta_tap -- the metastability-hybrid stretch tap (issue #43).

A self-timed matched-delay strobe derived from an RO transition, feeding a
metastable arbiter. This is the architecture survey's Recommendation 2 and
DR-0007 section 1 verbatim: a SECONDARY tap layered onto the RO core, never
a free-standing metastability source. What is and is not claimed for it is
DR-0011; read that before citing anything about this cell.

  xin    driven from ro_array_core's combined node xo. One minimum-width
         gate input (xbi) is the ENTIRE load this cell presents: nothing
         here is in series with, or feeds back into, the rings. See
         "not in the core's path" below.
  mo     the tap's output. NOT a raw tap: DR-0001 puts the raw tap at a
         SAMPLER output, and mo is a source output that still has to be
         re-timed into the raw-tap domain by #9's sampler like xo does.
  vddm   the tap's own supply pin, deliberately separate from vdd and from
         either ring's vddr, so the tap's power is separately measurable
         and the per-ring liveness observation on vddr1/vddr2 stays clean.

Topology

  xin -> xbi -> s0 -+-> xa1(cld=cta) -> a1 -> xa2 -> pa -> arbiter sn
                    +-> xb1(cld=ctb) -> b1 -> xb2 -> pb -> arbiter rn

  xarb -> mq -> xbo -> mo

Both strobe paths are three inversions deep from xin and are built from
the same cell with the same parameters. They differ in EXACTLY ONE value:
the load cta/ctb on the first stage. That is deliberate and it is the
whole calibration story --

  * A rising xin drives pa and pb LOW together: the arbiter is asserted
    into its forced state.
  * The following falling xin releases pa and pb, separated by the path
    skew dt = t(pb) - t(pa), set by ctb - cta plus mismatch.

So one arbitration event happens per xin period, self-timed off the RO's
own transitions with no external clock -- the "self-timed matched-delay
strobe" the survey specifies.

Balance and calibration

Entropy requires |dt| to be comparable to the arbiter's regeneration time
constant tau. dt has two parts: a SYSTEMATIC part (ctb - cta, plus any
layout asymmetry) and a RANDOM part (device mismatch). The shipped default
is cta = ctb, i.e. the systematic part nulled, which leaves mismatch --
which nominal-model simulation cannot see -- setting the balance point.
This cell therefore ships UNCALIBRATED and no entropy is claimed from it.
cta/ctb are the trim knob a calibration scheme would drive; DR-0011 states
what the measured drift of dt over PVT implies about whether a one-time
trim can hold that balance.

Not in the core's path

The tap hangs off xo, which is an OUTPUT of ro_array_core: the rings drive
the XOR's inputs and nothing downstream of the XOR drives them back except
through the combining gate's own Cgd. ro_array_core is instantiated
UNCHANGED in ro_array_core_meta -- its schematic and its exported netlist
are untouched by this tap -- so "the tap does not gate the core's critical
path" is a structural property here, and the residual coupling is measured
rather than asserted (sim/tb/ro-array-core-meta-power/ against
sim/tb/ro-array-core-power/ at the same corners).} -1300 -900 0 0 0.25 0.25 {}
C {ipin.sym} -1300 -420 0 0 {name=p1 lab=xin}
C {opin.sym} -1200 -420 0 0 {name=p2 lab=mo}
C {iopin.sym} -1300 -380 0 0 {name=p3 lab=vddm}
C {iopin.sym} -1200 -380 0 0 {name=p4 lab=vss}
C {meta_inv.sym} 0 0 0 0 {name=xbi cld=cld}
C {meta_inv.sym} 300 -200 0 0 {name=xa1 cld=cta}
C {meta_inv.sym} 500 -200 0 0 {name=xa2 cld=cld}
C {meta_inv.sym} 300 200 0 0 {name=xb1 cld=ctb}
C {meta_inv.sym} 500 200 0 0 {name=xb2 cld=cld}
C {meta_arb.sym} 800 0 0 0 {name=xarb cld=cld}
C {meta_inv.sym} 1050 0 0 0 {name=xbo cld=cld}
C {lab_pin.sym} -50 -10 0 1 {name=lxin lab=xin}
C {lab_pin.sym} 50 -10 0 0 {name=ls0a lab=s0}
C {lab_pin.sym} 0 -50 0 0 {name=lv1 lab=vddm}
C {lab_pin.sym} 0 50 0 0 {name=lg1 lab=vss}
C {lab_pin.sym} 250 -210 0 1 {name=ls0b lab=s0}
C {lab_pin.sym} 350 -210 0 0 {name=la1a lab=a1}
C {lab_pin.sym} 300 -250 0 0 {name=lv2 lab=vddm}
C {lab_pin.sym} 300 -150 0 0 {name=lg2 lab=vss}
C {lab_pin.sym} 450 -210 0 1 {name=la1b lab=a1}
C {lab_pin.sym} 550 -210 0 0 {name=lpaa lab=pa}
C {lab_pin.sym} 500 -250 0 0 {name=lv3 lab=vddm}
C {lab_pin.sym} 500 -150 0 0 {name=lg3 lab=vss}
C {lab_pin.sym} 250 190 0 1 {name=ls0c lab=s0}
C {lab_pin.sym} 350 190 0 0 {name=lb1a lab=b1}
C {lab_pin.sym} 300 150 0 0 {name=lv4 lab=vddm}
C {lab_pin.sym} 300 250 0 0 {name=lg4 lab=vss}
C {lab_pin.sym} 450 190 0 1 {name=lb1b lab=b1}
C {lab_pin.sym} 550 190 0 0 {name=lpba lab=pb}
C {lab_pin.sym} 500 150 0 0 {name=lv5 lab=vddm}
C {lab_pin.sym} 500 250 0 0 {name=lg5 lab=vss}
C {lab_pin.sym} 760 -20 0 1 {name=lpab lab=pa}
C {lab_pin.sym} 760 20 0 1 {name=lpbb lab=pb}
C {lab_pin.sym} 840 -20 0 0 {name=lmqa lab=mq}
C {lab_pin.sym} 840 20 0 0 {name=lmqn lab=mqn}
C {lab_pin.sym} 800 -40 0 0 {name=lv6 lab=vddm}
C {lab_pin.sym} 800 40 0 0 {name=lg6 lab=vss}
C {lab_pin.sym} 1000 -10 0 1 {name=lmqb lab=mq}
C {lab_pin.sym} 1100 -10 0 0 {name=lmo lab=mo}
C {lab_pin.sym} 1050 -50 0 0 {name=lv7 lab=vddm}
C {lab_pin.sym} 1050 50 0 0 {name=lg7 lab=vss}
