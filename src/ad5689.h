#ifndef AD5689_H
#define AD5689_H

#include <Arduino.h>
#include <SPI.h>

/**
 * AD5689 — 16-Bit Dual nanoDAC+ Driver
 * ======================================
 * Targeted at Teensy 4.1
 *
 * Tthe AD5689 generates two output voltages:
 *   DAC A → TOP_DRIVE  (ROW bias for memristor array)
 *   DAC B → BOT_DRIVE  (COL bias for memristor array)
 *
 * SPI frame format (24 bits total, sent MSB first):
 *  This is what gets sent to DAC from MCU through MOSI1
 *   Bits [23:20] — Command (4 bits) // tells DAC what to do
 *   Bits [19:16] — Address (4 bits) // VOUTA or VOUTBw
 *   Bits [15:0]  — 16-bit DAC value // 2^16 -1 = 65535 value that maps to output voltage within the reference voltage as the max (2.5 in our case)
 */

// ---------------------------------------------------------------------------
// Command Definitions (Datasheet Table 9)
// These go in the upper nibble of the first byte sent over SPI.
// ---------------------------------------------------------------------------
#define AD5689_CMD_NOP 0x0             // No operation — sends a blank frame
#define AD5689_CMD_WRITE_INPUT 0x1     // Write value to input register n (load into input reg and wait)
#define AD5689_CMD_UPDATE_DAC 0x2      // Update DAC Register n with contents of input register n (now update dac with what we got from above)
#define AD5689_CMD_WRITE_UPDATE 0x3    // Write to input register AND immediately update DAC output channel n — use this for normal operation (0x1 and 0x2 combined)
#define AD5689_CMD_POWER_CTRL 0x4      // Power down or power up DAC channel (controls power of DAC)
#define AD5689_CMD_LDAC_MASK 0x5       // Hardware LDAC (bar) mask register (chooses whether DAC channels update with LDAC)
#define AD5689_CMD_SOFT_RESET 0x6      // Software reset — returns all registers to power-on defaults (output goes to zero)
#define AD5689_CMD_REF_SETUP 0x7       // Internal reference setup register (enables or disables internal voltage ref [to use instead of external ref])
#define AD5689_CMD_DCEN_SETUP 0x8      // Set up DCEN register (daisy-chain enable) daisy chaining is when you cascade multiple DAC's through SDO and SDIN
#define AD5689_CMD_READBACK_SETUP 0x9  // Set up readback register (readback enable) (allows reading internal registers)
#define AD5689_CMD_NOP_DAISY 0xF       // No operation for daisy-chain mode

// ---------------------------------------------------------------------------
// Address Definitions (Datasheet Table 8)
// These go in the lower nibble of the first byte sent over SPI.
// ---------------------------------------------------------------------------
#define AD5689_ADDR_DAC_A 0x1  // Target DAC A only  → TOP_DRIVE in this system
#define AD5689_ADDR_DAC_B 0x8  // Target DAC B only  → BOT_DRIVE in this system || it was 0x2 and 0x8 for both before
#define AD5689_ADDR_BOTH 0x9   // Target both DAC A and DAC B simultaneously

// ---------------------------------------------------------------------------
// Internal Reference Control
// Passed as the data word to AD5689_CMD_REF_SETUP.
// ---------------------------------------------------------------------------
#define AD5689_REF_ON 0x0   // Enable internal 2.5V reference (power-on default)
#define AD5689_REF_OFF 0x1  // Disable internal reference — use this if supplying an external VREF

// ---------------------------------------------------------------------------
// SPI Settings
//
// Max clock per datasheet: 50 MHz.
// We use 30 MHz for stability on longer PCB traces.
// SPI mode 1 since CPOL is 0 and CPHA is is 1 -> sample on fall, shift on rise
// ---------------------------------------------------------------------------
static SPISettings ad5689Settings(30000000, MSBFIRST, SPI_MODE1);

// ---------------------------------------------------------------------------
// ad5689_write()
//
// MCU sends one 24-bit frame to the DAC.
//
// Frame structure sent on the wire:
//   Byte 1: [C3 C2 C1 C0 | A3 A2 A1 A0]   — command + address
//   Byte 2: [D15 D14 D13 D12 D11 D10 D9 D8] — upper 8 bits of DAC value
//   Byte 3: [D7 D6 D5 D4 D3 D2 D1 D0]      — lower 8 bits of DAC value
//
// @param bus   SPI bus instance (e.g. SPI or SPI1 on Teensy)
// @param cs    Chip select pin number
// @param cmd   Command nibble — use AD5689_CMD_* defines above
// @param addr  Address nibble — use AD5689_ADDR_* defines above
// @param data  16-bit DAC value (0x0000 = 0V, 0xFFFF = full scale)
// ---------------------------------------------------------------------------
inline void ad5689_write(SPIClass &bus, int cs, uint8_t cmd, uint8_t addr, uint16_t data) {
  // Pack command and address into a single header byte
  // Upper nibble = command, lower nibble = address
  // 0x0F is 00001111 which masks 4 bits from the right, since cmd is 8bit. Then shift 4 bits to left and bitwise OR with addr with same mask with bitwise AND
  uint8_t header = ((cmd & 0x0F) << 4) | (addr & 0x0F);

  bus.beginTransaction(ad5689Settings);
  digitalWriteFast(cs, LOW);  // Assert CS to begin transaction
  bus.transfer(header);  // Send 8-bit command + address
  bus.transfer16(data);  // Send 16-bit DAC value MSB first

  digitalWriteFast(cs, HIGH);  // Deassert CS — DAC latches the value on rising edge
  bus.endTransaction();
}

// ---------------------------------------------------------------------------
// ad5689_reset()
//
// Issues a software reset over SPI.
// Resets all DAC registers to their power-on default state (output = 0V).
// Call this once during setup() before configuring anything else.
//
// @param bus  SPI bus instance
// @param cs   Chip select pin number
// ---------------------------------------------------------------------------
inline void ad5689_reset(SPIClass &bus, int cs) {
  pinMode(cs, OUTPUT); // sets pin 38 as output
  digitalWriteFast(cs, HIGH);  // set high
  ad5689_write(bus, cs, AD5689_CMD_SOFT_RESET, 0, 0);
}

// ---------------------------------------------------------------------------
// ad5689_set_internal_ref()
//
// Enables or disables the AD5689's built-in 2.5V voltage reference.
//
// Use AD5689_REF_ON  if no external VREF is connected.
// Use AD5689_REF_OFF if supplying an external reference voltage to the VREF pin.
//
// NOTE: If the internal reference is off and no external reference is supplied,
// the DAC output will be unpredictable. 
//
// @param bus        SPI bus instance
// @param cs         Chip select pin number
// @param ref_state  AD5689_REF_ON or AD5689_REF_OFF
// ---------------------------------------------------------------------------
inline void ad5689_set_internal_ref(SPIClass &bus, int cs, uint8_t ref_state) {
  ad5689_write(bus, cs, AD5689_CMD_REF_SETUP, 0, (uint16_t)(ref_state & 0x01));
}


// later

// SDO (MISO) if we need to send stuff back to teensy for debugging

// LDAC if we need to sync top drive and bot drive ()

#endif  // AD5689_H
