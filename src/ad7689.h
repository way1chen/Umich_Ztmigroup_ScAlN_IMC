#ifndef AD7689_H
#define AD7689_H

#include <Arduino.h>
#include <SPI.h>

/**
 * =====================================NOT IN USE RIGHT NOW==========================================================
 * AD7689 — 16-Bit 8-Channel SAR ADC Driver
 * ==========================================
 *
 * --- One-Deep Pipeline ---
 * AD7689 uses a fully-pipelined architecture:
 *   - When you send a configuration frame, the ADC starts a NEW conversion
 *     based on that config.
 *   - The data clocked BACK to you during that same transfer is the result
 *     of the PREVIOUS conversion — not the one you just requested.
 *
 * To get a fresh reading of channel X you always need TWO transfers minimum:
 *   1. Transfer 1 — send config for channel X, discard the returned data
 *   2. Wait ~5us for conversion to complete (tCONV max = 3.3us)
 *   3. Transfer 2 — send anything (same config is fine), read back channel X result
 *
 * This is handled automatically by adc_read_channel() in main.ino. 
 * In most cases, do NOT call ad7689_transfer() directly
 */

// ---------------------------------------------------------------------------
// 14-Bit Configuration Register (CFG) Bit Definitions 
// This is what the teensy sends to ADC through MOSI
// (Datasheet Table 12/13 (page 28))
//
// The CFG word is 14 bits wide. It is left-shifted by 2 before sending
// so it occupies bits [15:2] of the 16-bit SPI frame.
// ---------------------------------------------------------------------------

// Bit [13] — CFG Update flag
// Must be set to 1 for the ADC to accept and apply the new configuration (overwrites).
// If 0, the ADC ignores the incoming config and keeps the previous settings.
#define AD7689_CFG_UPDATE        (1u << 13)

// Bits [12:10] — Input Channel Configuration (INCC)
// Selects the input mode. For single-ended signals referenced to GND (typical
// for TIA outputs in this system), use AD7689_INCC_UNIPOLAR_GND.
#define AD7689_INCC_BIPOLAR_DIFF  (0x0u << 10) // Bipolar Differential pairs, INx referenced to VREF/2 +/-0.1V
#define AD7689_INCC_BIPOLAR_COM   (0x2u << 10) // Bipolar; INx referenced to COM = VREF/2 ± 0.1 V.
#define AD7689_INCC_TEMP_SENSOR   (0x3u << 10) // Internal temperature sensor mode
#define AD7689_INCC_UNIPOLAR_DIF  (0x4u << 10) // Unipolar differential pairs; INx referenced to GND ± 0.1 V.
#define AD7689_INCC_UNIPOLAR_COM  (0x6u << 10) // Unipolar, INx referenced to COM = GND ± 0.1 V.
#define AD7689_INCC_UNIPOLAR_GND  (0x7u << 10) // Unipolar, INx referenced to GND — use this for TIA readout

// Bits [9:7] — Input Channel Select (INx)
// Selects which of the 8 input channels (IN0–IN7) to convert.
// The VOUTs from the opamp
// you choose the IN from 0 to 7 which gets converted to 16bit and masked with 0000 0111 and shift 7 bits to the left
// Usage: AD7689_CH(0) through AD7689_CH(7)
#define AD7689_CH(x)              (((uint16_t)(x) & 0x07u) << 7)

// Bit [6] — Anti-Aliasing Filter Bandwidth (BW)
// Full bandwidth (1.7 MHz) gives fastest response.
// Quarter bandwidth (425 kHz) reduces noise but slows down the input filter.
// For memristor readout at moderate speeds, either is fine.
#define AD7689_BW_FULL            (1u << 6)  // Full bandwidth  — 1.7 MHz
#define AD7689_BW_QUARTER         (0u << 6)  // Quarter bandwidth — 425 kHz, lower noise

// Bits [5:3] — Reference / Buffer Selection (REF)
// Determines the voltage reference used for the ADC conversion.
// Maybe ignore temperature for now
#define AD7689_REF_INT_25V                 (0x0u << 3) // Internal 2.5V reference, temperature sensor on
#define AD7689_REF_INT_4096V               (0x1u << 3) // Internal 4.096V reference, temperature sensor on
#define AD7689_REF_EXT_TEMP1_BUFF0         (0x2u << 3) // Use external reference, temperature sensor enabled and internal buffer disabled.
#define AD7689_REF_EXT_TEMP0_BUFF0         (0x3u << 3) // Use External reference with internal input buffer enabled and temperature enabled
#define AD7689_REF_EXT_INT0_TEMP0_BUFF0    (0x6u << 3) // Use external reference with internal reference, internal buffer, and temperature disabled
#define AD7689_REF_EXT_INT0_TEMP0_BUFF1    (0x7u << 3) // Use external reference with internal buffer, temperature sensor and internal reference disabled

