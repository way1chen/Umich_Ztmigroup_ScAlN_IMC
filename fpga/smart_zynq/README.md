# run from repo root for build

# first command for block design
# second command for bitstream

```sh
ROOT="$PWD/fpga/smart_zynq"
BUILD="$ROOT/build"
mkdir -p "$BUILD"
vivado -mode batch -log "$BUILD/create_project.log" -journal "$BUILD/create_project.jou" -source "$ROOT/vivado/create_project.tcl" -tclargs "$BUILD"
vivado -mode batch -log "$BUILD/build_bitstream.log" -journal "$BUILD/build_bitstream.jou" -source "$ROOT/vivado/build_bitstream.tcl" -tclargs "$BUILD"
```
