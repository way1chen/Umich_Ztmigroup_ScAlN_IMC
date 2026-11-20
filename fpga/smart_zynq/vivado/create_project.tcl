set script_dir [file dirname [file normalize [info script]]]
set root_dir [file dirname $script_dir]
set build_dir [file join $root_dir build]
set project_file [file join $build_dir imc_axi imc_axi.xpr]
file mkdir $build_dir
cd $build_dir

if {[file exists $project_file]} {
    open_project $project_file
} else {
    create_project imc_axi [file dirname $project_file] -part xc7z020clg484-2
    set_property target_language Verilog [current_project]
    add_files [glob [file join $root_dir rtl *.sv]]
    add_files [file join $root_dir board imc_axi_wrapper.v]
    add_files -fileset constrs_1 [file join $root_dir constraints scaln_cdc.xdc]
    update_compile_order -fileset sources_1
    source [file join $script_dir create_bd.tcl]
    generate_target all [get_files system.bd]
    make_wrapper -files [get_files system.bd] -top
    add_files -norecurse [file join $build_dir imc_axi imc_axi.gen sources_1 bd system hdl system_wrapper.v]
    set_property top system_wrapper [current_fileset]
}

set pcb_xdc [file join $root_dir constraints new_pcb_verified.xdc]
if {[file exists $pcb_xdc]} {
    if {[llength [get_files -quiet $pcb_xdc]] == 0} {
        add_files -fileset constrs_1 $pcb_xdc
    }
} else {
    puts "PCB pins unresolved: project and software setup available; bitstream blocked."
}
generate_target all [get_files system.bd]
update_compile_order -fileset sources_1
write_hw_platform -fixed -force [file join $build_dir imc_axi.xsa]
puts "PROJECT $project_file"
puts "XSA [file join $build_dir imc_axi.xsa] (without bitstream)"
