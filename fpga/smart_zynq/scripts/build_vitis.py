from pathlib import Path
import re
import shutil

import vitis


def main():
    root = Path(__file__).resolve().parents[1]
    build = root / "build"
    xsa = build / "imc_axi.xsa"
    if not xsa.is_file():
        raise RuntimeError("Run make project first")
    if not any(shutil.which(name) for name in ("arm-none-eabi-gcc", "arm-xilinx-eabi-gcc")):
        raise RuntimeError("Install the Zynq-7000/Cortex-A9 bare-metal Arm GCC tools in Vitis")

    workspace = build / "vitis"
    client = vitis.create_client()
    try:
        client.set_workspace(path=str(workspace))
        if (workspace / "imc_platform").exists():
            platform = client.get_component(name="imc_platform")
            platform.update_hw(hw_design=str(xsa))
        else:
            platform = client.create_platform_component(
                name="imc_platform", hw_design=str(xsa), os="standalone",
                cpu="ps7_cortexa9_0", domain_name="standalone_a9_0",
                architecture="32-bit", compiler="gcc",
                generate_dtb=False, no_boot_bsp=True,
            )
        platform.build()
        if (workspace / "axi_smoke").exists():
            app = client.get_component(name="axi_smoke")
        else:
            app = client.create_app_component(
                name="axi_smoke", platform=client.find_platform_in_repos("imc_platform"),
                domain="standalone_a9_0", template="empty_application",
            )
        app.import_files(
            from_loc=str(root / "sw"),
            files=["axi_smoke.c", "imc_platform.h", "imc_control.h"],
            dest_dir_in_cmp="src", is_skip_copy_sources=True,
        )

        # Keep the smoke test in OCM: the board's DDR configuration is unverified.
        linker = app.get_ld_script()
        linker.regenerate()
        linker.set_stack_size("0x2000")
        linker.set_heap_size("0x1000")
        ocm = [r["name"] for r in linker.get_memory_regions()
               if r["name"].startswith("ps7_ram_")
               and int(r["base_address"], 0) == 0 and int(r["size"], 0) >= 0x10000]
        if len(ocm) != 1:
            raise RuntimeError(f"Expected one generated low OCM region; found {ocm}")
        path = Path(linker.file_path)
        text, placements = re.subn(
            r"([ \t]+>[ \t]*)([A-Za-z_][A-Za-z_0-9]*)\b",
            lambda match: match[1] + ocm[0], path.read_text(),
        )
        if not placements:
            raise RuntimeError("No linker section placements found")
        path.write_text(text)
        app.build()
        elfs = list(Path(app.component_location).rglob("*.elf"))
        if len(elfs) != 1:
            raise RuntimeError(f"Expected one application ELF; found {elfs}")
        shutil.copy2(elfs[0], build / "axi_smoke.elf")
        print(f"ELF {build / 'axi_smoke.elf'}")
    finally:
        vitis.dispose()


if __name__ == "__main__":
    main()
