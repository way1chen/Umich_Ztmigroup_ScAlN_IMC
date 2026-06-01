#include "tests.h"
#include "ad5689.h"
#include "ad7689.h"
#include "analog_io.h"
#include "array_ops.h"
#include "ispp.h"
#include "integrator.h"
#include "inference.h"

void test_safe_boot();
void test_dac_a_static();
void test_dac_b_static();
void test_dual_dac();
void test_ispp_gate();
void test_vp_gate();
void test_shiftreg_mapping();
void test_column_switch();
void test_row_switch();
void test_spi1_cohabitation();
void test_write_waveform();

void test_reset_pulse();
void test_adc_baseline();
void test_tia_response();
void test_csa_hold();
void test_reset_repeatability();
void test_csa_accumulation();
void test_read_cell_sanity();

void test_incr_ispp_pulse();
void test_ispp_waveform();

void test_tia_read_total_current();

void test_adc_readout();
void test_col_leakage();

void test_mnist();

void test_conductance_sweep();
void test_full_sweep();
void test_run_ispp();
void test_ivsweep_erase();
void test_pwm_drift();
void test_two_row_current();
void test_tworows();
void test_cleanrows();

void test_set_weights();

void print_test_menu() {
  Serial.println();
  Serial.println("=== TEST MENU ===");
  Serial.println("1  - Safe boot / enable-state");
  Serial.println("2  - DAC A static output");
  Serial.println("3  - DAC B static output");
  Serial.println("4  - Dual-DAC independence");
  Serial.println("5  - ISPP gate path");
  Serial.println("6  - VP gate path");
  Serial.println("7  - Driven shift register mapping sweep");
  Serial.println("8  - Column switch");
  Serial.println("9 - Row switch");
  Serial.println("10 - SPI1 DAC + shift register coexistence");
  Serial.println("11 - write_cell waveform on dummy load");
  Serial.println("----------------------------------------------");
  Serial.println("12 - Integrator reset pulse");
  Serial.println("13 - ADC baseline after reset");
  Serial.println("14 - TIA response sanity");
  Serial.println("15 - CSA hold test");
  Serial.println("16 - Reset repeatability");
  Serial.println("17 - CSA accumulation");
  Serial.println("18 - read_cell sanity");
  Serial.println("----------------------------------------------");
  Serial.println("19 - simple incrementing of ispp v write pulse");
  Serial.println("20 - show the full ispp waveform");
  Serial.println("----------------------------------------------");
  Serial.println("21 - show the total current decreasing in the tia for reading inference");
  Serial.println("----------------------------------------------");
  Serial.println("22 - testing adc readout");
  Serial.println("23 - testing whether turning on multiple cols affect each other's calculations");
  Serial.println("----------------------------------------------");
  Serial.println("24 - test simple 20x20 mnist image processing convolution");
  Serial.println("----------------------------------------------");
  Serial.println("25 - doing a conductance sweep on the real array to see the initial conductances.");
  Serial.println("26 - doing a full conductance sweep on all cells");
  Serial.println("27 - running full ispp on a single cell");
  Serial.println("28 - do an iv sweep to erase/reset the conductnace of a cell");
  Serial.println("29 - PWM drift test on the same conductance level");
  Serial.println("30 - Test inputting into two rows of eqaully programmed cells and getting double the current");
  Serial.println("31 - Test rows 12 and 2 current");
  Serial.println("32 - codex assisted clean row test");
  Serial.println("33 - set the weights on the ScAlN array for mnist testing");


  Serial.println("Type -pymenu- to see python side menu");
  Serial.println();
}

void run_test(uint8_t test_id) {
  switch (test_id) {
    case TEST_SAFE_BOOT:
      test_safe_boot();
      break;
    case TEST_DAC_A_STATIC:
      test_dac_a_static();
      break;
    case TEST_DAC_B_STATIC:
      test_dac_b_static();
      break;
    case TEST_DUAL_DAC:
      test_dual_dac();
      break;
    case TEST_ISPP_GATE:
      test_ispp_gate();
      break;
    case TEST_VP_GATE:
      test_vp_gate();
      break;
    case TEST_SHIFTREG_MAPPING:
      test_shiftreg_mapping();
      break;
    case TEST_COLUMN_SWITCH:
      test_column_switch();
      break;
    case TEST_ROW_SWITCH:
      test_row_switch();
      break;
    case TEST_SPI1_COHABITATION:
      test_spi1_cohabitation();
      break;
    case TEST_WRITE_WAVEFORM:
      test_write_waveform();
      break;

    case TEST_RESET_PULSE:
      test_reset_pulse();
      break;
    case TEST_ADC_BASELINE:
      test_adc_baseline();
      break;
    case TEST_TIA_RESPONSE:
      test_tia_response();
      break;
    case TEST_CSA_HOLD:
      test_csa_hold();
      break;
    case TEST_RESET_REPEATABILITY:
      test_reset_repeatability();
      break;
    case TEST_CSA_ACCUMULATION:
      test_csa_accumulation();
      break;
    case TEST_READ_CELL_SANITY:
      test_read_cell_sanity();
      break;

    case TEST_INCR_ISPP_PULSE:
      test_incr_ispp_pulse();
      break;
    case TEST_ISPP_WAVEFORM:
      test_ispp_waveform();
      break;

    case TEST_TIA_READ_TOTAL_CURRENT:
      test_tia_read_total_current();
      break;

    case TEST_ADC_READOUT:
      test_adc_readout();
      break;
    case TEST_COL_LEAKAGE:
      test_col_leakage();
      break;

    case TEST_MNIST:
      test_mnist();
      break;

    case TEST_CONDUCTANCE_SWEEP:
      test_conductance_sweep();
      break;
    case TEST_FULL_SWEEP:
      test_full_sweep();
      break;
    case TEST_RUN_ISPP:
      test_run_ispp();
      break;
    case TEST_IVSWEEP_ERASE:
      test_ivsweep_erase();
      break;
    case TEST_PWM_DRIFT:
      test_pwm_drift();
      break;
    case TEST_TWO_ROW_CURRENT:
      test_two_row_current();
      break;
    case TEST_TWOROWS:
      test_tworows();
      break;
    case TEST_CLEANROWS:
      test_cleanrows();
      break;
    
    case TEST_SET_WEIGHTS:
      test_set_weights();
      break;
    default:
      Serial.println("Invalid test selection.");
      break;
  }
}

