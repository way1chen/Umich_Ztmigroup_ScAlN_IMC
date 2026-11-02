# Smart ZYNQ FPGA controller

AXI4-Lite controls raw DAC SPI transfers and four spike counters with independent
integrator reset. Target: `xc7z020clg484-2`; PL clock: 100 MHz; AXI base:
`0x43C00000`. ADC acquisition, array routing and classification are unimplemented.

## Setup

Use Vivado/Vitis **2025.2** with Zynq-7000 support and Cortex-A9 bare-metal Arm
GCC. Tests need Icarus Verilog. Run from this directory:

```bash
make project     # Create/reopen project and export XSA without bitstream
make vivado      # Open Vivado
make software    # Build the C smoke test in Vitis
make vitis       # Open the Vitis workspace
make test        # Run both RTL testbenches
make clean       # Delete generated build files and workspaces
```

Tools default to `/tools/AMD/2025.2`; override with `AMD_ROOT=/your/tool/path`.
In Vivado, choose **IP Integrator → Open Block Design → system**.
Project: `build/imc_axi/imc_axi.xpr`; top: `system_wrapper`.

Vitis workspace: `build/vitis/`; platform: `imc_platform`; domain:
`standalone_a9_0`; app: `axi_smoke`; output: `build/axi_smoke.elf`.
The app references `sw/` directly and runs in OCM because DDR settings are
unverified. Inspect `imc_smoke_result` in the debugger: 0 running, 1 pass,
3 scratch mismatch. No UART output.

Edit RTL in `rtl/`, application code in `sw/`, and project generation in
`vivado/`. All generated files go in ignored `build/`; save GUI project changes
in the source Tcl before `make clean`.

## Hardware

Still need to figure out package pin mapping.
`make hardware` requires `constraints/new_pcb_verified.xdc`, builds the
bitstream and exports `build/imc_axi.xsa` with it. Use Vivado Hardware Manager
and the Vitis debugger for board programming and debugging.

Ports: `dac_cs_n`, `dac_sclk`, `dac_mosi`, `dac_miso`, `spike[3:0]` and
`integrator_rst_n[3:0]`. Bit 0 is channel 1. Comparator pulse widths and minimum
analog reset duration still need measurement; short pulses can be missed.

## Registers

32-bit accesses; byte offsets below are relative to `0x43C00000`. Writable
registers honor byte strobes. Read-only/unmapped writes are ignored;
unmapped/unaligned reads return zero. The 8-bit local address aliases every
256 bytes within the 64 KiB AXI segment.

| Offset | Register | Access | Reset | Meaning |
| --- | --- | --- | --- | --- |
| `0x08` | SCRATCH | RW | 0 | Read/write smoke-test word |
| `0x0C` | COMMAND | WO | 0 | Issue one command; reads zero |
| `0x10` | STATUS | RO | 0 | Bits 0 busy, 1 done, 2 error, 3 counting enabled |
| `0x14` | ERROR | RO | 0 | 0 none, 1 busy, 2 unknown command, 3 invalid configuration |
| `0x28` | RESET_CYCLES | RW | 0 | Integrator reset duration in PL cycles; nonzero required |
| `0x40` | DAC_FRAME | RW | 0 | Bits 23:20 command, 19:16 address, 15:0 code; upper byte zero |
| `0x44` | SPI_HALF | RW | 10 | SPI half-period in PL cycles; valid 5–65535 |
| `0x54–0x60` | COUNT1–COUNT4 | RO | 0 | Live 32-bit saturating counts, spaced four bytes apart |
| `0x88` | DAC_RX | RO | 0 | Last completed raw 24-bit receive word |

Write configuration, issue COMMAND, poll for busy=0/done=1, then check ERROR.
Commands: **2 DAC**, **7 START**, **8 STOP**, **9 RESET**; zero is a no-op.
SPI captures its configuration on launch. START captures RESET_CYCLES;
START/STOP preserve counts. Commands during SPI busy are rejected except RESET.
RESET cancels SPI and clears configuration/counts, restores SPI_HALF=10 and
acknowledges with done=1. AXI reset also clears done.

DAC transfers use mode 0, MSB first, 24 clocks; default SCLK is 5 MHz.
DAC_RX is raw bus data. There is no automatic initialization or voltage
conversion. See `sw/imc_control.h` for the C API.

During counting, each HIGH-active comparator input passes through two
synchronizer flops. An accepted assertion counts once and drives that channel's
reset LOW for RESET_CYCLES. Re-arming requires LOW after reset release.
Startup resets and waits for LOW; outside counting, all resets stay LOW.
Clear wins over a coincident event. Counts are read individually, without a
shared snapshot. `sim/tb_spike_channel.sv` tests counting/reset;
`sim/tb_system.sv` tests AXI, SPI and integration.
