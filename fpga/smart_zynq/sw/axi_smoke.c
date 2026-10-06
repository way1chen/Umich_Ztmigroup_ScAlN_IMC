/* Standalone Vitis application: PS -> AXI4-Lite -> IMC register smoke test. */
#include <stdint.h>
#include "xil_io.h"
#include "xil_printf.h"
#include "imc_platform.h"

#define REG_CONTROL   0x00u
#define REG_STATUS    0x04u
#define REG_SCRATCH   0x08u
#define REG_DESIGN_ID 0xFCu
#define DESIGN_ID     0x494D4301u

int main(void)
{
    const UINTPTR base = (UINTPTR)IMC_AXI_BASEADDR;
    const uint32_t pattern = 0xA5C35A3Cu;
    uint32_t id = Xil_In32(base + REG_DESIGN_ID);
    uint32_t scratch;
    uint32_t status;

    Xil_Out32(base + REG_SCRATCH, pattern);
    scratch = Xil_In32(base + REG_SCRATCH);
    Xil_Out32(base + REG_CONTROL, pattern);
    status = Xil_In32(base + REG_STATUS);
    xil_printf("IMC AXI id=%08x scratch=%08x status=%08x\r\n",
               (unsigned int)id, (unsigned int)scratch, (unsigned int)status);
    if (id != DESIGN_ID || scratch != pattern || status != pattern) {
        xil_printf("IMC AXI smoke test failed\r\n");
        return 1;
    }
    xil_printf("IMC AXI smoke test passed\r\n");
    return 0;
} // written by claude just a smoke test