void test_safe_boot() {
  // Safe-state check after enable.
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);

  sr595_deselect_all();

  Serial.println("Safe boot / safe state asserted.");
  Serial.println("Expected:");
  Serial.println("  TOP_DRIVE = 0 V");
  Serial.println("  BOT_DRIVE = 0 V");
  Serial.println("  ISPP = LOW");
  Serial.println("  VP = LOW");
  Serial.println("  CC1/CC2/CC3 = LOW");
  Serial.println("  all rows deselected");
  Serial.println("Probe critical nodes and confirm no unintended bias is present.");
  Serial.println("End of test");
}

void test_dac_a_static() {
  // Static DAC A / TOP_DRIVE check.
  // DAC has GAIN HIGH, which does x2 to voltage
  bool testing = false;
  float DACAvoltage = 0.0f;

  Serial.println("Type the voltage you want DAC A to output under 0.125V.");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      if (input.toFloat() > 0.125) {
        Serial.println("Too high of a voltage, try again.");
      } else {
        DACAvoltage = input.toFloat();
        testing = true;
      }
    }
  }

  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, DACAvoltage);  // If I give 1V, I measure 8V from TOPDRIVE
  Serial.print("DAC A has been set to ");
  Serial.println(DACAvoltage);
  delay(10000);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  Serial.println("End of test");
}

void test_dac_b_static() {
  // Static DAC B / BOT_DRIVE check.

  bool testing = false;
  float DACBvoltage = 0.0f;

  Serial.println("Type the voltage you want DAC B to output under 0.5V.");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      if (input.toFloat() > 0.5) {
        Serial.println("Too high of a voltage, try again.");
      } else {
        testing = true;
        DACBvoltage = input.toFloat();
      }
    }
  }


  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, DACBvoltage);  // I measured 8V from BOTDRIVE
  Serial.print("DAC B has been set to ");
  Serial.println(DACBvoltage);
  delay(10000);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("End of test");
}

void test_dual_dac() {
  // DAC A and DAC B active together.

  dac_set_voltage(AD5689_ADDR_DAC_A, 1.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 1.0f);
  Serial.println("DAC A and B has been both set to 1V");
  delay(15000);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("End of test");
}

void test_ispp_gate() {
  // ISPP-controlled row path check. (ISPP HIGH VS LOW)

  dac_set_voltage(AD5689_ADDR_DAC_A, 1.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("DAC A has been set to 1V");

  digitalWriteFast(PIN_ISPP, LOW);
  Serial.println("ISPP has been set to low, check ROW of ADG5234");
  delay(10000);

  digitalWriteFast(PIN_ISPP, HIGH);
  Serial.println("ISPP has been set to HIGH, check ROW of ADG5234");
  delay(10000);

  digitalWriteFast(PIN_ISPP, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("End of test");
}

void test_vp_gate() {
  // VP-controlled column bias path check.
  // TODO: define stimulus and pass condition.

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 1.0f);
  Serial.println("DAC B has been set to 1V");

  digitalWriteFast(PIN_VP, LOW);
  Serial.println("VP has been set to low, check D of U4 (ADG1219)");
  delay(10000);

  digitalWriteFast(PIN_VP, HIGH);
  Serial.println("VP has been set to HIGH, check D of U4 (ADG1219)");
  delay(10000);

  digitalWriteFast(PIN_VP, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("End of test");
}

void test_shiftreg_mapping() {
  // Check whether MOSI works on the shift register.
  // The selected row will be 0V and the unselected rows will be HIGH

  bool testing = false;
  int rownum = 0;

  Serial.println("Select the row you want to probe from 1 to 12");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      if (input.toInt() < 1 || input.toInt() > 12) {
        Serial.println("Row number out of bounds, try again.");
      } else {
        rownum = input.toInt();
        testing = true;
      }
    }
  }


  sr595_select_row(rownum);
  Serial.print("Row ");
  Serial.print(rownum);
  Serial.println(" selected — probe shift register");
  delay(10000);
  sr595_deselect_all();

  Serial.println("All rows deselected");
  Serial.println("End of test");
}

void test_column_switch() {
  // Column routing check.

  bool testing = false;
  int colnum = 0;

  Serial.println("Type the column you would like to check. (1,2,3)");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      switch (input.toInt()) {
        case 1:
          colnum = PIN_CC1;
          testing = true;
          break;
        case 2:
          colnum = PIN_CC2;
          testing = true;
          break;
        case 3:
          colnum = PIN_CC3;
          testing = true;
          break;
        default:
          Serial.println("Try again from 1,2,3");
      }
    }
  }

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.5f);
  Serial.println("DAC B has been set to 0.5V");

  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_VP, HIGH);
  Serial.println("VP has been set to HIGH, all CC's to LOW, check that BOT_DRIVE and COL1 on CON is the same");
  delay(10000);

  digitalWriteFast(colnum, HIGH);
  Serial.println("Check that col is now virtual GND");
  Serial.println("Also check TIA");
  delay(10000);

  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_VP, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("End of test");
}

void test_row_switch() {
  // test row switch with shift register and ISPP, and check if it's correctly reflected on the connector

  bool testing = false;
  int rownum = 0;

  Serial.println("Type the row you would like to check. (1 through 12)");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      if (input.toInt() < 1 || input.toInt() > 12) {
        Serial.println("Row number out of bounds, try again.");
      } else {
        rownum = input.toInt();
        testing = true;
      }
    }
  }

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.1f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("DAC A has been set to 0.1V");

  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_ISPP, HIGH);
  Serial.println("ISPP has been set to HIGH, check ROW of ADG5234");


  sr595_select_row(rownum);
  Serial.print("Row ");
  Serial.print(rownum);
  Serial.println(" selected — probe connector");
  delay(10000);



  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("End of test");
}



