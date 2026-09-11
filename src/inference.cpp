#include "inference.h"
#include "array_ops.h"
#include "sr595.h"
#include "integrator.h"
#include "ads1115.h"

float run_parallel_inference(const uint8_t input_levels[12], const InferenceParams& params) {

  EventInfo schedule[12];
  EventInfo offarr[12];
  
  uint8_t event_count = 0;

  float v_read = params.v_read;
  uint32_t t_unit_us = params.t_unit_us;

  uint16_t init_mask = 0b1111111111111111;

  // turn on the rows with non-zero inputs
  // fill in offarr which indicates which row has what input
  for (int i = 0; i < 12; ++i) {
    if (input_levels[i] != 0) {
      offarr[event_count].row = i;
      offarr[event_count++].off_time_us = input_levels[i] * t_unit_us; 
      init_mask = init_mask & ~((uint16_t)0x01 << i);
    }
  }

  // bubble sort, worst O(n^2) best O(n)
  // sort the offarr into ascending order
  if (event_count > 1) {
    for (uint8_t i = 0; i < event_count - 1; ++i) {
      for (uint8_t j = 0; j < event_count - 1 - i; ++j) {
        if (offarr[j].off_time_us > offarr[j + 1].off_time_us) {
          EventInfo temp = offarr[j];
          offarr[j] = offarr[j + 1];
          offarr[j + 1] = temp;
        }
      }
    }
  }

  // precompute the masks 
  // the rows with the same input value will be turned off at the same time
  // the other rows will turn off sequenctially based on their input
  int cnt = 0;
  int sched_cnt = 0;
  uint16_t current_mask = init_mask;
  while (cnt < event_count) {
    uint32_t group_time = offarr[cnt].off_time_us;
    while (cnt < event_count && offarr[cnt].off_time_us == group_time) {
      current_mask = current_mask | ((uint16_t)0x01 << (offarr[cnt++].row));
    }
    schedule[sched_cnt].off_time_us = group_time;
    schedule[sched_cnt++].masks = current_mask;
  }


  // start of inference
  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_read);
  digitalWriteFast(PIN_VP, LOW);
  //digitalWriteFast(PIN_CC1, HIGH);
  //digitalWriteFast(PIN_CC2, HIGH);
  digitalWriteFast(PIN_CC3, HIGH);
  digitalWriteFast(PIN_ISPP, HIGH);

  sr595_select_multiple_rows(init_mask);  

  // the actual logic for turning off rows depending on its input.
  cnt = 0;
  uint32_t t_start = micros();
  while(sched_cnt > 0) {
    if (micros() - t_start >= schedule[cnt].off_time_us) {
      sr595_select_multiple_rows(schedule[cnt++].masks);
      sched_cnt--;
    }
  }

  // adc read from the i2c
  // float vout1 = adc_read_channel(1);
  // delay(20);
  // float vout2 = adc_read_channel(2);
  // delay(20);
  float vout3 = adc_read_channel(3);
  delay(5);

  //Serial.print("Here is vout1:"); Serial.println(vout1);
  //Serial.print("Here is vout2:"); Serial.println(vout2);
  //Serial.print("Here is vout3:"); Serial.println(vout3);

  // for (int i = 0; i < 5; ++i) {
  //   Serial.print("here is vout1:"); Serial.println(adc_read_channel(1));
  //   delay(1000);
  // }



  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  pulse_integrator_reset(1);

  return vout3;
}


