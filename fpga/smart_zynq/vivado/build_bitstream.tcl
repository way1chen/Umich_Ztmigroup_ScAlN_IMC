set root_dir [file dirname [file dirname [file normalize [info script]]]]
set build_dir [file join $root_dir build]
if {![file exists [file join $root_dir constraints new_pcb_verified.xdc]]} {
    error "Bitstream blocked: provide verified package pins in constraints/new_pcb_verified.xdc. See README.md."
}
open_project [file join $build_dir imc_axi imc_axi.xpr]

launch_runs synth_1 -jobs 2
wait_on_run synth_1
if {![string match {*Complete*} [get_property STATUS [get_runs synth_1]]]} {
    error "Synthesis failed; inspect the Vivado run log."
}
launch_runs impl_1 -to_step write_bitstream -jobs 2
wait_on_run impl_1
if {![string match {*Complete*} [get_property STATUS [get_runs impl_1]]]} {
    error "Implementation failed; inspect the Vivado run log."
}
open_run impl_1
write_hw_platform -fixed -include_bit -force [file join $build_dir imc_axi.xsa]
puts "BITSTREAM [get_property DIRECTORY [get_runs impl_1]]/system_wrapper.bit"
puts "XSA [file join $build_dir imc_axi.xsa] (with bitstream)"