void test_spi1_cohabitation() {
  // Shared SPI1 stress check.
  // Testing that SR and DAC works fine simultaneously.
  Serial.println("About to turn on DAC, probe DAC output");

  delay(5000);
  dac_set_voltage(AD5689_ADDR_DAC_A, 1.5f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.5f);
  Serial.println("Both DAC A and B are on at 1.5V and 0.5V respectively.");

  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_ISPP, HIGH);
  sr595_select_row(2);
  Serial.println("ROW 2 has been selected.");
  delay(10000);
  sr595_select_row(4);
  Serial.println("ROW 4 has been selected.");
  delay(10000);

  sr595_deselect_all();
  digitalWriteFast(PIN_ISPP, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("Reset");

  delay(1000);
  Serial.println("About to select row, probe DAC output");
  delay(5000);

  digitalWriteFast(PIN_ISPP, HIGH);
  sr595_select_row(3);
  Serial.println("ROW 3 has been selected.");
  delay(10000);
  digitalWriteFast(PIN_ISPP, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 1.5f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.5f);
  delay(10000);

  sr595_deselect_all();
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  Serial.println("End of test");
}

void test_write_waveform() {
  // Write-path waveform check on dummy load.

  float v_write = 2.0f;
  dac_set_voltage(AD5689_ADDR_DAC_B, v_write / 2.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_write);

  digitalWriteFast(PIN_VP, HIGH);  // unselected cols to botdrive

  sr595_select_row(1);
  select_column(1);

  digitalWriteFast(PIN_ISPP, HIGH);
  Serial.println("Probe TOP and BOT drive and ROWS/COLS");
  delayMicroseconds(10000);

  digitalWriteFast(PIN_ISPP, LOW);

  digitalWriteFast(PIN_VP, LOW);

  sr595_deselect_all();
  deselect_all_columns();

  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  Serial.println("End of test");
}

void test_reset_pulse() {
  // Reset-only check.
  // TODO: assert reset, release reset, and observe integrator outputs.

  Serial.println("Probe the CSA VOUT for baseline check.");
  delay(5000);

  dac_set_voltage(AD5689_ADDR_DAC_A, 1.0f);

  digitalWriteFast(PIN_VP, HIGH);
  sr595_select_row(1);
  select_column(1);
  digitalWriteFast(PIN_ISPP, HIGH);
  Serial.println("Check row 1 and col 1 for voltage. And probe CSA VOUT.");
  delay(10000);

  digitalWriteFast(PIN_ISPP, LOW);

  digitalWriteFast(PIN_VP, LOW);

  sr595_deselect_all();
  deselect_all_columns();

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  Serial.println("Integrator has been reset. Prove CSA VOUT");
  pulse_integrator_reset(1);
  Serial.println("End of test");
}

void test_adc_baseline() {
  // baseline adc read time

  uint32_t t0 = micros();
  float v = adc_read_channel(1);
  uint32_t dt = micros() - t0;

  Serial.print("ADC read us: ");
  Serial.println(dt);
}

void test_tia_response() {
  // One-channel TIA sanity check.
  // TODO: stimulate one known column path and observe the corresponding TIA/ADC response.
}

void test_csa_hold() {
  // CSA / integrator hold behavior.
  // TODO: create one controlled event, then observe whether the output holds before reset.
}

void test_reset_repeatability() {
  // Repeat reset and compare baselines.
  // TODO: run several reset->read cycles and look for consistency.
}

void test_csa_accumulation() {
  // Integrator accumulation behavior.
  // TODO: apply repeated identical pulses and observe whether the output builds monotonically.
}

void test_read_cell_sanity() {
  // read_cell() sanity check on a known safe path/load.
  // TODO: call read_cell() only after reset and baseline behavior are trusted.
}



// test simply that the ispp vwrite pulse is increasing, ther is no vread or gnd.
void test_incr_ispp_pulse() {
  uint8_t col = 3;
  uint8_t row = 6;
  float v_write = 0.4f;

  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_VP, LOW);


  for (int i = 0; i < 30; i++) {
    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);  // give v/2 first before v due to safety reasons, (V/2 difference rather than full V difference)
    dac_set_voltage(AD5689_ADDR_DAC_A, v_write);

    //digitalWriteFast(PIN_VP, HIGH); // unselected cols to botdrive

    sr595_select_row(row);
    select_column(col);

    delay(1);
    digitalWriteFast(PIN_ISPP, HIGH);
    delay(1);


    digitalWriteFast(PIN_ISPP, LOW);
    sr595_deselect_all();
    deselect_all_columns();
    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
    dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

    Serial.println(adc_read_channel(3) / 510000.0, 15);

    v_write = v_write + 0.03f;
  }
  Serial.println("End of test");
}

// tests the full ispp waveform
void test_ispp_waveform() {
  uint8_t col = 1;
  uint8_t row = 1;
  float target = 1.5f;

  IsppParams params = {};
  params.v_read = 0.07f;
  params.v_start = 0.1f;
  params.v_step = 0.1f;
  params.v_max = 1.5f;
  params.tolerance = 0.01f;
  params.pulse_length = 1.0f;
  params.max_pulses = 15;

  run_ispp_cell(row, col, target, params);
  Serial.println("End of test");
}

// tests the decreasing step current
void test_tia_read_total_current() {

  Serial.println("Running parallel inference");
  delay(1000);
  InferenceParams params = {};
  params.max_scale = 10;
  params.v_read = 0.1f;
  params.t_unit_us = 100000;

  //
  uint8_t input[12] = { 10, 10, 10, 10, 10, 10, 10, 10, 10, 0, 0, 0 };
  //uint8_t input[12] = {10,8,6,4,2,1,0,0,0,0,0,0};
  //uint8_t input[12] = {10,8,6,4,2,1,7,3,0,0,0,0};


  float temp = run_parallel_inference(input, params);
  Serial.println("End of test");
}

