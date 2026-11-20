#include <stdint.h>
#include "xil_io.h"
#include "imc_platform.h"

#define SCRATCH_OFFSET   0x08u
#define PATTERN          0xA5C35A3Cu

volatile uint32_t imc_smoke_result; // 0 running, 1 pass, 3 bad scratch
volatile uint32_t imc_smoke_scratch;

int main(void)
{
    const UINTPTR base = (UINTPTR)IMC_AXI_BASEADDR;
    Xil_Out32(base + SCRATCH_OFFSET, PATTERN);
    imc_smoke_scratch = Xil_In32(base + SCRATCH_OFFSET);
    imc_smoke_result = imc_smoke_scratch == PATTERN ? 1u : 3u;
    for (;;) {
        __asm__ volatile ("wfi");
    }
}