// SAME AS THE ABOVE PARALLEL INFERENCE BUT THE VERSION WHERE WE DON'T USE THE INTEGRATOR ON OUR CIRCUIT
// =========================================================================================================
InferenceResults run_parallel_inference_nointe(const uint8_t input_levels[12], const InferenceParams& params) {

  EventInfo schedule[12];
  EventInfo offarr[12];
  
  uint8_t event_count = 0;

  float v_read = params.v_read;
  uint32_t t_unit_us = params.t_unit_us;
  bool use_offset = params.use_offset;

  uint16_t init_mask = 0b1111111111111111;

  // turn on the rows with non-zero inputs
  // fill in offarr which indicates which row has what input
  for (int i = 0; i < 12; ++i) {
    if (input_levels[i] != 0) {
      offarr[event_count].row = i;
      offarr[event_count++].off_time_us = input_levels[i] * t_unit_us; 
      init_mask = init_mask & ~((uint16_t)0x01 << i);
    }
  }

  // bubble sort, worst O(n^2) best O(n)
  // sort the offarr into ascending order
  if (event_count > 1) {
    for (uint8_t i = 0; i < event_count - 1; ++i) {
      for (uint8_t j = 0; j < event_count - 1 - i; ++j) {
        if (offarr[j].off_time_us > offarr[j + 1].off_time_us) {
          EventInfo temp = offarr[j];
          offarr[j] = offarr[j + 1];
          offarr[j + 1] = temp;
        }
      }
    }
  }

  // precompute the masks 
  // the rows with the same input value will be turned off at the same time
  // the other rows will turn off sequenctially based on their input
  int cnt = 0;
  int sched_cnt = 0;
  uint16_t current_mask = init_mask;
  while (cnt < event_count) {
    uint32_t group_time = offarr[cnt].off_time_us;
    while (cnt < event_count && offarr[cnt].off_time_us == group_time) {
      current_mask = current_mask | ((uint16_t)0x01 << (offarr[cnt++].row));
    }
    schedule[sched_cnt].off_time_us = group_time;
    schedule[sched_cnt++].masks = current_mask;
  }

  float manual_sum = 0.0f;
  float manual_sum_offset = 0.0f;
  float state_voltage = 0.0f;
  float offset_voltage = 0.0f; // this is for when kernel is negative and we need to use the offset column
  uint32_t previous_time_us = 0;
  uint8_t schedule_index = 0;
  const uint32_t settle_us = 1000;


  // start of inference
  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_read);
  digitalWriteFast(PIN_VP, LOW);
  if (use_offset) {
    digitalWriteFast(PIN_CC1, HIGH);
  }
  //digitalWriteFast(PIN_CC2, HIGH);
  digitalWriteFast(PIN_CC3, HIGH);
  digitalWriteFast(PIN_ISPP, HIGH);

  sr595_select_multiple_rows(init_mask);  
  delayMicroseconds(settle_us);
  state_voltage = adc_read_channel(3);
  if (use_offset) {
    offset_voltage = adc_read_channel(1);
  }

  // the actual logic for turning off rows depending on its input.
  cnt = 0;
  uint32_t t_start = micros();

  while (schedule_index < sched_cnt) {
    uint32_t elapsed_us = micros() - t_start;

    if (elapsed_us >= schedule[schedule_index].off_time_us) {
      uint32_t delta_t_us = schedule[schedule_index].off_time_us - previous_time_us;

      // accumulate area under the current state
      manual_sum += (state_voltage) * ((float)delta_t_us);
      if (use_offset) {
        manual_sum_offset += offset_voltage * ((float)delta_t_us);
      }

      // switch to the next row mask
      sr595_select_multiple_rows(schedule[schedule_index].masks);

      previous_time_us = schedule[schedule_index].off_time_us;
      schedule_index++;

      // let analog path settle, then sample the new state
      delayMicroseconds(settle_us);
      state_voltage = adc_read_channel(3);
      if (use_offset) {
        offset_voltage = adc_read_channel(1);
      } 
    }
  }

  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  pulse_integrator_reset(1);

  InferenceResults result;
  result.manual_sum = manual_sum;
  result.manual_sum_offset = manual_sum_offset;

  return result;
}


// ================================================================================================================================================
// same general shape as above nointe but tweaked to match real array constraints
// 1. inference without going back and forth with python
// 2. Row 10 is always on, which gets subtracted to each row everytime
// 3. later might do ispp high and low immediately before and after adc readings

