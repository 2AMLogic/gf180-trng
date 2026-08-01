* jitter-estimator-calibration -- analytic anchor for the bit-extraction +
* min-entropy-estimator step, not (only) for the noise source itself.
*
* sim/tb/trnoise-calibration/tb_trnoise_cal.sp already pins down what a
* ngspice trnoise() source's arguments mean physically (S_w = 2*NA^2*NT,
* verified against two RC-filtered measurements in
* sim/records/2026-07-31-trnoise-calibration-01.md). This testbench reuses
* that SAME calibrated source and asks a different question: given a noise
* sample of KNOWN Gaussian statistics, does the downstream half of the
* pipeline -- threshold into a bit, then estimate min-entropy from the
* resulting stream -- recover the entropy theory predicts?
*
* vwhite delivers one fresh, independent, zero-mean Gaussian sample of
* standard deviation NA=vn_rms every NT=vn_dt seconds (a sample-and-hold
* process; NT here is set equal to the harness's linearize print step, so
* each grid point IS one held sample, not an interpolated one). Each held
* sample therefore has an EXACTLY known distribution: v(nw) ~ N(0, NA^2).
*
* A comparator that decides a bit by asking "does (deterministic offset +
* noise) cross zero" -- the same structural decision an RO-jitter sampler
* makes when accumulated phase noise competes against a fixed timing
* reference -- gives, for offset `bias`:
*
*     P(bit=1) = Phi(bias / NA)                          [[exact, not a bound]]
*
* where Phi is the standard normal CDF. spec/decision-records/DR-0012
* fixes `bias` at three levels chosen so P(bit=1) = 2^-H for H in
* {1.0, 0.5, 0.1} bit/sample -- see that record and
* sim/tools/jitter_estimator_calibration_check.py for the exact values and
* the derivation.
*
* This deliberately does NOT model RO phase accumulation/wraparound
* (sigma_acc(t) growing with t and wrapping mod the ring period T0, the
* Baudet-et-al. Q formula DR-0007 cites) -- that is the real jitter
* testbenches' (sim/tb/ro-inv-*-jitter/) and DR-0010's
* sim/tools/jitter_energy_law.py's territory. This testbench isolates the
* pipeline stage *downstream* of accumulated jitter: given a sample of
* known statistics, do thresholding and a most-common-value min-entropy
* point estimator recover the closed-form answer.

vwhite nw 0 dc 0 trnoise( vn_rms vn_dt 0 0)
rload nw 0 1meg
