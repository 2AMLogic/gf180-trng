* ro-ring5-starved-jitter-long -- long-window transient-noise jitter of ONE
* 5-stage ring built from the SHIPPED starved delay cell.
*
* Why this testbench exists
* -------------------------
* DR-0010's rate row rests on the jitter-energy invariant
*
*     a  =  kappa^2 * P_ring / (k_B * T)   =   1.79 +/- 0.14          (*)
*
* which is fitted to a PLAIN, unstarved 5-stage inverter ring
* (sim/tb/ro-inv-05stage-jitter/). The cell this project ships is a
* minimum-width, series-STARVED inverter (design/xschem/ro_stage.sch), and
* DR-0010 names the gap between the two as its own largest open risk.
*
* The only transient-noise run of the shipped-cell family so far
* (sim/records/2026-08-01-ro-array-sanity-jitter-01.md) measured a window of
* 16 periods opened at the second edge after start-up. Two independent
* diagnostics in that record say what it actually measured was deterministic
* settling drift, not jitter: its sigma varies by only 0.3 % across three
* independent noise seeds (a 16-period jitter estimate has a ~1/sqrt(2*16) =
* 18 % seed-to-seed spread), and it accumulates as lag^0.81 instead of the
* lag^0.5 of a random walk. This testbench is the corrected measurement.
*
* What is different from sim/tb/ro-array-sanity-jitter/
* ----------------------------------------------------
* The delay cell is deliberately identical -- ring 1 of that array, device
* for device: a ro_nand2 enable stage plus four ro_stage, wstv = 0.220 um,
* lstv = 2 um, cld = 0.5 f, with one trnoise() source in series with every
* stage input at the same fixed injected density. Three things change:
*
*   1. the other three rings and the XOR tree are gone. The three other rings
*      share nothing with ring 1 (separate supply pins, no shared node), so
*      dropping them changes nothing electrically. The XOR tree is NOT in
*      that category and this deck does not pretend it is: in the array,
*      ring 1's output node ro1 drives the `a` input of xa1, i.e. four
*      transistor gates (2x 0.44 um pfet, 1x 0.88 um pfet, 1x 0.44 um nfet).
*      Removing the tree therefore UNLOADS ro1, and the ring runs measurably
*      faster for it -- ~2.56 ns per period here against the 3.31 ns
*      2026-08-01-ro-array-sanity-jitter-01.md reports at tt/27 C/3.30 V
*      (that record's own figure is itself start-up-contaminated, so the two
*      are not cleanly separable; see the Caveats of the records this deck
*      produces). The unloaded ring is used here deliberately, because it is
*      then topologically the SAME experiment as the plain-cell reference
*      family sim/tb/ro-inv-05stage-jitter/, whose ring output is likewise
*      probe-only -- and that family is what (*) is fitted to. This deck's
*      job is to compare a starved cell with a plain one, so the delay cell
*      must be the only variable, and the output loading must not be;
*   2. the measurement window opens 256 periods after start-up instead of at
*      the second edge; and
*   3. the window is 512 periods rather than 16, so the accumulation exponent
*      can be fitted over lags 1..128, i.e. 2.11 decades.
*
* What that comparability does and does not extend to
* ---------------------------------------------------
* kappa^2 and P_ring are measured HERE, on the same ring, in the SAME run, so
* the quantity (*) is about -- their product -- is internally consistent
* whatever the loading. What the unloaded ring does NOT license is quoting
* this deck's T0, P_ring or E_cycle as the shipped array's; for those, cite
* the ro-array-core-power family, which measures the array as built.
*
* Injected per-stage input-referred white PSD (harness params vn_rms /
* vn_dt, see tb.json):
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* fixed across the PVT grid, so what varies corner to corner is the
* circuit's noise-to-jitter conversion, not the stimulus. Recovering the
* physical jitter needs the per-corner device-noise density of THIS cell,
* which sim/tb/rostage-noise/ measures (inoise_dens_1g).
*
* The charge integrator (fq1/cq1/rq1, as in sim/tb/ro-inv-05stage-power/)
* runs alongside so that the ring's energy per cycle and its jitter come
* from the SAME run: (*) relates exactly those two quantities, and relating
* them across two runs would import a needless cross-run assumption. Its
* window is the jitter window, not the whole run, so the start-up transient
* is excluded from the power figure too.
*
* bx1 is a measurement-only probe: it shifts the ring output so a
* mid-supply crossing becomes a zero crossing that `meas ... when v(x1)=0`
* finds at any supply. It is a behavioural B-source and presents no load.
*
* Only v(x1), v(q1) and v(vsup) are `save`d (see tb.json). Nothing else is
* read by any measurement, and at 1 ps print step over 2.4 us the full node
* set is ~1.5 GB of stored waveform per seeded run -- enough, at eight
* concurrent seeds, to push a shared build host into memory compression and
* slow every run on it, including this one.
*
* Start-up: the enable is held HIGH from t = 0 and the ring is kicked out of
* its unstable DC solution by a .ic, exactly as sim/tb/ro-inv-05stage-jitter/
* and sim/tb/ro-array-sanity-jitter/ do (an enable EDGE does not converge
* with trnoise() sources active in ngspice-42/46 -- a solver limit recorded
* in those testbenches and in every record they produce). Here that matters
* less than it did there, because the whole point of this deck is that the
* measurement window opens long after any start-up transient has decayed,
* and tb.json's per-block period measurements make that decay visible in
* the record instead of assuming it.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring supply pin, so the charge integrator sees the ring
*      current alone (identical arrangement to ro-array-sanity-jitter) ----
vr1 vsup vddr1 dc 0

* ---- the ring: ro_nand2 enable stage + four ro_stage, wstv = 0.220u ----
xg1 g10 en n11 vddr1 0 ro_nand2 wstv=0.220u lstv=2u cld=0.5f
x11 g11 n12 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x12 g12 n13 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x13 g13 n14 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x14 g14 ro1 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
vn10 ro1 g10 dc 0 trnoise( vn_rms vn_dt 0 0)
vn11 n11 g11 dc 0 trnoise( vn_rms vn_dt 0 0)
vn12 n12 g12 dc 0 trnoise( vn_rms vn_dt 0 0)
vn13 n13 g13 dc 0 trnoise( vn_rms vn_dt 0 0)
vn14 n14 g14 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- charge integrator: q1 is the ring's accumulated supply charge ----
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12

* ---- measurement probe ------------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