InferenceResults run_parallel_inference_nointe_real_array(const uint8_t input_levels[12], const InferenceParams& params) {

  EventInfo schedule[12];
  EventInfo offarr[12];
  
  uint8_t event_count = 0;

  float v_read = params.v_read;
  uint32_t t_unit_us = params.t_unit_us;
  uint8_t baseline_row = params.baseline_row;
  bool use_offset = params.use_offset;

  uint16_t init_mask = 0b1111111111111111;

  // turn on the rows with non-zero inputs
  // fill in offarr which indicates which row has what input
  for (int i = 0; i < 12; ++i) {
    if (input_levels[i] != 0) {
      offarr[event_count].row = i;
      offarr[event_count++].off_time_us = input_levels[i] * t_unit_us; 
      init_mask = init_mask & ~((uint16_t)0x01 << i);
    }
  }

  // bubble sort, worst O(n^2) best O(n)
  // sort the offarr into ascending order
  if (event_count > 1) {
    for (uint8_t i = 0; i < event_count - 1; ++i) {
      for (uint8_t j = 0; j < event_count - 1 - i; ++j) {
        if (offarr[j].off_time_us > offarr[j + 1].off_time_us) {
          EventInfo temp = offarr[j];
          offarr[j] = offarr[j + 1];
          offarr[j + 1] = temp;
        }
      }
    }
  }

  // precompute the masks 
  // the rows with the same input value will be turned off at the same time
  // the other rows will turn off sequenctially based on their input
  int cnt = 0;
  int sched_cnt = 0;
  uint16_t current_mask = init_mask;
  while (cnt < event_count) {
    uint32_t group_time = offarr[cnt].off_time_us;
    while (cnt < event_count && offarr[cnt].off_time_us == group_time) {
      current_mask = current_mask | ((uint16_t)0x01 << (offarr[cnt++].row));
    }
    schedule[sched_cnt].off_time_us = group_time;
    schedule[sched_cnt++].masks = current_mask;
  }

  int main_col = 3;
  float manual_sum = 0.0f;
  float manual_sum_offset = 0.0f;
  float state_voltage = 0.0f;
  float offset_voltage = 0.0f; // this is for when kernel is negative and we need to use the offset column
  uint32_t previous_time_us = 0;
  uint8_t schedule_index = 0;
  const uint32_t settle_us = 1000;


  // start of inference
  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_read);
  digitalWriteFast(PIN_VP, LOW);
  if (use_offset) {
    digitalWriteFast(PIN_CC2, HIGH);
  }
  //digitalWriteFast(PIN_CC1, HIGH);
  digitalWriteFast(PIN_CC3, HIGH);
  digitalWriteFast(PIN_ISPP, HIGH);

  // baseline row subtraction // row 10 usually, but row 7 subtraction for array v4 col 2.
  sr595_select_row(baseline_row);
  delayMicroseconds(settle_us);
  float baselineadc = adc_read_channel(main_col);
  sr595_deselect_all();
  // ---

  sr595_select_multiple_rows(init_mask);  
  delayMicroseconds(settle_us);
  state_voltage = adc_read_channel(main_col); 
  if (use_offset) {
    offset_voltage = adc_read_channel(1);
  }

  // the actual logic for turning off rows depending on its input.
  cnt = 0;
  uint32_t t_start = micros();

  while (schedule_index < sched_cnt) {
    uint32_t elapsed_us = micros() - t_start;

    if (elapsed_us >= schedule[schedule_index].off_time_us) {
      uint32_t delta_t_us = schedule[schedule_index].off_time_us - previous_time_us;

      // accumulate area under the current state
      // row10 subtraction
      manual_sum += (state_voltage - baselineadc) * ((float)delta_t_us);
      if (use_offset) {
        manual_sum_offset += offset_voltage * ((float)delta_t_us);
      }

      // switch to the next row mask
      sr595_select_multiple_rows(schedule[schedule_index].masks);

      previous_time_us = schedule[schedule_index].off_time_us;
      schedule_index++;

      // let analog path settle, then sample the new state
      delayMicroseconds(settle_us);
      state_voltage = adc_read_channel(main_col);
      if (use_offset) {
        offset_voltage = adc_read_channel(1);
      } 
    }
  }

  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  pulse_integrator_reset(1);

  InferenceResults result;
  result.manual_sum = manual_sum;
  result.manual_sum_offset = manual_sum_offset;

  return result;
}

