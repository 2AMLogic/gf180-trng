read_liberty /Users/rwalters/GitHub/gf180-trng/.loom/worktrees/issue-233/layout/.work/pdk-copy/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60.lib
read_lef /Users/rwalters/GitHub/gf180-trng/.loom/worktrees/issue-233/layout/.work/pdk-copy/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/techlef/gf180mcu_fd_sc_mcu9t5v0__nom.tlef
read_lef /Users/rwalters/GitHub/gf180-trng/.loom/worktrees/issue-233/layout/.work/pdk-copy/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lef/gf180mcu_fd_sc_mcu9t5v0.lef
read_def /Users/rwalters/GitHub/gf180-trng/.loom/worktrees/issue-233/layout/digital/trng_top.def
create_clock -name clk -period 1000.0 [get_ports clk]

# The six inter-region trunks that terminate on `digital` (#233),
# sourced from layout/floorplan/reports/interregion.json at run time
# -- permanent, not a one-off scenario, because re-deriving it costs
# nothing on every run while a pinned constant would go stale the
# moment #222's routing moves.
#
# All six are DIRECTION INPUT on trng_top (layout/digital/
# trng_top.def's own PINS section): raw_bit/raw_valid/ring_bit[0]/
# ring_bit[1] are genuinely combiner_sampler-driven inputs, and
# clk/rst_n are chip-pin-sourced inputs that also fan out to
# combiner_sampler along the same trunk (issue #233's Curator-
# verified correction). Neither group has a driver inside this
# digital-only netlist, which is what rules `set_load` out as the
# technique for all six rather than just for clk/rst_n: with no
# driver arc at the port there is nothing for a load to attach to,
# and OpenSTA reports bit-identical slack, slew and power with the
# trunks' as-built 15.6-30.7 fF and with 10 pF -- i.e. set_load
# here is a no-op that only looks like a measurement. Re-run that
# comparison with sdc_treatment_probe.py.
#
# What each port genuinely has is an edge arriving from off this
# netlist degraded by the trunk's own RC. At ff_n40C_3v60's own
# declared convention (30-70 % thresholds,
# slew_derate_from_library 0.5) a single-pole RC edge is
# 1.6946 * R * C in the table domain set_input_transition and
# max_transition both use -- lumped R and C, ideal source, so an
# upper bound on the trunk's own contribution (see InterfaceTrunk).
set_input_transition 0.003728 [get_ports {clk}]  ;# clk: 353.78 um, 106.13 ohm, 20.727 fF
set_input_transition 0.003430 [get_ports {rst_n}]  ;# rst_n: 339.34 um, 101.80 ohm, 19.881 fF
set_input_transition 0.008202 [get_ports {raw_bit}]  ;# raw_bit: 524.77 um, 157.43 ohm, 30.744 fF
set_input_transition 0.005941 [get_ports {raw_valid}]  ;# raw_valid: 446.61 um, 133.98 ohm, 26.165 fF
set_input_transition 0.003507 [get_ports {ring_bit[0]}]  ;# ring_bit1: 343.16 um, 102.95 ohm, 20.105 fF
set_input_transition 0.002099 [get_ports {ring_bit[1]}]  ;# ring_bit2: 265.47 um, 79.64 ohm, 15.553 fF

define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file /Users/rwalters/GitHub/gf180-trng/.loom/worktrees/issue-233/layout/.work/pdk-copy/gf180mcuD/libs.tech/openlane/rules.openrcx.gf180mcuD.min
write_spef /Users/rwalters/GitHub/gf180-trng/.loom/worktrees/issue-233/layout/.work/digital-sta/trng_top.ff_n40C_3v60.min.spef
read_spef /Users/rwalters/GitHub/gf180-trng/.loom/worktrees/issue-233/layout/.work/digital-sta/trng_top.ff_n40C_3v60.min.spef
puts "STA_METRIC worst_setup_slack_ideal_s [sta::worst_slack_cmd max]"
puts "STA_METRIC worst_hold_slack_ideal_s [sta::worst_slack_cmd min]"
set_propagated_clock [all_clocks]
set_power_activity -global -activity 0.25 -duty 0.5
puts "STA_METRIC period_ns 1000.0"
puts "STA_METRIC worst_setup_slack_s [sta::worst_slack_cmd max]"
puts "STA_METRIC worst_hold_slack_s [sta::worst_slack_cmd min]"
puts "STA_METRIC tns_setup_s [sta::total_negative_slack_cmd max]"
puts "STA_METRIC tns_hold_s [sta::total_negative_slack_cmd min]"
puts "STA_METRIC clock_skew_setup_s [sta::worst_clk_skew_cmd max 0]"
puts "STA_METRIC clock_skew_hold_s [sta::worst_clk_skew_cmd min 0]"
puts "STA_METRIC cell_area_m2 [rsz::design_area]"
puts "STA_METRIC utilization [rsz::utilization]"
report_worst_slack -max -digits 4
report_worst_slack -min -digits 4
report_tns -digits 4
report_checks -path_delay max -group_count 5 -digits 4 -format summary
report_checks -path_delay min -group_count 5 -digits 4 -format summary
report_clock_skew -setup -digits 4
report_power -digits 6
report_design_area
check_setup
set _mslim [sta::max_slew_check_limit]
if {$_mslim eq ""} { set _mslim nan }
puts "STA_METRIC max_slew_limit_ns $_mslim"
set _msslack [sta::max_slew_check_slack]
if {$_msslack eq ""} { set _msslack nan }
puts "STA_METRIC max_slew_slack_ns $_msslack"
puts "STA_METRIC max_slew_violations [sta::max_slew_violation_count]"
foreach _p [get_pins -of_objects [get_nets {clk}]] { puts "STA_IFACE_PIN clk [get_full_name $_p]" }
foreach _p [get_pins -of_objects [get_nets {rst_n}]] { puts "STA_IFACE_PIN rst_n [get_full_name $_p]" }
foreach _p [get_pins -of_objects [get_nets {raw_bit}]] { puts "STA_IFACE_PIN raw_bit [get_full_name $_p]" }
foreach _p [get_pins -of_objects [get_nets {raw_valid}]] { puts "STA_IFACE_PIN raw_valid [get_full_name $_p]" }
foreach _p [get_pins -of_objects [get_nets {ring_bit[0]}]] { puts "STA_IFACE_PIN ring_bit[0] [get_full_name $_p]" }
foreach _p [get_pins -of_objects [get_nets {ring_bit[1]}]] { puts "STA_IFACE_PIN ring_bit[1] [get_full_name $_p]" }
puts "STA_MAX_SLEW_VIOLATORS_BEGIN"
report_check_types -max_slew -violators -verbose
puts "STA_MAX_SLEW_VIOLATORS_END"
