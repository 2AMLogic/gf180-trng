* sampler-dff-reset-current-xsv -- static supply current of sampler_dff's
* xsv instance (design/sampler_core.spice: raw_valid path, D tied
* permanently to vdd) while reset is asserted and clk sits at the phase
* that leaves the input path conducting.
*
* Mechanism (#48, design/README.md "sampler_dff: why a transmission-gate
* master-slave DFF"): sampler_dff's input transmission gate (XMtdp/XMtdn)
* is transparent whenever clk = 0, and the async-reset pulldown XMrm (node
* m -> vss) is ON whenever rst_n = 0. While BOTH hold, whatever drives D
* has a resistive path through the input TG and the reset pulldown to
* vss. xsv's D is wired directly to vdd (sampler_core.spice: `xsv vdd clk
* rst_n raw_valid vdd vss sampler_dff`), so this is a static, continuous
* conduction path for the entire time reset is asserted with clk low --
* not a transient or a duty-cycled one. This testbench reproduces that
* exact bias (D = vdd, clk = 0, rst_n = 0) as a DC operating point.
*
* Method: identical in spirit to sim/tb/ro-inv-05stage-stopped-leakage/
* and sim/tb/device-leakage-03v3/ -- an `op` analysis with rst_n and clk
* held at their reset-asserted DC values. This is not leakage in the
* subthreshold sense those testbenches measure; it is deliberate resistive
* contention between two ON devices, so the reported current is expected
* to be many orders of magnitude larger than either of those leakage
* figures (both nA-scale) -- see the record's own comparison against
* design/README.md's <500 uW active-power budget.
*
* q is read alongside the current so the record proves reset actually
* held (q ~= 0) rather than measuring some other bias point.

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 0
vclk clk 0 dc 0

xdut vdd clk rst_n q vdd 0 sampler_dff
