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
* comparator's input-referred offset is the first inversion's own
* switching threshold: the ``d`` voltage at which ``mb`` crosses
* mid-supply. Since DR-0014-sampler-reset-gated-into-the-storage-loops
* (issue #53) that first inversion is a reset-gated NAND2 rather than a
* plain inverter -- ``rst_n`` is its second input, held HIGH here so the
* gate is in its inverting mode, and its NMOS stack is width-compensated
* (0.44u devices in series) rather than left at the plain cell's 0.22u.
* A series stack does not compensate exactly, so the switching threshold
* of the shipped cell is a property of THAT structure, not of a symmetric
* 0.44u/0.22u inverter; measuring it, rather than assuming VDD/2, is the
* point. Under device mismatch it shifts further. Because the real
* entropy-source XOR node
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
* Scope (issue #146): two PVT points, not a full corner sweep -- tt/27C/
* 3.30V (nominal) and ss/125C/3.63V (DR-0015's own measured entropy-binding
* worst corner), same rationale and same two points as
* sim/tb/ro-array-core-mc-freq/'s header. Before #146 this testbench's `.dc`
* sweep bound and mid-supply comparison were hardcoded to the single 3.30V
* nominal point (0-3.3V / 1.65V literals) and `corners` selection was inert
* (see tb.json's caveats) -- both are now parameterized by the PVT point via
* tb.json's `{vdd_val}`/`{vdd_half}` analyses fields.
*
* bvth is the same measurement-only mid-supply probe used throughout this
* repository's testbenches (e.g. sim/tb/ro-array-core-power/).

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 'vdd_val'
vclk clk 0 dc 0
vd d 0 dc 0

xdut d clk rst_n q vdd 0 sampler_dff

bvth vth 0 v = 0.5*vdd_val
