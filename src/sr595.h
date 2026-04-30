#ifndef SR595_H
#define SR595_H

#include <Arduino.h>
#include <SPI.h>

/**
 * 74HC595 — 8-Bit Shift Register Driver (Daisy-chained pair)
 * ============================================================
 * Controls row selection for the memristor array.
 *
 * Hardware setup:
 *   - Two 74HC595s daisy-chained on SPI1
 *   - MOSI1 = pin 26 (serial data in)
 *   - SCK1  = pin 27 (shift clock)
 *   - STCP  = pin 24 (storage/latch clock — active rising edge)
 *   - MR#   = tied to 3.3V (never in reset)
 *   - OE#   = pin 20
 *
 * Row select scheme:
 *   - 12 rows total: 8 bits from first 595 + 4 bits from second
 *   - One-hot ACTIVE LOW: selected row bit = 0, all others = 1
 *     (IN=0 on ADG5234 → SB connects → row gets ROW net)
 *     (IN=1 on ADG5234 → SA connects → row gets GND)
 *   - So "select row 3" = all 1s except bit 3 is 0
 *
 */

// ---------------------------------------------------------------------------
// Pin Definitions
// ---------------------------------------------------------------------------
#define PIN_SR_LATCH  24   // STCP — pulse HIGH to latch shifted data to outputs
#define PIN_OE 20          // OE# defaulted to 3.3V by pull up resistor, but teensy can set it low to activate

// ---------------------------------------------------------------------------
// SPI Settings for 74HC595
//
// Max clock per datasheet: ~25 MHz at 3.3V
// Use a conservative speed to start — you can increase later.
// Mode 0: data captured on rising edge
// ---------------------------------------------------------------------------
// TODO: Create SPISettings object for SPI1
//   - MSBFIRST or LSBFIRST depends on daisy-chain order — start with MSBFIRST
//     and adjust based on hardware testing
static SPISettings SR595Settings(10000000, MSBFIRST, SPI_MODE0); // might change msb or lsb depending on how bits are transferred


// ---------------------------------------------------------------------------
// Low-level: shifts 16 bits out on SPI1 and latches them.
// @param data  16-bit value to shift out. Only lower 12 bits matter for rows.
// ---------------------------------------------------------------------------
inline void sr595_shift_out(uint16_t data) {
    SPI1.beginTransaction(SR595Settings);
    SPI1.transfer16(data);
    SPI1.endTransaction();

    digitalWriteFast(PIN_SR_LATCH, HIGH); // latch was already low before, we drive high so bit is shift on rising edge
    delayMicroseconds(1);
    digitalWriteFast(PIN_SR_LATCH, LOW); // reset to low
    
}

// ---------------------------------------------------------------------------
// Call once in setup() to initialize SPI1 and the latch pin.
// ---------------------------------------------------------------------------
inline void sr595_init() {
    pinMode(PIN_SR_LATCH, OUTPUT); // in the perspective of teensy, I'm outputting STCP
    digitalWriteFast(PIN_SR_LATCH, LOW);
    pinMode(PIN_OE, OUTPUT);
    digitalWriteFast(PIN_OE, LOW);
    sr595_shift_out(0xFFFF); // deselect all rows
}

// select multiple rows at the same time
// exact mapping of which rows we want on, 0 is on, 1 is off. 
inline void sr595_select_multiple_rows(uint16_t mask) {
    sr595_shift_out(mask); // pass the mask directly to shift out
} 

// ---------------------------------------------------------------------------
// Selects a single row (1–12) by setting its bit LOW and all others HIGH.
//
// @param row  Row number 1-12
// ---------------------------------------------------------------------------
inline void sr595_select_row(uint8_t row) {
    uint16_t selection = ~((uint16_t)0x01 << (row-1)); // shift into the row we want for single rows between 1 and 12
    sr595_shift_out(selection);
}

// ---------------------------------------------------------------------------
// sr595_deselect_all()
//
// Deselects all rows (all bits HIGH = all rows connected to GND).
// Call this as a safe state between operations.
// ---------------------------------------------------------------------------
inline void sr595_deselect_all() {
    sr595_shift_out(0xFFFF);
}

#endif // SR595_H