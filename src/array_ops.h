#ifndef ARRAY_OPS_H
#define ARRAY_OPS_H

#include <Arduino.h>
#include "ad5689.h"
#include "ad7689.h"
#include "sr595.h"
#include "analog_io.h"

#include <math.h>

/**
 * Array Operations — Mid-Level Control
 * ======================================
 * Coordinates DAC, ADC, shift registers, and analog switches
 * to perform read/write operations on individual memristor cells.
 *
 */

// ---------------------------------------------------------------------------
// Pin Definitions — Analog Switches
// ---------------------------------------------------------------------------
#define PIN_ISPP    2    // ISPP switch IN
#define PIN_VP      22   // U4 switch IN: HIGH=BOT_DRIVE, LOW=GND 
#define PIN_CC1     3    // Col 1 switch IN: HIGH=TIA, LOW=SA (U4 output)
#define PIN_CC2     4    // Col 2 switch IN: HIGH=TIA, LOW=SA 
#define PIN_CC3     5    // Col 3 switch IN: HIGH=TIA, LOW=SA  // its in2 is this a problem?

// Column pin lookup — maps column index 1-3 to pin number
// Usage: digitalWrite(COL_PINS[col], HIGH);
static const uint8_t COL_PINS[3] = { PIN_CC1, PIN_CC2, PIN_CC3 };

// ---------------------------------------------------------------------------
// Initializes all analog switch control pins to safe default states.
// Call once in setup() after SPI and DAC/ADC init.
//
// Safe defaults:
//   - ISPP = LOW → row bus at GND (no voltage on rows)
//   - VP = LOW → column SA at GND
//   - All COLx = LOW → columns connected to SA (GND) not TIA
//
//   * pinMode OUTPUT for all 5 pins
// ---------------------------------------------------------------------------
inline void array_gpio_init() {
    pinMode(PIN_ISPP, OUTPUT); 
    digitalWriteFast(PIN_ISPP, LOW);
    pinMode(PIN_VP, OUTPUT); 
    digitalWriteFast(PIN_VP, LOW);
    pinMode(PIN_CC1, OUTPUT); 
    digitalWriteFast(PIN_CC1, LOW);
    pinMode(PIN_CC2, OUTPUT); 
    digitalWriteFast(PIN_CC2, LOW);
    pinMode(PIN_CC3, OUTPUT); 
    digitalWriteFast(PIN_CC3, LOW);
}

// ---------------------------------------------------------------------------
// Connects one column to its TIA for reading, all others to SA for biasing.
//
// @param col  Column index 1,2, or 3
//
// ---------------------------------------------------------------------------
inline void select_column(uint8_t col) {

    for (int i = 1; i < 4; i++) {
        if (i == col) {
            digitalWriteFast(COL_PINS[i-1], HIGH);
        } else {
            digitalWriteFast(COL_PINS[i-1], LOW);
        }
    }

}

// ---------------------------------------------------------------------------
// Connects all columns to TIA simultaneously.
// Used during inference when reading all 3 outputs at once.
//
// ---------------------------------------------------------------------------
inline void select_all_columns_to_tia() {
    for (int i = 1; i < 4; i++) {
        digitalWriteFast(COL_PINS[i-1], HIGH);
    }
}

// ---------------------------------------------------------------------------
// Disconnects all columns from TIA, connects to SA (bias/GND).
// Safe state — no current flows through TIAs.
//
// ---------------------------------------------------------------------------
inline void deselect_all_columns() {
    for (int i = 1; i < 4; i++) {
        digitalWriteFast(COL_PINS[i-1], LOW);
    }
}

// ---------------------------------------------------------------------------
// Reads the conductance of a single memristor cell.
//
// @param row      Row index 1-12
// @param col      Column index 1-3
// @param v_read   Read voltage in volts (applied to selected row)
// @return         TIA output voltage (proportional to cell conductance)
//
// ---------------------------------------------------------------------------
inline float read_cell(uint8_t row, uint8_t col, float v_read, float pulse_length) {

    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f); // GND for doing read
    dac_set_voltage(AD5689_ADDR_DAC_A, v_read); 

    digitalWriteFast(PIN_VP, LOW);

    sr595_select_row(row);
    select_column(col);

    digitalWriteFast(PIN_ISPP, HIGH);
    delay(pulse_length);
    
    float read_voltage = adc_read_channel(col);

    digitalWriteFast(PIN_ISPP, LOW);

    sr595_deselect_all();
    deselect_all_columns();
    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
    dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

    delay(pulse_length);

    return read_voltage; 
}

// ---------------------------------------------------------------------------
// Applies a single write pulse to one memristor cell using half-bias scheme.
//
// @param row      Row index 1–12
// @param col      Column index 1-3
// @param v_write  Write voltage in volts (applied to selected row)
//
// ---------------------------------------------------------------------------
inline void write_cell(uint8_t row, uint8_t col, float v_write, float pulse_length) {
    dac_set_voltage(AD5689_ADDR_DAC_B, v_write / 2.0f); // give v/2 first before v due to safety reasons, (V/2 difference rather than full V difference)
    dac_set_voltage(AD5689_ADDR_DAC_A, v_write);

    digitalWriteFast(PIN_VP, HIGH); // unselected cols to botdrive

    sr595_select_row(row);
    select_column(col);

    digitalWriteFast(PIN_ISPP, HIGH);
    delay(pulse_length);

    digitalWriteFast(PIN_ISPP, LOW);

    digitalWriteFast(PIN_VP, LOW);

    sr595_deselect_all();
    deselect_all_columns();

    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
    dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

    delay(pulse_length);

}

#endif // ARRAY_OPS_H