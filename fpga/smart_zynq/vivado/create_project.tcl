set script_dir [file dirname [file normalize [info script]]]
set root_dir [file dirname $script_dir]
if {$argc > 0} {
    set build_dir [file normalize [lindex $argv 0]]
} else {
    set build_dir [file normalize [file join $root_dir build]]
}
file mkdir $build_dir
cd $build_dir
create_project imc_axi [file join $build_dir imc_axi] \
    -part xc7z020clg484-2 -force
set_property target_language Verilog [current_project]
add_files [glob [file join $root_dir rtl *.sv]]
add_files [file join $root_dir board imc_axi_wrapper.v]
add_files -fileset constrs_1 [list \
    [file join $root_dir constraints old_pcb_pinout.xdc]]
update_compile_order -fileset sources_1

source [file join $script_dir create_bd.tcl]
generate_target all [get_files system.bd]
make_wrapper -files [get_files system.bd] -top
add_files -norecurse [glob [file join $build_dir imc_axi \
    imc_axi.gen sources_1 bd system hdl system_wrapper.v]]
set_property top system_wrapper [current_fileset]
update_compile_order -fileset sources_1
puts "PROJECT_READY [current_project]"