void test_adc_readout() {

  bool testing = false;
  int adcnum = 0;
  int pinnum = 0;

  Serial.println("Type the ADC pins you would like to check. (A0 -> 1, A1 -> 2, A2 -> 3)");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      switch (input.toInt()) {
        case 1:
          pinnum = PIN_CC1;
          adcnum = 1;
          testing = true;
          break;
        case 2:
          pinnum = PIN_CC2;
          adcnum = 2;
          testing = true;
          break;
        case 3:
          pinnum = PIN_CC3;
          adcnum = 3;
          testing = true;
          break;
        default:
          Serial.println("Try again among 1,2,3");
      }
    }
  }

  float v = 0.0f;
  float min_v = 999.0f;
  float max_v = -999.0f;
  float sum_v = 0.0f;
  const int samples = 100;

  float v_offset = 0.0f;
  float sum_v_offset = 0.0f;
  float min_v_offset = 999.0f;
  float max_v_offset = -999.0f;

  pulse_integrator_reset(1);
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  sr595_deselect_all();

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.4f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  digitalWriteFast(PIN_ISPP, HIGH);
  // sr595_select_row(1);
  digitalWriteFast(pinnum, HIGH);
  digitalWriteFast(PIN_CC1, HIGH);

  Serial.println("ADS1115 readout truth test starting.");
  Serial.print("Hold ADC ");
  Serial.print(adcnum);
  Serial.println(" at a known stable DC voltage and compare against a multimeter.");

  pulse_integrator_reset(1);

  uint16_t mask = 0b1111111111111111;
  for (int i = 0; i < 9; ++i) {
    mask = mask & ~((uint16_t)(0x01) << i);
    sr595_select_multiple_rows(mask);

    for (int i = 0; i < samples; i++) {
      delay(10);

      v = adc_read_channel((uint8_t)adcnum);
      v_offset = adc_read_channel(1);

      sum_v += v;
      sum_v_offset += v_offset;

      if (v < min_v) min_v = v;
      if (v > max_v) max_v = v;

      if (v_offset < min_v_offset) min_v_offset = v_offset;
      if (v_offset > max_v_offset) max_v_offset = v_offset;

      Serial.print("Sample ");
      Serial.print(i);
      Serial.print(": ");
      Serial.println(v, 6);

      Serial.print("Sample ");
      Serial.print(i);
      Serial.print(" for offset: ");
      Serial.println(v_offset, 6);


      delay(20);
    }
  }

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  digitalWriteFast(PIN_ISPP, LOW);
  sr595_deselect_all();
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);

  Serial.println("End of test");
}

// testing mnist convolution (image processing) without pyserial, with manual copy and paste
void test_mnist() {

  const uint8_t mnist_image[20][20] = {
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 18, 32, 24, 30, 54, 40, 5, 0, 0 },
    { 0, 0, 0, 0, 0, 8, 22, 41, 61, 83, 91, 100, 107, 81, 93, 108, 65, 7, 0, 0 },
    { 0, 0, 0, 0, 2, 42, 111, 119, 122, 125, 119, 121, 109, 37, 35, 28, 11, 1, 0, 0 },
    { 0, 0, 0, 0, 1, 24, 87, 96, 127, 111, 52, 55, 74, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 2, 14, 25, 104, 77, 7, 2, 10, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 8, 73, 101, 21, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 1, 19, 90, 84, 52, 13, 1, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 1, 32, 91, 116, 74, 19, 1, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 20, 66, 114, 84, 18, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 7, 20, 107, 122, 47, 2, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 4, 29, 70, 101, 123, 114, 30, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 1, 3, 21, 64, 104, 122, 121, 95, 46, 8, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 4, 28, 50, 98, 122, 118, 94, 53, 14, 2, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 3, 30, 65, 107, 123, 126, 111, 58, 16, 1, 0, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 9, 70, 100, 100, 77, 58, 21, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
  };

  InferenceParams params = {};
  params.v_read = 0.4f;
  params.t_unit_us = 4652;
  params.max_scale = 128;

  uint8_t input12[12];
  float output_image[18][18];

  for (int row = 0; row < 18; row++) {
    for (int col = 0; col < 18; col++) {
      // zero everything first
      for (int i = 0; i < 12; i++) {
        input12[i] = 0;
      }

      // flatten 3x3 patch into first 9 entries
      int idx = 0;
      for (int pr = 0; pr < 3; pr++) {
        for (int pc = 0; pc < 3; pc++) {
          input12[idx++] = mnist_image[row + pr][col + pc];
        }
      }

      InferenceResults result = run_parallel_inference_nointe(input12, params);
      output_image[row][col] = result.manual_sum - result.manual_sum_offset;
    }
  }

  Serial.println("Finished MNIST patch sweep.");

  Serial.println("OUTPUT_IMAGE_BEGIN");
  for (int row = 0; row < 18; row++) {
    for (int col = 0; col < 18; col++) {
      Serial.print(output_image[row][col], 6);
      if (col < 18 - 1) {
        Serial.print(", ");
      }
    }
    Serial.println();
  }
  Serial.println("OUTPUT_IMAGE_END");
}

float read_adc_avg(uint8_t adc_channel, int samples = 50) {
  float sum = 0.0f;

  for (int i = 0; i < samples; ++i) {
    delay(5);
    sum += adc_read_channel(adc_channel);
  }

  return sum / samples;
}


void test_col_leakage() {

  const int samples = 50;

  pulse_integrator_reset(1);
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  sr595_deselect_all();

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.4f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  digitalWriteFast(PIN_ISPP, HIGH);
  digitalWriteFast(PIN_CC3, HIGH);

  Serial.println("Column leakage verifier starting.");

  uint16_t mask = 0b1111111111111111;
  pulse_integrator_reset(1);
  delay(3000);


  for (int i = 0; i < 9; ++i) {
    mask = mask & ~((uint16_t)(0x01) << i);
    sr595_select_multiple_rows(mask);
    delay(10);

    // -------------------------------
    // Case 1: CC3 only
    // -------------------------------
    digitalWriteFast(PIN_CC1, LOW);
    digitalWriteFast(PIN_CC3, HIGH);
    delay(20);

    float cc3_only_adc3 = read_adc_avg(3, samples);
    float cc3_only_adc1 = read_adc_avg(1, samples);

    // -------------------------------
    // Case 2: CC1 only
    // -------------------------------
    digitalWriteFast(PIN_CC3, LOW);
    digitalWriteFast(PIN_CC1, HIGH);
    delay(20);

    float cc1_only_adc3 = read_adc_avg(3, samples);
    float cc1_only_adc1 = read_adc_avg(1, samples);

    // -------------------------------
    // Case 3: CC3 + CC1
    // -------------------------------
    digitalWriteFast(PIN_CC1, HIGH);
    digitalWriteFast(PIN_CC3, HIGH);
    delay(20);

    float both_adc3 = read_adc_avg(3, samples);
    float both_adc1 = read_adc_avg(1, samples);

    float leak_into_3 = both_adc3 - cc3_only_adc3;
    float leak_into_1 = both_adc1 - cc1_only_adc1;

    Serial.println("--------------------------------");
    Serial.print("Rows active: ");
    Serial.println(i + 1);

    Serial.print("CC3 only, ADC3: ");
    Serial.println(cc3_only_adc3, 6);

    Serial.print("CC3 only, ADC1: ");
    Serial.println(cc3_only_adc1, 6);

    Serial.print("CC1 only, ADC3: ");
    Serial.println(cc1_only_adc3, 6);

    Serial.print("CC1 only, ADC1: ");
    Serial.println(cc1_only_adc1, 6);

    Serial.print("Both, ADC3: ");
    Serial.println(both_adc3, 6);

    Serial.print("Both, ADC1: ");
    Serial.println(both_adc1, 6);

    Serial.print("Leak into ADC3: ");
    Serial.println(leak_into_3, 6);

    Serial.print("Leak into ADC1: ");
    Serial.println(leak_into_1, 6);
  }

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  digitalWriteFast(PIN_ISPP, LOW);
  sr595_deselect_all();
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);

  Serial.println("End of test");
}


