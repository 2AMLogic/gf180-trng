* ro-array-core-startup-extracted-routed -- issue #217's routing-level
* post-layout re-run of sim/tb/ro-array-core-startup-extracted/ against
* layout/pex/ro_array_core.routed.extracted.spice. Byte-identical to that
* testbench's own fragment except this header and the `xdut` line naming
* `ro_array_core_routed_extracted`. No measurement expression changes:
* `v(xdut.rn1)`/`v(xdut.rn2)` remain valid addresses for each ring's own
* output node (between the ring instance and its buffer instance,
* layout/pex/build.py's own `_ro_array_core_routed_subckt`), unchanged by
* the routing-level composition. No `.ic` used or needed -- see the
* leaf-level testbench's own header for why `en = 0` is already this
* circuit's unique, stable DC solution.
*
* See sim/characterization-post-layout-extracted.md's 2026-09-11 delta
* section and layout/pex/build.py's own module docstring for scope/limits.

vsup vsup 0 dc vdd_val
ven en 0 dc 0 pulse(0 vdd_val 5n 1p 1p 10u 20u)

xdut en en vsup vsup vsup 0 xo ro1 ro2 0 ro_array_core_routed_extracted

bvth vth 0 v = 0.5*vdd_val
