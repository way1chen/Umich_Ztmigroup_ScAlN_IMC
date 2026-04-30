#include "ispp.h"
#include "array_ops.h"


// sanity check for read protocol for ispp
float read_verify_cell(uint8_t row, uint8_t col, float v_read, float pulse_length) {

  if ((row < 1 || row > 12) || (col < 1 || col > 3) || (v_read <= 0.0f) || (pulse_length < 0.0f)) {
    return 0.0f;
  }
  return read_cell(row, col, v_read, pulse_length);
}

// sanity check for write protocol for ispp
void write_cell_once(uint8_t row, uint8_t col, float v_write, float pulse_length) {

  if ((row < 1 || row > 12) || (col < 1 || col > 3) || (v_write <= 0.0f) || (pulse_length < 0.0f)) {
    return;
  }

  write_cell(row, col, v_write, pulse_length);

}

// check whether the weight is within tolerance of our target during write
bool is_within_tolerance(float measured, float target, float tolerance) {
  if (fabsf(measured - target) < tolerance) {
    return true;
  }
  return false;
}

// Running a single ispp sequence for one weight
IsppResult run_ispp_cell(uint8_t row, uint8_t col, float target, const IsppParams& params) {
  IsppResult results = {};
  results.target = target;
  results.final_readback = 0.0f;
  results.last_write_voltage = 0.0f;
  results.cycles_used = 0;
  results.success = false;

  float v_write = params.v_start;
  float v_read = params.v_read;
  float tolerance = params.tolerance;
  float v_step = params.v_step;
  float v_max = params.v_max;
  float pulse_length = params.pulse_length;
  uint8_t max_pulses = params.max_pulses;

  // define how to want to log / print progress
  for (uint8_t cycle = 0; cycle < max_pulses; cycle++) {

    results.final_readback = read_verify_cell(row, col, v_read, pulse_length);

    if (is_within_tolerance(results.final_readback, results.target, tolerance)) {
      results.success = true;
      break;
    }

    if (v_write > v_max) {
      results.success = false;
      break;
    }

    write_cell_once(row,col,v_write, pulse_length);

    results.last_write_voltage = v_write;
    v_write = v_write + v_step;
    results.cycles_used++;
  }
  
  return results;
}

void run_ispp_matrix(const float targets[12][3], const IsppParams& params) {
  // TODO:
  // iterate over rows and columns
  // run one-cell ISPP on each target
  // decide how I want to report results

  


}