void wait_for_enter() {
  Serial.println("Press Enter to continue to next row.");

  while (true) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();
      break;
    }
  }
}

// for testing with the real ScAlN array
// this test goes through each 36 nodes of the 12x3 array and checks the conductance
// We know that (V_DAC * 8)G = I is the current we get at the cols
// I = V_ADC / R_ref is what the ADC reads through the TIA
// So to get G, we do G = V_ADC/(V_DAC *8 *R_ref)
void test_conductance_sweep() {

  pulse_integrator_reset(1);
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  sr595_deselect_all();

  dac_set_voltage(AD5689_ADDR_DAC_A, 1.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  digitalWriteFast(PIN_ISPP, HIGH);

  // for (int cols = 3; cols < 0; --cols) {

  //   if (cols == 3) {
  //     digitalWriteFast(PIN_CC3, HIGH);
  //   } else if (cols == 2) {
  //     digitalWriteFast(PIN_CC3, LOW);
  //     digitalWriteFast(PIN_CC2, HIGH);
  //   } else if (cols == 1) {
  //     digitalWriteFast(PIN_CC2, LOW);
  //     digitalWriteFast(PIN_CC1, HIGH);
  //   }

  //   for (int rows = 12; rows > 0; --rows) {
  //     sr595_select_row(rows);
  //     if (cols == 3) {

  //     } else if (cols == 2) {

  //     } else if (cols == 1) {

  //     }
  //   }
  // }




  const uint32_t sample_window_us = 1000000UL;
  const int max_samples = 900;

  uint32_t times[max_samples];
  float readings[max_samples];

  digitalWriteFast(PIN_CC1, HIGH);

  Serial.println("time_us,row,adc_voltage");

  for (int row = 12; row > 0; --row) {
    sr595_deselect_all();
    delay(20);

    int sample_count = 0;
    uint32_t t_start = micros();

    bool row_is_on = false;
    bool row_was_turned_off = false;

    while ((micros() - t_start < sample_window_us) && (sample_count < max_samples)) {
      uint32_t elapsed = micros() - t_start;

      if (!row_is_on && elapsed >= 500000UL) {
        sr595_select_row(row);
        delay(10);
        row_is_on = true;
      }

      if (row_is_on && !row_was_turned_off && elapsed >= 1500000UL) {
        sr595_deselect_all();
        delay(10);
        row_was_turned_off = true;
      }

      times[sample_count] = elapsed;
      readings[sample_count] = adc_read_channel(1);

      sample_count++;

      delay(1);
    }

    for (int i = 0; i < sample_count; ++i) {
      const char* phase;

      if (times[i] < 500000UL) {
        phase = "before";
      } else if (times[i] < 1500000UL) {
        phase = "on";
      } else {
        phase = "after";
      }

      Serial.print(times[i]);
      Serial.print(",");
      Serial.print(row);
      Serial.print(",");
      Serial.print(phase);
      Serial.print(",");
      Serial.println(readings[i], 6);
    }

    Serial.print("ROW_END,");
    Serial.println(row);

    wait_for_enter();
  }

  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  Serial.println("End of test");
}


void test_full_sweep() {

  pulse_integrator_reset(1);
  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);
  sr595_deselect_all();

  float vdac = 1.5f;
  float Rref = 1000000.0f;
  float adc3 = 0.0f;
  float adc2 = 0.0f;
  float adc1 = 0.0f;

  dac_set_voltage(AD5689_ADDR_DAC_A, vdac);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  digitalWriteFast(PIN_ISPP, HIGH);

  for (int cols = 3; cols > 0; --cols) {
    Serial.print("Col ");
    Serial.println(cols);
    if (cols == 3) {
      digitalWriteFast(PIN_CC3, HIGH);
    } else if (cols == 2) {
      digitalWriteFast(PIN_CC3, LOW);
      digitalWriteFast(PIN_CC2, HIGH);
    } else if (cols == 1) {
      digitalWriteFast(PIN_CC2, LOW);
      digitalWriteFast(PIN_CC1, HIGH);
    }

    for (int rows = 12; rows > 0; --rows) {
      sr595_select_row(rows);
      Serial.print("Row ");
      Serial.print(rows);
      Serial.print(" Conductance: ");
      if (cols == 3) {
        adc3 = read_adc_avg(3);
        Serial.println((adc3 / (8 * vdac * Rref)), 15);
        sr595_deselect_all();

      } else if (cols == 2) {
        adc2 = read_adc_avg(2);
        Serial.println((adc2 / (8 * vdac * Rref)), 15);
        sr595_deselect_all();
      } else if (cols == 1) {
        adc1 = read_adc_avg(1);
        Serial.println((adc1 / (8 * vdac * Rref)), 15);
        sr595_deselect_all();
      }
    }
  }

  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  Serial.println("End of test");
}

