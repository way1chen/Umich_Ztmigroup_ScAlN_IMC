if {$argc < 1} { error "Pass the absolute build directory" }
set build_dir [file normalize [lindex $argv 0]]
set project_file [file join $build_dir imc_axi imc_axi.xpr]
open_project $project_file
set report_dir [file join $build_dir reports]
file mkdir $report_dir

launch_runs synth_1 -jobs 2
wait_on_run synth_1
set synth_status [get_property STATUS [get_runs synth_1]]
puts "SYNTH_STATUS $synth_status"
if {![string match {*Complete*} $synth_status]} {
    error "Synthesis did not complete: $synth_status"
}
open_run synth_1
report_utilization -file [file join $report_dir synthesis_utilization.rpt]
report_timing_summary -file [file join $report_dir synthesis_timing.rpt]
close_design

launch_runs impl_1 -to_step write_bitstream -jobs 2
wait_on_run impl_1
set impl_status [get_property STATUS [get_runs impl_1]]
puts "IMPL_STATUS $impl_status"
if {![string match {*Complete*} $impl_status]} {
    error "Implementation did not complete: $impl_status"
}
open_run impl_1
report_utilization -file [file join $report_dir implementation_utilization.rpt]
report_timing_summary -file [file join $report_dir implementation_timing.rpt]
report_drc -file [file join $report_dir implementation_drc.rpt]
close_design

write_hw_platform -fixed -include_bit -force \
    [file join $build_dir imc_axi.xsa]
puts "BITSTREAM [get_property DIRECTORY [get_runs impl_1]]/system_wrapper.bit"
puts "XSA [file join $build_dir imc_axi.xsa]"
