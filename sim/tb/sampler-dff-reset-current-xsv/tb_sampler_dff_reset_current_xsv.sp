* sampler-dff-reset-current-xsv -- static supply current of sampler_dff's
* xsv instance (design/sampler_core.spice: raw_valid path, D tied
* permanently to vdd) while reset is asserted and clk sits at the phase
* that leaves the input path conducting.
*
* Mechanism this bias point exists to interrogate (#48, design/README.md
* "sampler_dff: why a transmission-gate master-slave DFF"): sampler_dff's
* input transmission gate (XMtdp/XMtdn) is transparent whenever clk = 0.
* In the cell as #48 measured it, an async-reset pulldown (XMrm, node
* m -> vss) was also ON whenever rst_n = 0, so while BOTH held, whatever
* drives D had a resistive path through the input TG and that pulldown to
* vss. xsv's D is wired directly to vdd (sampler_core.spice: `xsv vdd clk
* rst_n raw_valid vdd vss sampler_dff`), so it was a static, continuous
* conduction path for the entire time reset was asserted with clk low --
* not a transient or a duty-cycled one. This testbench reproduces that
* exact bias (D = vdd, clk = 0, rst_n = 0) as a DC operating point.
*
* #53 then removed that path: reset is now gated into the two latches'
* own inverters (NAND2s taking rst_n) and there is no reset device on a
* storage node at all, so at this same bias nothing pulls node m against
* the transparent input TG and m simply sits at D. The testbench is
* UNCHANGED -- deliberately, so the two record sets are the same
* measurement on two cells and the before/after comparison is not a
* comparison of methods. What it now reads is whatever residual the
* biased cell draws, which is a leakage figure rather than a contention
* figure; the sign that the fix took is that this number collapsed by
* ~7 orders of magnitude, not that the testbench changed its mind about
* what it is measuring.
*
* Method: identical in spirit to sim/tb/ro-inv-05stage-stopped-leakage/
* and sim/tb/device-leakage-03v3/ -- an `op` analysis with rst_n and clk
* held at their reset-asserted DC values. On the pre-#53 cell the reported
* current was NOT leakage in the subthreshold sense those testbenches
* measure but deliberate resistive contention between two ON devices, and
* it was many orders of magnitude larger than either of those leakage
* figures (both nA-scale). On the post-#53 cell the conduction path is
* gone and the residual is comparable to them -- so the comparison those
* testbenches offer is meaningful for the new records and was not for the
* old ones. Read each record's own caveats, which say which cell it ran
* against.
*
* q is read alongside the current so the record proves reset actually
* held (q ~= 0) rather than measuring some other bias point.

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 0
vclk clk 0 dc 0

xdut vdd clk rst_n q vdd 0 sampler_dff
