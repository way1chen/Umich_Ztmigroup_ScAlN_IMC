# ============================================================
# OLD PCB PINOUT
# These constraints correspond to the previous PCB revision.
# They are intentionally disabled for the portable smart-zynq
# baseline. Replace with the new PCB pinout before bring-up.
# ============================================================
# Reference: Smart Zynq V1.2, 3x12 old array (10/5/2026)

# set_property -dict {PACKAGE_PIN M19 IOSTANDARD LVCMOS33} [get_ports clk_50]
# create_clock -name clk_50 -period 20.000 [get_ports clk_50]


# set_property -dict {PACKAGE_PIN H19 IOSTANDARD LVCMOS33} [get_ports {j5[0]}]
# set_property -dict {PACKAGE_PIN H20 IOSTANDARD LVCMOS33} [get_ports {j5[1]}]
# set_property -dict {PACKAGE_PIN E18 IOSTANDARD LVCMOS33} [get_ports {j5[2]}]
# set_property -dict {PACKAGE_PIN F18 IOSTANDARD LVCMOS33} [get_ports {j5[3]}]
# set_property -dict {PACKAGE_PIN F17 IOSTANDARD LVCMOS33} [get_ports {j5[4]}]
# set_property -dict {PACKAGE_PIN G17 IOSTANDARD LVCMOS33} [get_ports {j5[5]}]
# set_property -dict {PACKAGE_PIN C17 IOSTANDARD LVCMOS33} [get_ports {j5[6]}]
# set_property -dict {PACKAGE_PIN C18 IOSTANDARD LVCMOS33} [get_ports {j5[7]}]
# set_property -dict {PACKAGE_PIN G19 IOSTANDARD LVCMOS33} [get_ports {j5[8]}]
# set_property -dict {PACKAGE_PIN F19 IOSTANDARD LVCMOS33} [get_ports {j5[9]}]
# set_property -dict {PACKAGE_PIN E20 IOSTANDARD LVCMOS33} [get_ports {j5[10]}]
# set_property -dict {PACKAGE_PIN E19 IOSTANDARD LVCMOS33} [get_ports {j5[11]}]
# set_property -dict {PACKAGE_PIN D22 IOSTANDARD LVCMOS33} [get_ports {j5[12]}]
# set_property -dict {PACKAGE_PIN C22 IOSTANDARD LVCMOS33} [get_ports {j5[13]}]
# set_property -dict {PACKAGE_PIN B22 IOSTANDARD LVCMOS33} [get_ports {j5[14]}]
# set_property -dict {PACKAGE_PIN B21 IOSTANDARD LVCMOS33} [get_ports {j5[15]}]
# set_property -dict {PACKAGE_PIN B17 IOSTANDARD LVCMOS33} [get_ports {j5[16]}]
# set_property -dict {PACKAGE_PIN B16 IOSTANDARD LVCMOS33} [get_ports {j5[17]}]
# set_property -dict {PACKAGE_PIN A17 IOSTANDARD LVCMOS33} [get_ports {j5[18]}]
# set_property -dict {PACKAGE_PIN A16 IOSTANDARD LVCMOS33} [get_ports {j5[19]}]
# set_property -dict {PACKAGE_PIN D20 IOSTANDARD LVCMOS33} [get_ports {j5[20]}]
# set_property -dict {PACKAGE_PIN C20 IOSTANDARD LVCMOS33} [get_ports {j5[21]}]
# set_property -dict {PACKAGE_PIN B15 IOSTANDARD LVCMOS33} [get_ports {j5[22]}]
# set_property -dict {PACKAGE_PIN C15 IOSTANDARD LVCMOS33} [get_ports {j5[23]}]
# set_property -dict {PACKAGE_PIN D17 IOSTANDARD LVCMOS33} [get_ports {j5[24]}]
# set_property -dict {PACKAGE_PIN D16 IOSTANDARD LVCMOS33} [get_ports {j5[25]}]
# set_property -dict {PACKAGE_PIN D15 IOSTANDARD LVCMOS33} [get_ports {j5[26]}]
# set_property -dict {PACKAGE_PIN E15 IOSTANDARD LVCMOS33} [get_ports {j5[27]}]
# set_property -dict {PACKAGE_PIN D18 IOSTANDARD LVCMOS33} [get_ports {j5[28]}]
# set_property -dict {PACKAGE_PIN C19 IOSTANDARD LVCMOS33} [get_ports {j5[29]}]
# set_property -dict {PACKAGE_PIN E16 IOSTANDARD LVCMOS33} [get_ports {j5[30]}]
# set_property -dict {PACKAGE_PIN F16 IOSTANDARD LVCMOS33} [get_ports {j5[31]}]
# set_property -dict {PACKAGE_PIN G15 IOSTANDARD LVCMOS33} [get_ports {j5[32]}]
# set_property -dict {PACKAGE_PIN G16 IOSTANDARD LVCMOS33} [get_ports {j5[33]}]

