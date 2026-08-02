* sampler-dff-mc-offset -- sampler_dff's master-latch decision threshold
* under Monte Carlo device mismatch.
*
* DUT: the sampler_dff cell of design/sampler_core.spice (same cell
* sim/tb/sampler-dff-setup-hold/ characterizes deterministically).
*
* Why a DC sweep, and why clk = 0 the whole run. Per
* design/xschem/sampler_dff.sch's own header, the master latch's data
* transmission gate (TG_D) is transparent when clk = 0 and its OWN
* feedback gate (TG_FBM) is open (non-transparent) in that phase -- i.e.
* clk = 0 is the master's open-loop, non-bistable phase: node ``m`` is a
* single-valued (monotonic) function of ``d`` through TG_D, and node
* ``mb`` (the first inversion, INVM: m -> mb) is a single-valued function
* of ``m``. That is exactly the condition a ``.dc`` sweep needs to have a
* unique, convergence-friendly solution at every swept ``d`` -- no
* metastable tie, no bistable jump, because the loop that would make this
* cell bistable is open throughout. The slave latch is correspondingly in
* ITS hold phase (TG_S off, TG_FBS holding ``s``), so ``q`` does not move
* during this sweep; this testbench reads the master's own internal
* decision node, ``xdut.mb``, not ``q``.
*
* What "sampler offset" means here. sampler_dff has no analog comparator
* input by design (design/xschem/sampler_dff.sch: "the ONLY cell ... that
* turns an analog swing ... into a logic-level bit") -- it is an ordinary
* static CMOS transmission-gate flip-flop. Its closest analogue to a
* comparator's input-referred offset is the first inversion's (INVM's)
* own switching threshold: the ``d`` voltage at which ``mb`` crosses
* mid-supply. In a mismatch-free device this sits at VDD/2 by the cell's
* own symmetric P/N sizing (0.44u/0.22u, matching xor2/ro_stage); under
* device mismatch it shifts. Because the real entropy-source XOR node
* (design/xschem/ro_array_core.sch) drives ``d`` with a fast, rail-to-rail
* transition (design/README.md), a threshold sitting away from VDD/2 does
* not change WHETHER the cell captures correctly -- it changes WHEN,
* relative to the ring's own jitter-broadened crossing, biasing the
* captured bit's probability away from 1/2 by an amount set by the
* threshold offset divided by the crossing's slew rate. This testbench
* measures the offset; issue #13's own analysis converts it to a bias
* estimate using the array's own measured slew rate and jitter (both
* already committed evidence, cited rather than re-derived here).
*
* Scope: nominal corner only (tt/27C/3.30V), same rationale as
* sim/tb/ro-array-core-mc-freq/'s header.
*
* bvth is the same measurement-only mid-supply probe used throughout this
* repository's testbenches (e.g. sim/tb/ro-array-core-power/).

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 'vdd_val'
vclk clk 0 dc 0
vd d 0 dc 0

xdut d clk rst_n q vdd 0 sampler_dff

bvth vth 0 v = 0.5*vdd_val
