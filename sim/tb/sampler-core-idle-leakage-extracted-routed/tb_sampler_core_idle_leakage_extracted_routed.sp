* sampler-core-idle-leakage-extracted-routed -- issue #217's routing-level
* post-layout re-run of sim/tb/sampler-core-idle-leakage-extracted/ against
* layout/pex/sampler_core.routed.extracted.spice. Byte-identical to that
* testbench's own fragment except this header and the `xdutA`/`xdutB`
* lines (name `sampler_core_routed_extracted`). No measurement expression
* changes here -- those live in tb.json, and are addressed one hierarchy
* hop shallower than the leaf-level family's own (see tb.json's own
* caveats for why: this DUT has no intermediate ro_array_core-level
* instance).
*
* sampler-core-idle-leakage -- see the leaf-level family's own testbench
* header (sim/tb/sampler-core-idle-leakage-extracted/
* tb_sampler_core_idle_leakage_extracted.sp) for the full idle-state
* protocol, method notes and sign convention, all unchanged here.

vsup vsup 0 dc vdd_val

ven en 0 dc 0
vrst rst_n 0 dc 0 pulse(0 vdd_val 100n 1p 1p 10u 20u)
vclk0 clk0 0 dc 0 pulse(0 vdd_val 200n 1p 1p 100n 10u)
vclk1 clk1 0 dc 0 pulse(0 vdd_val 200n 1p 1p 10u 20u)

vsA vsup vddA dc 0
vsB vsup vddB dc 0

* Copy A: clock parked LOW. sampler_core_routed_extracted's header
* (layout/pex/build.py) declares the same 13 ports the leaf-level
* sampler_core_extracted does; ncA1/ncA2 are unused per-copy nets, vsubs
* ties to 0 explicitly at this call site, same convention as the
* leaf-level deck.
xdutA en en vddA vddA vddA 0 clk0 rst_n rbA rvA ncA1 ncA2 0 sampler_core_routed_extracted

* Copy B: clock parked HIGH.
xdutB en en vddB vddB vddB 0 clk1 rst_n rbB rvB ncB1 ncB2 0 sampler_core_routed_extracted

fqA qA 0 vsA 1
cqA qA 0 1n
rqA qA 0 1e12
fqB qB 0 vsB 1
cqB qB 0 1n
rqB qB 0 1e12
.ic v(qA)=0
.ic v(qB)=0