// ========================================================
// baseline adc reading to subtract from all my adc reading calculations 
float adc_baseline() {
  
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.53f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  sr595_deselect_all();
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, HIGH);

  digitalWriteFast(PIN_ISPP, HIGH);
  // float baseline = read_adc_avg(3, 10);

  float baseline = 0;
  for (int i = 0; i < 10; ++i) {
    float reading = adc_read_channel(3);
    Serial.println(reading,15);
    baseline += reading;
  }

  digitalWriteFast(PIN_ISPP, LOW);

  digitalWriteFast(PIN_CC3, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  return baseline/10;
}
// ========================================================

void test_run_ispp() {

  bool testing = false;
  uint8_t i = 12;


  Serial.println("Type the row you want to run ispp: ");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      if (input.toInt() > 12) {
        Serial.println("Invalid row");
      } else {
        testing = true;
        i = input.toInt();
      }
    }
  }

  //for (int i = 12; i > 11; --i) {

    IsppParams params = {};
    params.v_read = 0.6f;
    params.v_start = 0.8f;
    params.v_step = 0.005f;
    params.v_max = 1.5f;
    params.tolerance = 0.00000000200000;

    params.pulse_length = 3500.0f; // our adc read time is consistently about 2417 us. test 13. 
    params.max_pulses = 200;

    Serial.print("Running row "); Serial.println(i);
    IsppResult results = run_ispp_cell(i, 3, 0.00000004000000, params);
    //IsppResult results = run_ispp_cell(i, 2, 0.00004, params);



    Serial.print("Final resistance: ");
    Serial.println(results.final_readback);
    Serial.print("Cycles used: ");
    Serial.println(results.cycles_used);
    Serial.print("Last vwrite: ");
    Serial.println(results.last_write_voltage);
    Serial.println(results.success);

    digitalWriteFast(PIN_ISPP, LOW);
    digitalWriteFast(PIN_CC1, LOW);
    digitalWriteFast(PIN_CC2, LOW);
    digitalWriteFast(PIN_CC3, LOW);
    sr595_deselect_all();

    dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  //}
  Serial.println("End of test");
}

// attempt to erase conductance by starting at 0V to 12V to -12V back to 0V
void test_ivsweep_erase() {

  bool testing = false;
  uint8_t row = 12;
  float pulse_length = 3500.0f;
  float v_read = 0.6f;


  Serial.println("Type the row you want to reset: ");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      if (input.toInt() > 12) {
        Serial.println("Invalid row");
      } else {
        testing = true;
        row = input.toInt();
      }
    }
  }

  uint8_t col = 2;
  float v_write = 1.5f;

  // read_cell(row,col,v_read,pulse_length);

  // digitalWriteFast(PIN_CC2, LOW);
  // digitalWriteFast(PIN_CC1, LOW);
  // digitalWriteFast(PIN_VP, LOW);

  // Serial.println("From 12V to 0V");
  // for (int i = 0; i < 150; i++) {
  //   dac_set_voltage(AD5689_ADDR_DAC_A, v_write);
  //   dac_set_voltage(AD5689_ADDR_DAC_B, v_write/2);
  //   //sr595_select_multiple_rows(0b1111000000000000); // GND the row you want to reset and open all others to v_write
  //   sr595_select_multiple_rows(~(uint16_t)(1u << (row - 1)));

  //   digitalWriteFast(PIN_CC1, LOW);
  //   digitalWriteFast(PIN_CC2, LOW);
  //   digitalWriteFast(PIN_CC3, HIGH);

  //   digitalWriteFast(PIN_VP, HIGH);
  //   digitalWriteFast(PIN_ISPP, HIGH);
  //   delayMicroseconds(pulse_length);
  //   digitalWriteFast(PIN_ISPP, LOW);
  //   digitalWriteFast(PIN_VP, LOW);


  //   sr595_deselect_all();
  //   deselect_all_columns();
  //   dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  //   dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  //   v_write = v_write - 0.01f;
  //   delayMicroseconds(2*pulse_length);

  // }

  // read_cell(row,col,v_read,pulse_length);

  // --

  v_write = 0.01f;

  read_cell(row,col,v_read,pulse_length);

  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_VP, LOW);

  Serial.println("From 0V to -12V");
  for (int i = 0; i < 150; i++) {
    dac_set_voltage(AD5689_ADDR_DAC_A, v_write);
    dac_set_voltage(AD5689_ADDR_DAC_B, v_write);
    //sr595_select_multiple_rows(0b1111000000000000); // GND the row you want to reset and open all others to v_write
    sr595_select_multiple_rows((uint16_t)(1u << (row - 1)));

    digitalWriteFast(PIN_CC1, LOW);
    digitalWriteFast(PIN_CC2, LOW);
    digitalWriteFast(PIN_CC3, LOW);

    digitalWriteFast(PIN_VP, HIGH);
    digitalWriteFast(PIN_ISPP, HIGH);
    delayMicroseconds(pulse_length);
    digitalWriteFast(PIN_ISPP, LOW);
    digitalWriteFast(PIN_VP, LOW);


    sr595_deselect_all();
    deselect_all_columns();
    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
    dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

    v_write = v_write + 0.01f;
    delayMicroseconds(2*pulse_length);

  }
  v_write = 1.5f;
  for (int i = 0; i < 50; i++) {
    dac_set_voltage(AD5689_ADDR_DAC_A, v_write);
    dac_set_voltage(AD5689_ADDR_DAC_B, v_write);
    //sr595_select_multiple_rows(0b1111000000000000); // GND the row you want to reset and open all others to v_write
    sr595_select_multiple_rows((uint16_t)(1u << (row - 1)));

    digitalWriteFast(PIN_CC1, LOW);
    digitalWriteFast(PIN_CC2, LOW);
    digitalWriteFast(PIN_CC3, LOW);

    digitalWriteFast(PIN_VP, HIGH);
    digitalWriteFast(PIN_ISPP, HIGH);
    delayMicroseconds(pulse_length);
    digitalWriteFast(PIN_ISPP, LOW);
    digitalWriteFast(PIN_VP, LOW);


    sr595_deselect_all();
    deselect_all_columns();
    dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
    dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

    delayMicroseconds(2*pulse_length);

  }

  read_cell(row,col,v_read,pulse_length);

  // // --

  // v_write = 1.5f;

  // read_cell(row,col,v_read,pulse_length);

  // digitalWriteFast(PIN_CC2, LOW);
  // digitalWriteFast(PIN_CC1, LOW);
  // digitalWriteFast(PIN_VP, LOW);

  // Serial.println("From -12V to 0V");
  // for (int i = 0; i < 150; i++) {
  //   dac_set_voltage(AD5689_ADDR_DAC_A, v_write);
  //   dac_set_voltage(AD5689_ADDR_DAC_B, v_write);
  //   //sr595_select_multiple_rows(0b1111000000000000); // GND the row you want to reset and open all others to v_write
  //   sr595_select_multiple_rows((uint16_t)(1u << (row - 1)));

  //   digitalWriteFast(PIN_CC1, LOW);
  //   digitalWriteFast(PIN_CC2, LOW);
  //   digitalWriteFast(PIN_CC3, LOW);

  //   digitalWriteFast(PIN_VP, HIGH);
  //   digitalWriteFast(PIN_ISPP, HIGH);
  //   delayMicroseconds(pulse_length);
  //   digitalWriteFast(PIN_ISPP, LOW);
  //   digitalWriteFast(PIN_VP, LOW);


  //   sr595_deselect_all();
  //   deselect_all_columns();
  //   dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  //   dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

  //   v_write = v_write - 0.01f;
  //   delayMicroseconds(2*pulse_length);

  // }

  // read_cell(row,col,v_read,pulse_length);


  Serial.println("End of test");



}


