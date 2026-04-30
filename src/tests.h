#ifndef TESTS_H
#define TESTS_H

#include <Arduino.h>

enum TestId {

  TEST_SAFE_BOOT = 1,
  TEST_DAC_A_STATIC,
  TEST_DAC_B_STATIC,
  TEST_DUAL_DAC,
  TEST_ISPP_GATE,
  TEST_VP_GATE,
  TEST_SHIFTREG_MAPPING,
  TEST_COLUMN_SWITCH,
  TEST_ROW_SWITCH,
  TEST_SPI1_COHABITATION,
  TEST_WRITE_WAVEFORM,
  // 
  TEST_RESET_PULSE,
  TEST_ADC_BASELINE,
  TEST_TIA_RESPONSE,
  TEST_CSA_HOLD,
  TEST_RESET_REPEATABILITY,
  TEST_CSA_ACCUMULATION,
  TEST_READ_CELL_SANITY,
  //
  TEST_INCR_ISPP_PULSE,
  TEST_ISPP_WAVEFORM,

  // 
  TEST_TIA_READ_TOTAL_CURRENT,

  //
  TEST_ADC_READOUT,

  //
  TEST_MNIST,
  TEST_SANITY_SUITE,

  //placeholder for testid size
  TEST_END

};

void print_test_menu();
void run_test(uint8_t test_id);

#endif 