// Inference for CNN image classification
// =================================================================================================================
InferenceResults run_parallel_inference_nointe_CNN(const uint8_t input_levels[12], const InferenceParams& params) {


  EventInfo schedule[12];
  EventInfo offarr[12];
  
  uint8_t event_count = 0;

  float v_read = params.v_read;
  uint32_t t_unit_us = params.t_unit_us;
  bool use_offset = params.use_offset;

  uint16_t init_mask = 0b1111111111111111;

  // turn on the rows with non-zero inputs
  // fill in offarr which indicates which row has what input
  for (int i = 0; i < 12; ++i) {
    if (input_levels[i] != 0) {
      offarr[event_count].row = i;
      offarr[event_count++].off_time_us = input_levels[i] * t_unit_us; 
      init_mask = init_mask & ~((uint16_t)0x01 << i);
    }
  }

  // bubble sort, worst O(n^2) best O(n)
  // sort the offarr into ascending order
  if (event_count > 1) {
    for (uint8_t i = 0; i < event_count - 1; ++i) {
      for (uint8_t j = 0; j < event_count - 1 - i; ++j) {
        if (offarr[j].off_time_us > offarr[j + 1].off_time_us) {
          EventInfo temp = offarr[j];
          offarr[j] = offarr[j + 1];
          offarr[j + 1] = temp;
        }
      }
    }
  }

  // precompute the masks 
  // the rows with the same input value will be turned off at the same time
  // the other rows will turn off sequenctially based on their input
  int cnt = 0;
  int sched_cnt = 0;
  uint16_t current_mask = init_mask;
  while (cnt < event_count) {
    uint32_t group_time = offarr[cnt].off_time_us;
    while (cnt < event_count && offarr[cnt].off_time_us == group_time) {
      current_mask = current_mask | ((uint16_t)0x01 << (offarr[cnt++].row));
    }
    schedule[sched_cnt].off_time_us = group_time;
    schedule[sched_cnt++].masks = current_mask;
  }

  float col_1_sum = 0.0f;
  float col_2_sum = 0.0f;
  float col_1_voltage = 0.0f;
  float col_2_voltage = 0.0f; // this is for when kernel is negative and we need to use the offset column
  uint32_t previous_time_us = 0;
  uint8_t schedule_index = 0;
  const uint32_t settle_us = 1000;


  // start of inference
  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_read);
  digitalWriteFast(PIN_VP, LOW);

  digitalWriteFast(PIN_CC1, HIGH);
  digitalWriteFast(PIN_CC2, HIGH);
  // digitalWriteFast(PIN_CC3, HIGH);
  digitalWriteFast(PIN_ISPP, HIGH);

  sr595_select_multiple_rows(init_mask);  
  delayMicroseconds(settle_us);
  col_1_voltage = adc_read_channel(1);
  col_2_voltage = adc_read_channel(2);

  // the actual logic for turning off rows depending on its input.
  cnt = 0;
  uint32_t t_start = micros();

  while (schedule_index < sched_cnt) {
    uint32_t elapsed_us = micros() - t_start;

    if (elapsed_us >= schedule[schedule_index].off_time_us) {
      uint32_t delta_t_us = schedule[schedule_index].off_time_us - previous_time_us;

      // accumulate area under the current state
      col_1_sum += (col_1_voltage) * ((float)delta_t_us);
      col_2_sum += col_2_voltage * ((float)delta_t_us);

      // switch to the next row mask
      sr595_select_multiple_rows(schedule[schedule_index].masks);

      previous_time_us = schedule[schedule_index].off_time_us;
      schedule_index++;

      // let analog path settle, then sample the new state
      delayMicroseconds(settle_us);
      col_1_voltage = adc_read_channel(1);
      col_2_voltage = adc_read_channel(2);
      // THIS CAN ACTUALLY BE A PROBLEM SINCE IF ADC READ TIME IS LONGER THAN THE VREAD PULSE LENGTH THEN TIMING CAN BE MESSY. 
      // So conservaively this should be true: t_unit_us > settle_us + adc1_us + adc2_us + mask_update_us + overhead_us
      // in order for the timing to be truly clean
    }
  }

  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  pulse_integrator_reset(1);

  InferenceResults result;
  result.manual_sum = col_1_sum;
  result.col_2_sum = col_2_sum;

  return result;
}