// Bits [2:1] — Channel Sequencer Control (SEQ)
// The sequencer can automatically cycle through channels without reprogramming.
// For manual per-channel control (our approach), disable it.
// Might need later for fast CNN readings
#define AD7689_SEQ_DISABLE         (0x0u << 1) // No sequencing — channel set manually each transfer
#define AD7689_SEQ_UPDATE_CONFIG   (0x1u << 1) //  Update configuration during sequence
#define AD7689_SEQ_SCAN_INx        (0x2u << 1) // Scan IN0 to IN[7:0] (set in CFG[9:7]), then temperature
#define AD7689_SEQ_SCAN_INx_NOTEMP (0x3u << 1) // Scan IN0 to IN[7:0] (set in CFG[9:7])

// Bit [0] — Configuration Readback (RB)
// When enabled, the ADC echoes its current config word back to the host
// after each conversion. Useful for debugging but wastes bandwidth.
// Essentially reads back to the CFG register
#define AD7689_RB_ENABLE          (0u << 0)  // Echo config back after each conversion
#define AD7689_RB_DISABLE         (1u << 0)  // No readback — normal operation

// ---------------------------------------------------------------------------
// ad7689_init()
//
// Initialises the AD7689 and flushes the conversion pipeline.
//
// The ADC requires at least 2 dummy conversions after
// power-on before the configuration register is valid and data is reliable.
// This function performs those 2 dummy transfers.
//
// Call this once in setup() before any calls to ad7689_transfer().
//
// @param bus           SPI bus instance (e.g. SPI on Teensy)
// @param cs            Chip select pin number
// @param settings      SPISettings object (clock, bit order, mode)
// @param initialConfig The CFG word to load — build it using the defines above
// ---------------------------------------------------------------------------
inline void ad7689_init(SPIClass &bus, int cs, SPISettings &settings, uint16_t initialConfig) {
    pinMode(cs, OUTPUT);
    digitalWrite(cs, HIGH);  // Ensure CS starts deasserted

    // The 14-bit CFG word must be left-shifted by 2 to occupy bits [15:2]
    // of the 16-bit SPI frame. Bits [1:0] are don't-care.
    uint16_t frame = initialConfig << 2;

    // Send 2 dummy frames to flush the pipeline and lock in the configuration
    for (int i = 0; i < 2; i++) {
        bus.beginTransaction(settings);
        digitalWriteFast(cs, LOW);
        bus.transfer16(frame);
        digitalWriteFast(cs, HIGH);
        bus.endTransaction();
        delayMicroseconds(5);  // Wait for conversion to finish (tCONV max = 3.3us, 5us gives safe margin)
    }
}

// ---------------------------------------------------------------------------
// ad7689_transfer()
//
// Performs one SPI frame exchange with the AD7689.
//
// This is the core low-level function. Due to the one-deep pipeline:
//   - The config you send HERE determines what channel converts NEXT time.
//   - The value returned HERE is the result of the PREVIOUS conversion.
//
// For a correct single-channel read, always call this twice:
//   uint16_t stale = ad7689_transfer(..., cfg);   // queue channel, discard
//   delayMicroseconds(5);
//   uint16_t fresh = ad7689_transfer(..., cfg);   // collect the real result
//
// This is wrapped cleanly in adc_read_channel() in main.ino — prefer that
// function over calling ad7689_transfer() directly.
//
// @param bus       SPI bus instance
// @param cs        Chip select pin number
// @param settings  SPISettings object
// @param config    14-bit CFG word (NOT pre-shifted — this function shifts it)
// @return          16-bit raw ADC result from the PREVIOUS conversion
// ---------------------------------------------------------------------------
inline uint16_t ad7689_transfer(SPIClass &bus, int cs, SPISettings &settings, uint16_t config) {
    uint16_t result;

    bus.beginTransaction(settings);
    digitalWriteFast(cs, LOW);

    // Full-duplex exchange:
    //   Outgoing: config shifted left by 2 to align CFG[13:0] into frame bits [15:2]
    //   Incoming: 16-bit conversion result from the previous sample

    result = bus.transfer16(config << 2);

    digitalWriteFast(cs, HIGH);
    bus.endTransaction();

    // NOTE: No delay here — the caller is responsible for waiting tCONV
    // before calling again to retrieve the result. See adc_read_channel()
    // in main.ino for the correct usage pattern.

    return result;
}

#endif // AD7689_H
