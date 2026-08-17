* sampler-dff-mc-offset-control -- deterministic negative control for
* sim/tb/sampler-dff-mc-offset/: same DUT, same measurement, mismatch
* disabled (tb.json's design_params sets sw_stat_mismatch=0).
*
* Why this exists (issue #146). #146's acceptance criteria requires a
* deterministic negative control next to the mismatch-enabled MC spread --
* the thing that distinguishes a real MC result from a noisy one: if the
* mismatch draw were NOT actually doing anything, the offset "spread"
* sim/tb/sampler-dff-mc-offset/'s record reports would be an artifact and
* this control run would look identical to it instead of collapsing to
* zero. With sw_stat_mismatch=0 the local mismatch offset every gf180mcu
* device computes is always multiplied to exactly zero regardless of which
* ``.option seed`` is active, so this testbench's dtrip_v measurement is
* bit-for-bit identical across every seed. This deck is otherwise IDENTICAL
* to sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset.sp -- see that
* file's header for the DUT, why a DC sweep with clk=0, what "sampler
* offset" means here, and the corner scope (the two same PVT points:
* tt/27 C/3.30 V and ss/125 C/3.63 V, DR-0015's binding corner).

vdd vdd 0 dc 'vdd_val'
vrst rst_n 0 dc 'vdd_val'
vclk clk 0 dc 0
vd d 0 dc 0

xdut d clk rst_n q vdd 0 sampler_dff

bvth vth 0 v = 0.5*vdd_val
