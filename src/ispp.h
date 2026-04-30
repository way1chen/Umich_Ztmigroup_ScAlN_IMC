#ifndef ISPP_H
#define ISPP_H

#include <Arduino.h>

struct IsppParams {
  float v_read;
  float v_start;
  float v_step;
  float v_max;
  float tolerance;
  float pulse_length;
  uint8_t max_pulses;

};

struct IsppResult {
  float final_readback;
  float target;
  float last_write_voltage;
  uint8_t cycles_used;
  bool success;
};

float read_verify_cell(uint8_t row, uint8_t col, float v_read, float pulse_length);
void write_cell_once(uint8_t row, uint8_t col, float v_write, float pulse_length);
bool is_within_tolerance(float measured, float target, float tolerance);

// return type is isppresult struct
// isppparam& takes a reference of that struct instead of creating a whole new copy
IsppResult run_ispp_cell(uint8_t row, uint8_t col, float target, const IsppParams& params);
void run_ispp_matrix(const float targets[12][3], const IsppParams& params);

#endif