// Inference for CNN image classification with using only one row
// =================================================================================================================
InferenceResults run_parallel_inference_nointe_CNN_onecol(const uint8_t input_levels[12], const InferenceParams& params, uint8_t main_col) {


  EventInfo schedule[12];
  EventInfo offarr[12];
  
  uint8_t event_count = 0;

  float v_read = params.v_read;
  uint32_t t_unit_us = params.t_unit_us;
  uint8_t baseline_row = params.baseline_row;
  bool use_offset = params.use_offset;

  uint16_t init_mask = 0b1111111111111111;

  // turn on the rows with non-zero inputs
  // fill in offarr which indicates which row has what input
  for (int i = 0; i < 12; ++i) {
    if (input_levels[i] != 0) {
      offarr[event_count].row = i;
      offarr[event_count++].off_time_us = input_levels[i] * t_unit_us; 
      init_mask = init_mask & ~((uint16_t)0x01 << i);
    }
  }

  // bubble sort, worst O(n^2) best O(n)
  // sort the offarr into ascending order
  if (event_count > 1) {
    for (uint8_t i = 0; i < event_count - 1; ++i) {
      for (uint8_t j = 0; j < event_count - 1 - i; ++j) {
        if (offarr[j].off_time_us > offarr[j + 1].off_time_us) {
          EventInfo temp = offarr[j];
          offarr[j] = offarr[j + 1];
          offarr[j + 1] = temp;
        }
      }
    }
  }

  // precompute the masks 
  // the rows with the same input value will be turned off at the same time
  // the other rows will turn off sequenctially based on their input
  int cnt = 0;
  int sched_cnt = 0;
  uint16_t current_mask = init_mask;
  while (cnt < event_count) {
    uint32_t group_time = offarr[cnt].off_time_us;
    while (cnt < event_count && offarr[cnt].off_time_us == group_time) {
      current_mask = current_mask | ((uint16_t)0x01 << (offarr[cnt++].row));
    }
    schedule[sched_cnt].off_time_us = group_time;
    schedule[sched_cnt++].masks = current_mask;
  }

  float main_col_sum = 0.0f;
  float main_col_voltage = 0.0f;
  uint32_t previous_time_us = 0;
  uint8_t schedule_index = 0;
  const uint32_t settle_us = 1000;


  // start of inference
  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_read);
  digitalWriteFast(PIN_VP, LOW);

  select_column(main_col);

  digitalWriteFast(PIN_ISPP, HIGH);

  // baseline subtraction
  sr595_select_row(baseline_row);
  delayMicroseconds(settle_us);
  float baseline_voltage = adc_read_channel(main_col);
  sr595_deselect_all();

  sr595_select_multiple_rows(init_mask);  
  delayMicroseconds(settle_us);
  main_col_voltage = adc_read_channel(main_col);

  // the actual logic for turning off rows depending on its input.
  cnt = 0;
  uint32_t t_start = micros();

  while (schedule_index < sched_cnt) {
    uint32_t elapsed_us = micros() - t_start;

    if (elapsed_us >= schedule[schedule_index].off_time_us) {
      uint32_t delta_t_us = schedule[schedule_index].off_time_us - previous_time_us;

      // accumulate area under the current state
      main_col_sum += (main_col_voltage-baseline_voltage) * ((float)delta_t_us);

      // switch to the next row mask
      sr595_select_multiple_rows(schedule[schedule_index].masks);

      previous_time_us = schedule[schedule_index].off_time_us;
      schedule_index++;

      // let analog path settle, then sample the new state
      delayMicroseconds(settle_us);
      main_col_voltage = adc_read_channel(main_col);
      // THIS CAN ACTUALLY BE A PROBLEM SINCE IF ADC READ TIME IS LONGER THAN THE VREAD PULSE LENGTH THEN TIMING CAN BE MESSY. 
      // So conservatively this should be true: t_unit_us > settle_us + adc1_us + adc2_us + mask_update_us + overhead_us
      // in order for the timing to be truly clean
    }
  }

  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  pulse_integrator_reset(1);

  InferenceResults result;
  result.manual_sum = main_col_sum;
  result.col_2_sum = 0.0f;
  result.manual_sum_offset = 0.0f;

  return result;
}

