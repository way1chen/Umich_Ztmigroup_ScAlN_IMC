#ifndef IMC_CONTROL_H
#define IMC_CONTROL_H

#include <stdint.h>
#include "xil_io.h"
#include "imc_platform.h"

enum imc_register {
    IMC_SCRATCH=0x08, IMC_COMMAND=0x0C, IMC_OP_STATUS=0x10, IMC_ERROR=0x14,
    IMC_RESET_CYCLES=0x28, IMC_DAC_FRAME=0x40, IMC_SPI_HALF=0x44,
    IMC_COUNT1=0x54, IMC_COUNT2=0x58, IMC_COUNT3=0x5C, IMC_COUNT4=0x60,
    IMC_DAC_RX=0x88
};
enum imc_command { IMC_DAC=2, IMC_START=7, IMC_STOP=8, IMC_RESET=9 };
enum imc_error { IMC_OK=0, IMC_ERR_BUSY=1, IMC_ERR_COMMAND=2, IMC_ERR_CONFIG=3 };
#define IMC_POLL_TIMEOUT UINT32_MAX
#define IMC_PL_CLK_HZ 100000000u
#define IMC_DAC_VW 0u
#define IMC_DAC_RV 1u
#define IMC_DAC_VTH 2u

static inline uint32_t imc_read(uint32_t offset)
{
    return Xil_In32((UINTPTR)IMC_AXI_BASEADDR + offset);
}
static inline void imc_write(uint32_t offset, uint32_t value)
{
    Xil_Out32((UINTPTR)IMC_AXI_BASEADDR + offset, value);
}
static inline void imc_issue(enum imc_command command)
{
    imc_write(IMC_COMMAND, (uint32_t)command);
}
/* One software owner; issue a command, then wait for busy=0 and done=1. */
static inline uint32_t imc_wait_done(uint32_t poll_limit)
{
    while (poll_limit-- != 0u) {
        if ((imc_read(IMC_OP_STATUS) & 3u) == 2u) return imc_read(IMC_ERROR);
    }
    return IMC_POLL_TIMEOUT;
}
static inline uint32_t imc_execute(enum imc_command command, uint32_t poll_limit)
{
    imc_issue(command);
    return imc_wait_done(poll_limit);
}
/* Raw LTC2664 command/address/code. No voltage conversion or initialization. */
static inline uint32_t imc_dac(uint8_t command, uint8_t channel,
                               uint16_t code, uint32_t poll_limit)
{
    if (command > 15u || channel > 3u) return IMC_ERR_CONFIG;
    imc_write(IMC_DAC_FRAME, ((uint32_t)command << 20) |
              ((uint32_t)channel << 16) | code);
    return imc_execute(IMC_DAC, poll_limit);
}
#endif
