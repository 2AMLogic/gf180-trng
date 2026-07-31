* noise-floor-resistor -- analytic anchor for ngspice `.noise` output units
*
* Two ideal 1 kohm resistors in a divider driven by a 0 V AC-1 source.
* Everything about this testbench is computable in closed form, which is
* exactly the point: it pins down what ngspice-46's `onoise_spectrum` /
* `onoise_total` vectors actually MEAN before any device noise figure
* recorded by this repo is allowed to lean on them.
*
* Closed-form expectations (Johnson-Nyquist, one-sided):
*   S_out(f)      = 4 k T (R1 || R2)              [V^2/Hz]
*   sqrt(S_out)   = sqrt(4 k T * 500 ohm)         [V/sqrt(Hz)], white
*   V_out,rms     = sqrt(S_out * (f_hi - f_lo))   [V rms]
*   gain(vn->out) = R2/(R1+R2) = 0.5              [V/V]
*   inoise        = onoise / gain                  = 2 * onoise
*
* Ideal (not PDK) resistors are used deliberately: the process corner must
* NOT move these numbers, so a process-corner shift showing up here would
* mean the harness is contaminating the analysis rather than the device
* being characterized. Temperature MUST move them, as sqrt(T) -- that is
* the second half of the anchor.
r1 nin nout 1k
r2 nout 0 1k
vn nin 0 dc 0 ac 1