void test_pwm_drift() {

  bool testing = false;
  uint8_t row;
  float pulse_length = 3500.0f;
  // float v_read = 0.55f;
  float v_read = 0.6f;




  Serial.println("Type the row you want to do PWM ");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      if (input.toInt() > 12) {
        Serial.println("Invalid row");
      } else {
        testing = true;
        row = input.toInt();
      }
    }
  }

  uint8_t col = 3;

  // for (int i = 0; i < 70; ++i) {
  //   read_cell(row,col,v_read,pulse_length);
  // }

  for (int i = 0; i < 100; ++i) {
    read_cell(row,col,v_read,pulse_length);
    delayMicroseconds(pulse_length * 3);
  }
  Serial.println("IDLE");
  delay(2000);
  for (int i = 0; i < 100; ++i) {
    read_cell(row,col,v_read,pulse_length);
    delayMicroseconds(pulse_length * 3);
  }
}

void test_two_row_current() {

  float baseline = adc_baseline();


  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.53f);
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, HIGH);

  bool testing = false;
  int comma = 0;
  uint16_t mask = 0b1111111111111111;
  int row1 = 0;
  int row2 = 0;

  Serial.println("Type the rows you want the total current of. (Separate with commas for multiple rows)");
  while (!testing) {
    if (Serial.available() > 0) {
      String input = Serial.readStringUntil('\n');
      input.trim();

      comma = input.indexOf(',');

      if (comma == -1) {
        mask = ~(0x01 << (input.toInt() - 1));
        testing = true;
        row1 = input.toInt();
      } else {
        row1 = input.substring(0,comma).toInt();
        row2 = input.substring(comma+1).toInt();

        mask = (uint16_t)~((uint16_t)(1u << (row1 - 1)) | (uint16_t)(1u << (row2 - 1)));
        testing = true;
      }

    }
  }

  Serial.print("Running rows ");Serial.print(row1);Serial.print(" and ");Serial.println(row2);

  sr595_select_multiple_rows(mask);
  digitalWriteFast(PIN_ISPP, HIGH);

  float sum = 0.0f;
  int samples = 10;
  uint8_t adc_channel = 3;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel) - baseline;
    Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }


  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);

  sr595_deselect_all();
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
}

void test_tworows() {

  //float baseline = adc_baseline();


  pulse_integrator_reset(1);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.55f);
  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, HIGH);



  sr595_select_multiple_rows(0b1111111111111101);
  digitalWriteFast(PIN_ISPP, HIGH);

  float sum = 0.0f;
  int samples = 30;
  uint8_t adc_channel = 3;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }


  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 2 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  // -----
  sr595_select_multiple_rows(0b1111011111111111);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }


  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 12 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  // -----
  sr595_select_multiple_rows(0b1111111111111110);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }


  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 1 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  // -----
  sr595_select_multiple_rows(0b1111111111111100);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }

  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 1, 2 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  // -----
  sr595_select_multiple_rows(0b1111011111111100);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }

  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 12,1,2 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  

  // -----
  sr595_select_multiple_rows(0b1111001111111100);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }

  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 12,1,2,11 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  

  // -----
  sr595_select_multiple_rows(0b1111001111111101);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }

  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 12,11,2 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  

  // -----
  sr595_select_multiple_rows(0b1111101111111101);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }

  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 2,11 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  // -----
  sr595_select_multiple_rows(0b1111101111111111);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }

  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("Row 11 Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);
  // -----
  sr595_select_multiple_rows(0b1111111111111111);
  digitalWriteFast(PIN_ISPP, HIGH);

  sum = 0.0f;
  for (int i = 0; i < samples; ++i) {
    float adcreading = adc_read_channel(adc_channel);
    //Serial.print("ADC: "); Serial.println(adcreading,15);
    Serial.print("Current: "); Serial.println(adcreading/1000000.0f,15);
    if (i > 2) {
      sum += adcreading;
    } 
  }

  digitalWriteFast(PIN_ISPP, LOW);

  Serial.print("No Row Avg Current: ");Serial.println((sum / (samples-3))/1000000.0f,15);


  sr595_deselect_all();
  digitalWriteFast(PIN_CC3, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC1, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
}

// ----------------------
float read_mask_once_col3(uint16_t mask, float v_read) {
  const float RF = 1000000.0f;

  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_A, v_read);

  digitalWriteFast(PIN_VP, LOW);
  digitalWriteFast(PIN_CC1, LOW);
  digitalWriteFast(PIN_CC2, LOW);
  digitalWriteFast(PIN_CC3, HIGH);

  sr595_select_multiple_rows(mask);

  digitalWriteFast(PIN_ISPP, HIGH);
  delayMicroseconds(1000);   // settle/read pulse before ADC starts

  float adc = adc_read_channel(3);

  digitalWriteFast(PIN_ISPP, LOW);
  sr595_deselect_all();
  digitalWriteFast(PIN_CC3, LOW);
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  delayMicroseconds(4000);

  return adc / RF;
}

