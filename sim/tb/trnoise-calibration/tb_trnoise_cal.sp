* trnoise-calibration -- analytic anchor for ngspice TRNOISE source levels
*
* ngspice does NOT simulate device noise during `.tran`; every transient-
* noise result in this repo therefore comes from explicitly INJECTED
* `trnoise()` sources. That makes the mapping from the source's arguments
* to a physical noise power spectral density the single most load-bearing
* assumption on the transient-noise side of this characterization. This
* testbench measures that mapping instead of assuming it.
*
* trnoise( NA NT NALPHA NAMP ) generates a zero-mean Gaussian sample-and-
* hold sequence: a new sample of rms amplitude NA every NT seconds, plus a
* 1/f^NALPHA component of amplitude NAMP. For a sample-and-hold sequence
* the one-sided PSD in the flat region is
*
*     S_w = 2 * NA^2 * NT                       [V^2/Hz]
*
* rolling off as sinc^2(f*NT) with its first null at 1/NT.
*
* Filtering white noise of one-sided PSD S_w with an ideal single-pole RC
* (f_3dB = 1/(2*pi*R*C)) gives an output mean-square of
*
*     <v_o^2> = S_w * (pi/2) * f_3dB = S_w / (4*R*C)
*
* which is exact and independent of NA/NT individually. Two RC branches a
* decade apart therefore give two independent estimates of S_w, and their
* rms ratio must be sqrt(10) = 3.1623 if the sqrt(bandwidth) law holds.
*
* The 1/f branch is a weaker check by construction: the integral of a 1/f
* spectrum diverges logarithmically at low frequency, so its measured rms
* depends on the run length. It is recorded as an ORDER-OF-MAGNITUDE
* calibration only (see this testbench's records' Caveats).
*
* Parameters vn_rms / vn_dt / vn_flick are supplied by the harness manifest.

* ---- white source, two RC branches a decade apart ----------------------
vwhite nw 0 dc 0 trnoise( vn_rms vn_dt 0 0)
r1 nw o1 1k
c1 o1 0 1p
r2 nw o2 10k
c2 o2 0 1p

* ---- 1/f-only source, fast RC branch -----------------------------------
vflick nf 0 dc 0 trnoise( 0 vn_dt 1 vn_flick)
r3 nf o3 1k
c3 o3 0 1p
