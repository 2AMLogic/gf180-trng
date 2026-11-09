read_liberty /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib
read_lef /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/techlef/gf180mcu_fd_sc_mcu9t5v0__nom.tlef
read_lef /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lef/gf180mcu_fd_sc_mcu9t5v0.lef
read_def /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/digital/trng_top.def
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
# netlist degraded by the trunk's own RC. At tt_025C_3v30's own
# declared convention (30-70 % thresholds,
# slew_derate_from_library 0.5) a single-pole RC edge is
# 1.6946 * R * C in the table domain set_input_transition and
# max_transition both use -- lumped R and C, ideal source, so an
# upper bound on the net's own contribution (see InterfaceTrunk).
set_input_transition 0.027890 [get_ports {clk}]  ;# clk: trunk 430.62 um + legs 540.60 um, 277.83 ohm, 59.238 fF
set_input_transition 0.030587 [get_ports {rst_n}]  ;# rst_n: trunk 430.31 um + legs 593.80 um, 288.59 ohm, 62.545 fF
set_input_transition 0.043251 [get_ports {raw_bit}]  ;# raw_bit: trunk 607.49 um + legs 610.04 um, 345.20 ohm, 73.938 fF
set_input_transition 0.040725 [get_ports {raw_valid}]  ;# raw_valid: trunk 547.95 um + legs 637.48 um, 333.03 ohm, 72.163 fF
set_input_transition 0.033401 [get_ports {ring_bit[0]}]  ;# ring_bit1: trunk 487.75 um + legs 578.68 um, 303.42 ohm, 64.959 fF
set_input_transition 0.029814 [get_ports {ring_bit[1]}]  ;# ring_bit2: trunk 427.56 um + legs 580.36 um, 285.91 ohm, 61.535 fF

read_spef /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta/trng_top.tt_025C_3v30.min.spef
set_propagated_clock [all_clocks]
puts "ACT_BEGIN alarm-gated reset"
read_vcd -scope tb/dut -begin_time 0 -end_time 8000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/alarm-gated.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN alarm-gated startup"
read_vcd -scope tb/dut -begin_time 8000000 -end_time 1048000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/alarm-gated.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN alarm-gated steady"
read_vcd -scope tb/dut -begin_time 1145000000 -end_time 2169000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/alarm-gated.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN backpressure reset"
read_vcd -scope tb/dut -begin_time 0 -end_time 8000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/backpressure.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN backpressure startup"
read_vcd -scope tb/dut -begin_time 8000000 -end_time 1048000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/backpressure.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN backpressure steady"
read_vcd -scope tb/dut -begin_time 1048000000 -end_time 2072000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/backpressure.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN conditioned-streaming reset"
read_vcd -scope tb/dut -begin_time 0 -end_time 8000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/conditioned-streaming.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN conditioned-streaming startup"
read_vcd -scope tb/dut -begin_time 8000000 -end_time 1048000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/conditioned-streaming.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN conditioned-streaming steady"
read_vcd -scope tb/dut -begin_time 1048000000 -end_time 2072000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/conditioned-streaming.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN disabled-clock-running reset"
read_vcd -scope tb/dut -begin_time 0 -end_time 8000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/disabled-clock-running.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN disabled-clock-running startup"
read_vcd -scope tb/dut -begin_time 8000000 -end_time 1048000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/disabled-clock-running.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN disabled-clock-running steady"
read_vcd -scope tb/dut -begin_time 1048000000 -end_time 2072000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/disabled-clock-running.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN raw-streaming reset"
read_vcd -scope tb/dut -begin_time 0 -end_time 8000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/raw-streaming.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN raw-streaming startup"
read_vcd -scope tb/dut -begin_time 8000000 -end_time 1048000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/raw-streaming.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
puts "ACT_BEGIN raw-streaming steady"
read_vcd -scope tb/dut -begin_time 1048000000 -end_time 2072000000 /home/ubuntu/GitHub/gf180-trng/.loom/worktrees/issue-709/layout/.work/digital-sta-activity/raw-streaming.vcd
report_activity_annotation
report_power -digits 6
puts "ACT_END"