void run_mask_segment(const char* label, uint16_t mask, float v_read) {
  const int samples = 20;
  float currents[samples];

  for (int i = 0; i < samples; ++i) {
    currents[i] = read_mask_once_col3(mask, v_read);
  }

  float sum = 0.0f;

  Serial.println(label);
  for (int i = 0; i < samples; ++i) {
    Serial.print("Current: ");
    Serial.println(currents[i], 15);

    // Average all independent short-pulse reads.
    // If first few still look transient, change this to i >= 3.
    sum += currents[i];
  }

  Serial.print(label);
  Serial.print(" Avg Current: ");
  Serial.println(sum / samples, 15);
}

// void run_single_row_baseline(float v_read) {
//   const int samples = 20;
//   float currents[samples];

//   for (int i = 0; i < samples; ++i) {
//     currents[i] = read_mask_once_col3(mask, v_read);
//   }

//   float sum = 0.0f;

//   for (int i = 0; i < samples; ++i) {
//     Serial.print("Current: ");
//     Serial.println(currents[i], 15);

//     // Average all independent short-pulse reads.
//     // If first few still look transient, change this to i >= 3.
//     sum += currents[i];
//   }

//   Serial.print(" Avg Current: ");
//   Serial.println(sum / samples, 15);
// }




void test_cleanrows() {
  float v_read = 0.60f;

  uint16_t no_rows = 0b1111111111111111;

  uint16_t row1 = 0b1111111111111110;
  uint16_t row2 = 0b1111111111111101;
  uint16_t row11 = 0b1111101111111111;
  uint16_t row12 = 0b1111011111111111;

  uint16_t row1_2 = 0b1111111111111100;
  uint16_t row2_11 = 0b1111101111111101;
  uint16_t row12_1_2 = 0b1111011111111100;
  uint16_t row12_11_2 = 0b1111001111111101;
  uint16_t row12_1_2_11 = 0b1111001111111100;

  run_mask_segment("No Rows Before", no_rows, v_read);

  run_mask_segment("Row 1", row1, v_read);

  run_mask_segment("Row 2", row2, v_read);

  run_mask_segment("Row 11", row11, v_read);

  run_mask_segment("Row 12", row12, v_read);

  run_mask_segment("Row 2,11", row2_11, v_read);

  run_mask_segment("Row 12,11,2", row12_11_2, v_read);

  run_mask_segment("Row 12,1,2,11", row12_1_2_11, v_read);

  run_mask_segment("Row 12,1,2", 0b1111011111111100, v_read);

  run_mask_segment("Row 12,1", 0b1111011111111110, v_read);

  run_mask_segment("Row 1", 0b1111111111111110, v_read);

  run_mask_segment("No Rows Before", no_rows, v_read);

}

void test_set_weights() {

  
  uint8_t row = 12;
  float pulse_length = 3500.0f;
  float v_read = 0.6f;
  uint8_t col = 3;

  IsppParams params = {};
  params.v_read = 0.6f;
  params.v_start = 0.8f;
  params.v_step = 0.005f;
  params.v_max = 1.5f;
  params.tolerance = 0.00000000250000;

  params.pulse_length = 3500.0f; // our adc read time is consistently about 2417 us. test 13. 
  params.max_pulses = 200;


  for (int rw = 12; rw > 8; --rw) {
    for (int twice = 0; twice < 2; ++twice) {
      // program twice, once for calibration and once again for the rela weight setting
      if (rw == 10) {
        row = 2;
      } else if (rw == 9) {
        row = 1;
      } else {
        row = rw;
      }

      // reset cell 
      float v_write = 0.01f;
      read_cell(row,col,v_read,pulse_length);

      digitalWriteFast(PIN_CC2, LOW);
      digitalWriteFast(PIN_CC1, LOW);
      digitalWriteFast(PIN_VP, LOW);

      Serial.println("From 0V to -12V");
      for (int i = 0; i < 150; i++) {
        dac_set_voltage(AD5689_ADDR_DAC_A, v_write);
        dac_set_voltage(AD5689_ADDR_DAC_B, v_write);
        //sr595_select_multiple_rows(0b1111000000000000); // GND the row you want to reset and open all others to v_write
        sr595_select_multiple_rows((uint16_t)(1u << (row - 1)));

        digitalWriteFast(PIN_CC1, LOW);
        digitalWriteFast(PIN_CC2, LOW);
        digitalWriteFast(PIN_CC3, LOW);

        digitalWriteFast(PIN_VP, HIGH);
        digitalWriteFast(PIN_ISPP, HIGH);
        delayMicroseconds(pulse_length);
        digitalWriteFast(PIN_ISPP, LOW);
        digitalWriteFast(PIN_VP, LOW);


        sr595_deselect_all();
        deselect_all_columns();
        dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
        dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);

        v_write = v_write + 0.01f;
        delayMicroseconds(2*pulse_length);

      }

      read_cell(row,col,v_read,pulse_length);

      Serial.print("Running row "); Serial.println(row);

      float weight = 0.0f;
      if (twice == 1 && row == 12) {
        weight = 0.00000006;
      } else if (twice == 1 && ( row == 11 || row == 2)) {
        weight = 0.00000004;
      } else if (twice == 1 && row == 1) {
        weight = 0.00000002;
      } else {
        weight = 0.000004;
      }

      // IsppResult results = run_ispp_cell(i, 3, 0.00000004000000, params);
      IsppResult results = run_ispp_cell(row, 3, weight, params);



      Serial.print("Final resistance: ");
      Serial.println(results.final_readback);
      Serial.print("Cycles used: ");
      Serial.println(results.cycles_used);
      Serial.print("Last vwrite: ");
      Serial.println(results.last_write_voltage);
      Serial.println(results.success);

      digitalWriteFast(PIN_ISPP, LOW);
      digitalWriteFast(PIN_CC1, LOW);
      digitalWriteFast(PIN_CC2, LOW);
      digitalWriteFast(PIN_CC3, LOW);
      sr595_deselect_all();

      dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
      dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);
    }
  }
  Serial.println("Weights all set");
}