// Running inference using new bit serial method where 0 - 255 greyscale pixel is represented using 8 bits and each bit is equal to one time step. 
// At every time step we read from adc and left shift by the current time step and add the 8 adc reads digitally.
InferenceResults run_parallel_inference_nointe_bitser(const uint8_t input_levels[12], const InferenceParams& params) {


  float v_read = params.v_read;
  uint32_t t_unit_us = params.t_unit_us;
  uint8_t baseline_row = params.baseline_row;
  bool use_offset = params.use_offset;

  int main_col = 3;
  int32_t  manual_sum = 0.0;
  int32_t  manual_sum_offset = 0.0f;
  int32_t  state_voltage = 0.0f;
  int32_t  offset_voltage = 0.0f; // this is for when kernel is negative and we need to use the offset column
  const uint32_t settle_us = 1000;
  
  uint16_t init_mask = 0b1111111111111111;  
  int64_t  final_accumulation = 0;


  // start of inference
  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_read);
  digitalWriteFast(PIN_VP, LOW);
  if (use_offset) {
    digitalWriteFast(PIN_CC2, HIGH);
  }
  //digitalWriteFast(PIN_CC1, HIGH);
  digitalWriteFast(PIN_CC3, HIGH);
  digitalWriteFast(PIN_ISPP, HIGH);

  // row 7 subtraction // row 10 usually, but row 7 subtraction for array v4 col 2.
  sr595_select_row(baseline_row);
  delayMicroseconds(settle_us);
  int32_t baselineadc = (int32_t)adc_read_raw(main_col);
  //float row10adc = 0;
  sr595_deselect_all();
  // ---

  for (int bits = 0; bits < 8; ++bits) { // number of bits in MAX LEVEL of the greyscale
    bool any_active = false;
    for (int rows = 0; rows < 12; ++rows) { // number of rows
      if ((input_levels[rows] >> bits) & 1) {
        init_mask = init_mask & ~((uint16_t)0x01 << rows);
        any_active = true;
      }
    }
    if (!any_active) {
      continue;
    }
    sr595_select_multiple_rows(init_mask);  
    delayMicroseconds(t_unit_us);
    state_voltage = (int32_t)adc_read_raw(main_col); 
    if (use_offset) {
      offset_voltage = adc_read_raw(1);
    }

    manual_sum = (state_voltage - baselineadc);
    final_accumulation += (int64_t)manual_sum * (1LL << bits); // this is multiplying manual sum * 1, 2, 4, 8, 16,... same as bit shifting but in case manual sum is negative.
    sr595_deselect_all();
    init_mask = 0b1111111111111111; 
  }

  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  pulse_integrator_reset(1);

  InferenceResults result;
  result.manual_sum = (float)final_accumulation * ADS1115_DEFAULT_FSR_VOLTS / 32767.0f;
  result.manual_sum_offset = manual_sum_offset;

  return result;
}

