#ifndef ANALOG_IO_H
#define ANALOG_IO_H


// ----------------------------------------------------
// different analog operations

#include <Arduino.h>
#include <SPI.h>
#include "ad5689.h"
//#include "ad7689.h"

// --------------------------------------------------------------------------------------------------------------------
#include <Wire.h>
#include "ads1115.h"

#define ADS1115_I2C_ADDR 0x48
#define ADC_CHANNEL_0_AIN 0
#define ADC_CHANNEL_1_AIN 1
#define ADC_CHANNEL_2_AIN 2
#define ADC_CHANNEL_3_AIN 3
// ---------------------------------------------------------------------------------------------------------------------


// SPI for ADC and SPI1 for DAC and 
// only one should be low at a time
#define PIN_CS_DAC 38  
#define PIN_CS_ADC 10 

// --- VOLTAGE / REFERENCE CONSTANTS ---
// ============================================================

#define DAC_VREF 2.5f        // Reference voltage in volts
#define DAC_FULLSCALE 65535  // 16-bit DAC max counts (2^16 - 1)
#define ADC_VREF 4.096f
#define ADC_FULLSCALE 65535  // 16-bit ADC max counts


// --- SPI SETTINGS FOR AD7689 ADC ---
// ============================================================
// SPI_MODE0: CPOL=0, CPHA=0 (data captured on rising edge)
static SPISettings adcSettings(1000000, MSBFIRST, SPI_MODE0); 


// --- AD7689 INITIAL CONFIG WORD ---
// ============================================================
// The specific information for the stream is in ad7689.h

// Note: We will override CH(x) in the read function per-channel.
// Thus, bits [9:7] are left empty right now for later
#define ADC_BASE_CFG (AD7689_CFG_UPDATE \
                      | AD7689_INCC_UNIPOLAR_GND \
                      | AD7689_BW_FULL \
                      | AD7689_REF_INT_4096V \
                      | AD7689_SEQ_DISABLE \
                      | AD7689_RB_DISABLE)


// --- Set DAC voltage (0.0 to DAC_VREF volts) ---
// ============================================================
/**
 * Sets one DAC channel to a target voltage. (VOUT on DAC)
 * I tell the DAC the voltage I want, so I need to convert it into bits so it can understand. 
 * @param channel  Use AD5689_ADDR_DAC_A or AD5689_ADDR_DAC_B
 * @param voltage  Desired output in volts (clamped to 0 ~ DAC_VREF)
 */
inline void dac_set_voltage(uint8_t channel, float voltage) {
  // Clamp to valid range of 0.0 to the reference voltage
  if (voltage < 0.0f) voltage = 0.0f;
  if (voltage > DAC_VREF) voltage = DAC_VREF;

  // Convert volts → 16-bit counts
  uint16_t counts = (uint16_t)((voltage / DAC_VREF) * (float)DAC_FULLSCALE); // maybe roundf?

  // Write and immediately update the DAC output
  ad5689_write(SPI1, PIN_CS_DAC, AD5689_CMD_WRITE_UPDATE, channel, counts);
}

// --- Read one ADC channel (handles pipeline delay) ---
// ============================================================
/**
 * Reads a single ADC channel and returns the voltage.
 *
 * @param channel  ADC channel number IN0->input 1, IN1->2, IN2->3
 * @return         Measured voltage in volts
 */
// inline float adc_read_channel(uint8_t channel) {
//   // Build config word for the desired channel (VOUT)
//   uint16_t cfg = ADC_BASE_CFG | AD7689_CH(channel-1);

//   // 1st transfer: queue this channel conversion, discard old result
//   ad7689_transfer(SPI, PIN_CS_ADC, adcSettings, cfg);
//   delayMicroseconds(20);  // wait for conversion to complete (~3.3us max)

//   // 2nd transfer: send NOP (keep same config), read back the fresh result
//   // this is because of the one deep pipeline
//   uint16_t raw = ad7689_transfer(SPI, PIN_CS_ADC, adcSettings, cfg);
//   delayMicroseconds(20);

//   Serial.print("  raw="); Serial.println(raw);

//   // Convert counts → volts
//   return ((float)raw / (float)ADC_FULLSCALE) * ADC_VREF;
// }

// Code for ads1115 that using I2C protocol. 
// -----------------------------------------------------------------------------------------------------------------------------------
inline bool adc_init() {
  uint16_t cfg = 0;
  
  for (int attempt = 0; attempt < 20; attempt++) {
    if (ads1115_read_register(Wire, ADS1115_I2C_ADDR, ADS1115_REG_CONFIG, cfg)) {
      return true;
    }
    delay(15);
  }

  return false;
}

inline float adc_read_channel(uint8_t channel) {

  int8_t ain = 0;
  switch (channel) {
  case 1:
    ain = ADC_CHANNEL_0_AIN;
    break;
  case 2:
    ain = ADC_CHANNEL_1_AIN;
    break;
  case 3:
    ain = ADC_CHANNEL_2_AIN;
    break;
  case 4:
    ain = ADC_CHANNEL_3_AIN;
    break;
  default:
    Serial.print("ERROR: invalid ADC channel ");
    Serial.println(channel);
    return NAN;
  }


  float voltage = ads1115_read_single_ended_voltage(Wire, ADS1115_I2C_ADDR, (uint8_t)ain);

  if (isnan(voltage)) {
    Serial.print("ERROR: ADS1115 read failed on channel ");
    Serial.println(channel);
  }

  return voltage;
}
// -----------------------------------------------------------------------------------------------------------------------------------

#endif //ANALOG_IO_H