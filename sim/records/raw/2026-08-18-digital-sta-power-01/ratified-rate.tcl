read_liberty /home/ubuntu/.volare/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib
read_lef /home/ubuntu/.volare/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/techlef/gf180mcu_fd_sc_mcu9t5v0__nom.tlef
read_lef /home/ubuntu/.volare/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lef/gf180mcu_fd_sc_mcu9t5v0.lef
read_def /home/ubuntu/loom-workspaces/gf180-trng/.loom/worktrees/issue-183/layout/digital/trng_top.def
create_clock -name clk -period 1000.0 [get_ports clk]
define_process_corner -ext_model_index 0 X
extract_parasitics -ext_model_file /home/ubuntu/.volare/gf180mcuD/libs.tech/openlane/rules.openrcx.gf180mcuD.min
write_spef /home/ubuntu/loom-workspaces/gf180-trng/.loom/worktrees/issue-183/layout/.work/digital-sta/trng_top.ss_125C_3v00.min.spef
read_spef /home/ubuntu/loom-workspaces/gf180-trng/.loom/worktrees/issue-183/layout/.work/digital-sta/trng_top.ss_125C_3v00.min.spef
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
