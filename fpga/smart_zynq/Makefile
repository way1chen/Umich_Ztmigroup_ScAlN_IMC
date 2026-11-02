SHELL := /bin/bash
.DEFAULT_GOAL := project
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BUILD := $(ROOT)/build
AMD_ROOT ?= /tools/AMD/2025.2
VIVADO := $(AMD_ROOT)/Vivado/bin/vivado
VITIS := $(AMD_ROOT)/Vitis/bin/vitis

.PHONY: project vivado vitis hardware software test clean

project:
	@mkdir -p "$(BUILD)"
	@cd "$(BUILD)" && "$(VIVADO)" -mode batch -log project.log -journal project.jou -source "$(ROOT)/vivado/create_project.tcl"

vivado: project
	@cd "$(BUILD)" && "$(VIVADO)" "$(BUILD)/imc_axi/imc_axi.xpr"

vitis:
	@mkdir -p "$(BUILD)"
	@cd "$(BUILD)" && XILINX_VITIS_DATA_DIR="$(BUILD)/vitis_config" "$(VITIS)" -w "$(BUILD)/vitis"

software: project
	@source "$(AMD_ROOT)/Vitis/settings64.sh" && cd "$(BUILD)" && XILINX_VITIS_DATA_DIR="$(BUILD)/vitis_config" "$(VITIS)" -s "$(ROOT)/scripts/build_vitis.py"

hardware: project
	@cd "$(BUILD)" && "$(VIVADO)" -mode batch -log hardware.log -journal hardware.jou -source "$(ROOT)/vivado/build_bitstream.tcl"

test:
	@mkdir -p "$(BUILD)/test"
	@set -e; for top in tb_spike_channel tb_system; do \
		iverilog -g2012 -s $$top -o "$(BUILD)/test/$$top.vvp" "$(ROOT)"/rtl/*.sv "$(ROOT)/board/imc_axi_wrapper.v" "$(ROOT)/sim/$$top.sv"; \
		vvp "$(BUILD)/test/$$top.vvp"; \
	done

clean:
	rm -rf "$(BUILD)"
