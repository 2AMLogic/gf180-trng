v {xschem version=3.4.4 file_version=1.2}
G {cta=2f ctb=2f cld=0.5f}
K {}
V {}
S {}
E {}
T {ro_array_core_meta -- the entropy source with the metastability-hybrid
stretch tap attached (issue #43).

This cell exists so that the tap can be simulated in situ WITHOUT editing
ro_array_core. That is not a stylistic preference: the tap's first
acceptance criterion is that the core is unchanged in period, power and
swing, and the strongest available form of that evidence is that
design/xschem/ro_array_core.sch and design/ro_array_core.spice are
byte-identical to what they were before the tap existed. The comparison
that remains -- whether one extra gate load on xo perturbs the rings
through the combining gate's Cgd -- is measured, at PVT corners, by
running sim/tb/ro-array-core-meta-power/ against the SAME measurement set
as sim/tb/ro-array-core-power/.

  xcore   ro_array_core, unmodified. Its xo is the tap's only input.
  xtap    ro_meta_tap on its own supply pin vddm, so the tap's power is
          separately accountable against the ratified < 500 uW row and the
          per-ring liveness observation on vddr1/vddr2 stays clean.

  xo      still the combined RO node, still not the raw tap (DR-0001).
  mo      the tap's output, likewise not a raw tap -- see ro_meta_tap.

cta/ctb are forwarded to the tap so a testbench can detune the strobe
paths by a stated amount. A noiseless transient solver has no mechanism to
leave a perfectly balanced arbiter, so the balanced default (cta = ctb) is
a simulation dead end rather than a simulation result; deliberately
detuning, and saying by how much in the record, is the honest way to get a
convergent run out of this cell. DR-0011 makes that limitation the
centrepiece rather than a footnote.} -1200 -800 0 0 0.25 0.25 {}
C {ipin.sym} -1200 -420 0 0 {name=pe1 lab=en1}
C {ipin.sym} -1200 -380 0 0 {name=pe2 lab=en2}
C {iopin.sym} -1100 -420 0 0 {name=pv1 lab=vddr1}
C {iopin.sym} -1100 -380 0 0 {name=pv2 lab=vddr2}
C {iopin.sym} -1000 -420 0 0 {name=pv lab=vdd}
C {iopin.sym} -1000 -380 0 0 {name=pvm lab=vddm}
C {iopin.sym} -900 -420 0 0 {name=ps lab=vss}
C {opin.sym} -900 -380 0 0 {name=po lab=xo}
C {opin.sym} -800 -380 0 0 {name=pm lab=mo}
C {ro_array_core.sym} 0 0 0 0 {name=xcore}
C {ro_meta_tap.sym} 300 0 0 0 {name=xtap cta=cta ctb=ctb cld=cld}
C {lab_pin.sym} -70 -40 0 1 {name=le1 lab=en1}
C {lab_pin.sym} -70 -10 0 1 {name=le2 lab=en2}
C {lab_pin.sym} -30 -70 0 0 {name=lw1 lab=vddr1}
C {lab_pin.sym} 0 -70 0 0 {name=lw2 lab=vddr2}
C {lab_pin.sym} 30 -70 0 0 {name=lw3 lab=vdd}
C {lab_pin.sym} 0 70 0 0 {name=lg1 lab=vss}
C {lab_pin.sym} 70 0 0 0 {name=lxo1 lab=xo}
C {lab_pin.sym} 240 -10 0 1 {name=lxo2 lab=xo}
C {lab_pin.sym} 360 -10 0 0 {name=lmo lab=mo}
C {lab_pin.sym} 300 -60 0 0 {name=lwm lab=vddm}
C {lab_pin.sym} 300 60 0 0 {name=lg2 lab=vss}
