#include "inference.h"
#include "array_ops.h"
#include "sr595.h"
#include "integrator.h"

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


float run_parallel_inference_nointe(const uint8_t input_levels[12], const InferenceParams& params) {

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

  float manual_sum = 0.0f;
  float state_voltage = 0.0f;
  uint32_t previous_time_us = 0;
  uint8_t schedule_index = 0;
  const uint32_t settle_us = 1000;


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
  delayMicroseconds(settle_us);
  state_voltage = adc_read_channel(3);

  // the actual logic for turning off rows depending on its input.
  cnt = 0;
  uint32_t t_start = micros();

  while (schedule_index < sched_cnt) {
    uint32_t elapsed_us = micros() - t_start;

    if (elapsed_us >= schedule[schedule_index].off_time_us) {
      uint32_t delta_t_us = schedule[schedule_index].off_time_us - previous_time_us;

      // accumulate area under the current state
      manual_sum += state_voltage * ((float)delta_t_us);

      // switch to the next row mask
      sr595_select_multiple_rows(schedule[schedule_index].masks);

      previous_time_us = schedule[schedule_index].off_time_us;
      schedule_index++;

      // let analog path settle, then sample the new state
      delayMicroseconds(settle_us);
      state_voltage = adc_read_channel(3);
    }
  }

  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  pulse_integrator_reset(1);

  return manual_sum;
}

