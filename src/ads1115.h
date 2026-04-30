#ifndef ADS1115_H
#define ADS1115_H

#include <Arduino.h>
#include <Wire.h>

// ADS1115 register map
#define ADS1115_REG_CONVERSION 0x00
#define ADS1115_REG_CONFIG     0x01
#define ADS1115_REG_LO_THRESH  0x02
#define ADS1115_REG_HI_THRESH  0x03

// Config register bits
#define ADS1115_OS_SINGLE            0x8000

#define ADS1115_MUX_DIFF_0_1         0x0000
#define ADS1115_MUX_DIFF_0_3         0x1000
#define ADS1115_MUX_DIFF_1_3         0x2000
#define ADS1115_MUX_DIFF_2_3         0x3000
#define ADS1115_MUX_SINGLE_0         0x4000
#define ADS1115_MUX_SINGLE_1         0x5000
#define ADS1115_MUX_SINGLE_2         0x6000
#define ADS1115_MUX_SINGLE_3         0x7000

#define ADS1115_PGA_6_144V           0x0000
#define ADS1115_PGA_4_096V           0x0200
#define ADS1115_PGA_2_048V           0x0400
#define ADS1115_PGA_1_024V           0x0600
#define ADS1115_PGA_0_512V           0x0800
#define ADS1115_PGA_0_256V           0x0A00

#define ADS1115_MODE_CONTINUOUS      0x0000
#define ADS1115_MODE_SINGLE_SHOT     0x0100

#define ADS1115_DR_8SPS              0x0000
#define ADS1115_DR_16SPS             0x0020
#define ADS1115_DR_32SPS             0x0040
#define ADS1115_DR_64SPS             0x0060
#define ADS1115_DR_128SPS            0x0080
#define ADS1115_DR_250SPS            0x00A0
#define ADS1115_DR_475SPS            0x00C0
#define ADS1115_DR_860SPS            0x00E0

#define ADS1115_COMP_MODE_TRAD       0x0000
#define ADS1115_COMP_POL_ACTIVE_LOW  0x0000
#define ADS1115_COMP_LAT_NONLATCH    0x0000
#define ADS1115_COMP_QUE_DISABLE     0x0003

// Default measurement settings
static constexpr uint16_t ADS1115_DEFAULT_PGA = ADS1115_PGA_4_096V  ;
static constexpr float ADS1115_DEFAULT_FSR_VOLTS = 4.096f;
static constexpr uint16_t ADS1115_DEFAULT_DR = ADS1115_DR_860SPS;

inline bool ads1115_write_register(TwoWire &bus, uint8_t i2c_addr, uint8_t reg, uint16_t value) {
  bus.beginTransmission(i2c_addr);
  bus.write(reg);
  bus.write((uint8_t)(value >> 8));
  bus.write((uint8_t)(value & 0xFF));
  return bus.endTransmission() == 0;
}

inline bool ads1115_read_register(TwoWire &bus, uint8_t i2c_addr, uint8_t reg, uint16_t &value) {
  bus.beginTransmission(i2c_addr);
  bus.write(reg);

  if (bus.endTransmission(false) != 0) {
    return false;
  }

  if (bus.requestFrom((int)i2c_addr, 2) != 2) {
    return false;
  }

  value = ((uint16_t)bus.read() << 8) | (uint16_t)bus.read();
  return true;
}

inline uint16_t ads1115_mux_from_single_ended_channel(uint8_t ain) {
  switch (ain) {
    case 0: return ADS1115_MUX_SINGLE_0;
    case 1: return ADS1115_MUX_SINGLE_1;
    case 2: return ADS1115_MUX_SINGLE_2;
    case 3: return ADS1115_MUX_SINGLE_3;
    default: return ADS1115_MUX_SINGLE_0;
  }
}

inline uint16_t ads1115_build_single_ended_config(uint8_t ain) {
  return ADS1115_OS_SINGLE
       | ads1115_mux_from_single_ended_channel(ain)
       | ADS1115_DEFAULT_PGA
       | ADS1115_MODE_SINGLE_SHOT
       | ADS1115_DEFAULT_DR
       | ADS1115_COMP_MODE_TRAD
       | ADS1115_COMP_POL_ACTIVE_LOW
       | ADS1115_COMP_LAT_NONLATCH
       | ADS1115_COMP_QUE_DISABLE;
}

inline bool ads1115_start_single_ended_conversion(TwoWire &bus, uint8_t i2c_addr, uint8_t ain) {
  uint16_t cfg = ads1115_build_single_ended_config(ain);
  return ads1115_write_register(bus, i2c_addr, ADS1115_REG_CONFIG, cfg);
}

inline bool ads1115_conversion_ready(TwoWire &bus, uint8_t i2c_addr) {
  uint16_t cfg = 0;

  if (!ads1115_read_register(bus, i2c_addr, ADS1115_REG_CONFIG, cfg)) {
    return false;
  }

  return (cfg & ADS1115_OS_SINGLE) != 0;
}

inline bool ads1115_read_conversion_raw(TwoWire &bus, uint8_t i2c_addr, int16_t &raw) {
  uint16_t reg_value = 0;

  if (!ads1115_read_register(bus, i2c_addr, ADS1115_REG_CONVERSION, reg_value)) {
    return false;
  }

  raw = (int16_t)reg_value;
  return true;
}

inline float ads1115_counts_to_volts(int16_t raw) {
  return ((float)raw * ADS1115_DEFAULT_FSR_VOLTS) / 32767.0f;
}

inline float ads1115_read_single_ended_voltage(TwoWire &bus, uint8_t i2c_addr, uint8_t ain) {
  if (!ads1115_start_single_ended_conversion(bus, i2c_addr, ain)) {
    return NAN;
  }

  const uint32_t t_start_ms = millis();
  while (!ads1115_conversion_ready(bus, i2c_addr)) {
    if (millis() - t_start_ms > 10) {
      return NAN;
    }
    delayMicroseconds(50);
  }

  int16_t raw = 0;
  if (!ads1115_read_conversion_raw(bus, i2c_addr, raw)) {
    return NAN;
  }

  return ads1115_counts_to_volts(raw);
}

#endif // ADS1115_H