# J5[0], header 7: sr_data
# set_property -dict {PACKAGE_PIN H19 IOSTANDARD LVCMOS33} [get_ports sr_data]
# J5[1], header 8: sr_clk
# set_property -dict {PACKAGE_PIN H20 IOSTANDARD LVCMOS33} [get_ports sr_clk]
# J5[2], header 9: sr_latch
# set_property -dict {PACKAGE_PIN E18 IOSTANDARD LVCMOS33} [get_ports sr_latch]
# J5[3], header 10: sr_oe_n
# set_property -dict {PACKAGE_PIN F18 IOSTANDARD LVCMOS33} [get_ports sr_oe_n]
# J5[4], header 11: dac_mosi
# set_property -dict {PACKAGE_PIN F17 IOSTANDARD LVCMOS33} [get_ports dac_mosi]
# J5[5], header 12: dac_sclk
# set_property -dict {PACKAGE_PIN G17 IOSTANDARD LVCMOS33} [get_ports dac_sclk]
# J5[6], header 13: dac_cs_n
# set_property -dict {PACKAGE_PIN C17 IOSTANDARD LVCMOS33} [get_ports dac_cs_n]
# J5[7], header 14: dac_reset_n
# set_property -dict {PACKAGE_PIN C18 IOSTANDARD LVCMOS33} [get_ports dac_reset_n]
# J5[8], header 15: adc_scl
# set_property -dict {PACKAGE_PIN G19 IOSTANDARD LVCMOS33} [get_ports adc_scl]
# J5[9], header 16: adc_sda
# set_property -dict {PACKAGE_PIN F19 IOSTANDARD LVCMOS33} [get_ports adc_sda]
# J5[10], header 17: ispp
# set_property -dict {PACKAGE_PIN E20 IOSTANDARD LVCMOS33} [get_ports ispp]
# J5[11], header 18: vp
# set_property -dict {PACKAGE_PIN E19 IOSTANDARD LVCMOS33} [get_ports vp]
# J5[12], header 19: cc1
# set_property -dict {PACKAGE_PIN D22 IOSTANDARD LVCMOS33} [get_ports cc1]
# J5[13], header 20: cc2
# set_property -dict {PACKAGE_PIN C22 IOSTANDARD LVCMOS33} [get_ports cc2]
# J5[14], header 21: cc3
# set_property -dict {PACKAGE_PIN B22 IOSTANDARD LVCMOS33} [get_ports cc3]
# J5[15], header 22: integrator_reset1
# set_property -dict {PACKAGE_PIN B21 IOSTANDARD LVCMOS33} [get_ports integrator_reset1]
# J5[16], header 23: integrator_reset2
# set_property -dict {PACKAGE_PIN B17 IOSTANDARD LVCMOS33} [get_ports integrator_reset2]
# J5[17], header 24: integrator_reset3
# set_property -dict {PACKAGE_PIN B16 IOSTANDARD LVCMOS33} [get_ports integrator_reset3]
# J5[18], header 25: board_control
# set_property -dict {PACKAGE_PIN A17 IOSTANDARD LVCMOS33} [get_ports board_control]
# J5[19], header 26: timing_pulse
# set_property -dict {PACKAGE_PIN A16 IOSTANDARD LVCMOS33} [get_ports timing_pulse]
