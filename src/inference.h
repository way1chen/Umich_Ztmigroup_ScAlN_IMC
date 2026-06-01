#ifndef INFERENCE_H
#define INFERENCE_H

#include <Arduino.h>

struct EventInfo {
  uint8_t row;
  uint16_t masks;
  uint32_t off_time_us;
  
};

struct InferenceParams {
  float v_read;
  uint32_t t_unit_us;
  uint8_t max_scale; // the downsampled range from 0-255 -> 0-max_scale
  bool use_offset;
};

struct InferenceResults {
  float manual_sum;
  float col_2_sum;
  float manual_sum_offset;
};

float run_parallel_inference(const uint8_t input_levels[12], const InferenceParams& params);
InferenceResults run_parallel_inference_nointe(const uint8_t input_levels[12], const InferenceParams& params);
InferenceResults run_parallel_inference_nointe_real_array(const uint8_t input_levels[12], const InferenceParams& params);
InferenceResults run_parallel_inference_nointe_CNN(const uint8_t input_levels[12], const InferenceParams& params);


#endif 