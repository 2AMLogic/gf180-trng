read_liberty /home/ubuntu/.volare/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__ss_n40C_3v00.lib
read_lef /home/ubuntu/.volare/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/techlef/gf180mcu_fd_sc_mcu9t5v0__nom.tlef
read_lef /home/ubuntu/.volare/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lef/gf180mcu_fd_sc_mcu9t5v0.lef
read_def /home/ubuntu/loom-workspaces/gf180-trng/.loom/worktrees/issue-145/layout/digital/trng_top.def
create_clock -name clk -period 50.0 [get_ports clk]
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file /home/ubuntu/.volare/gf180mcuD/libs.tech/openlane/rules.openrcx.gf180mcuD.max
write_spef /home/ubuntu/loom-workspaces/gf180-trng/.loom/worktrees/issue-145/layout/.work/digital-sta/trng_top.ss_n40C_3v00.max.spef
read_spef /home/ubuntu/loom-workspaces/gf180-trng/.loom/worktrees/issue-145/layout/.work/digital-sta/trng_top.ss_n40C_3v00.max.spef
puts "STA_METRIC worst_setup_slack_ideal_s [sta::worst_slack_cmd max]"
puts "STA_METRIC worst_hold_slack_ideal_s [sta::worst_slack_cmd min]"
set_propagated_clock [all_clocks]
set_power_activity -global -activity 0.25 -duty 0.5
puts "STA_METRIC period_ns 50.0"
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

# Fmax by bisection on the clock period: the smallest period at
# which worst setup slack is still >= 0. Reported alongside the
# linear 1/(T - WNS) extrapolation the P&R flow's own
# report_fmax_metric uses, so the two can be compared rather
# than one of them assumed.
proc setup_slack_at {p} {
  create_clock -name clk -period $p [get_ports clk]
  set_propagated_clock [all_clocks]
  return [sta::worst_slack_cmd max]
}
set lo 0.1
set hi 50.0
puts "STA_METRIC bisect_slack_at_lo_s [setup_slack_at $lo]"
if {[setup_slack_at $lo] >= 0} {
  puts "STA_METRIC min_period_ns $lo"
} else {
  while {[expr {$hi - $lo}] > 0.001} {
    set mid [expr {($lo + $hi) / 2.0}]
    if {[setup_slack_at $mid] >= 0} { set hi $mid } else { set lo $mid }
  }
  puts "STA_METRIC min_period_ns $hi"
  puts "STA_METRIC min_period_slack_s [setup_slack_at $hi]"
  puts "STA_METRIC min_period_hold_slack_s [sta::worst_slack_cmd min]"
}
