create_bd_design system
set ps [create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 ps7]

# Device-level PS defaults must be reviewed for the actual Zynq board,
# especially DDR, MIO, and PS clock. Only the PL AXI settings are generic.
set_property -dict [list \
    CONFIG.PCW_FPGA0_PERIPHERAL_FREQMHZ {100} \
    CONFIG.PCW_FPGA_FCLK0_ENABLE {1} \
    CONFIG.PCW_USE_M_AXI_GP0 {1} \
] $ps

set imc [create_bd_cell -type module \
    -reference imc_axi_wrapper imc]
set ic [create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:* axi_ic]
set_property -dict [list CONFIG.NUM_SI {1} CONFIG.NUM_MI {1}] $ic
set rst [create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:* axi_reset]
set locked [create_bd_cell -type ip -vlnv xilinx.com:ip:xlconstant:* pll_locked]
set_property CONFIG.CONST_VAL {1} $locked

make_bd_intf_pins_external [get_bd_intf_pins ps7/DDR]
make_bd_intf_pins_external [get_bd_intf_pins ps7/FIXED_IO]

connect_bd_intf_net [get_bd_intf_pins ps7/M_AXI_GP0] \
    [get_bd_intf_pins axi_ic/S00_AXI]
connect_bd_intf_net [get_bd_intf_pins axi_ic/M00_AXI] \
    [get_bd_intf_pins imc/S_AXI]
connect_bd_net [get_bd_pins ps7/FCLK_CLK0] \
    [get_bd_pins ps7/M_AXI_GP0_ACLK] \
    [get_bd_pins axi_ic/ACLK] [get_bd_pins axi_ic/S00_ACLK] \
    [get_bd_pins axi_ic/M00_ACLK] \
    [get_bd_pins axi_reset/slowest_sync_clk] [get_bd_pins imc/s_axi_aclk]
connect_bd_net [get_bd_pins ps7/FCLK_RESET0_N] \
    [get_bd_pins axi_reset/ext_reset_in]
connect_bd_net [get_bd_pins pll_locked/dout] \
    [get_bd_pins axi_reset/dcm_locked]
connect_bd_net [get_bd_pins axi_reset/interconnect_aresetn] \
    [get_bd_pins axi_ic/ARESETN]
connect_bd_net [get_bd_pins axi_reset/peripheral_aresetn] \
    [get_bd_pins axi_ic/S00_ARESETN] [get_bd_pins axi_ic/M00_ARESETN] \
    [get_bd_pins imc/s_axi_aresetn]

assign_bd_address
set target_seg [get_bd_addr_segs imc/S_AXI/*]
if {[llength $target_seg] != 1} {
    error "Expected one IMC AXI address segment, found $target_seg"
}
set mapped_seg [get_bd_addr_segs -of_objects [get_bd_addr_spaces ps7/Data] \
    -filter {NAME =~ *imc*}]
if {[llength $mapped_seg] != 1} {
    error "Expected one mapped IMC segment, found $mapped_seg"
}
set_property offset 0x43C00000 $mapped_seg
set_property range 64K $mapped_seg

validate_bd_design
save_bd_design
puts "IMC_BASE [get_property offset $mapped_seg]"
puts "FCLK_MHZ [get_property CONFIG.PCW_ACT_FPGA0_PERIPHERAL_FREQMHZ $ps]"
