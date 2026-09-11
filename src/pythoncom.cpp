#include "pythoncom.h"
#include "ispp.h"
#include "array_ops.h"

void run_patch_sanity_suite(String patch, bool use_offset) {
  String stream = "";
  uint8_t patcharr[12];
  int comma = 0;
  String value = "";

  // substring gives a string at that index to the end. Strings are 0 indexed.
  if (use_offset) {
  stream = patch.substring(10); // "PATCHOFFS,"
  } else {
    stream = patch.substring(6);  // "PATCH,"
  }

  // making patch string into int array for input to our array
  for (int i = 0; i < 9; ++i) {
    // indexOf gives the index of the first comma it sees
    comma = stream.indexOf(',');

    if (comma == -1) { // when we are on the last number, there will be no comma
      patcharr[i] = stream.toInt();
    } else {
      patcharr[i] = stream.substring(0, comma).toInt(); // substring with bounds specified gives from start to end but not including end.
      stream = stream.substring(comma + 1);
    }
  }
  // fill array with zeros because iinference expects array of 12
  patcharr[9] = 0;
  patcharr[10] = 0;
  patcharr[11] = 0;

  // run inference
  InferenceParams params = {};
  params.v_read = 0.005f;
  params.t_unit_us = 4652;
  params.max_scale = 128;
  params.use_offset = use_offset;

  // print that gets read immediately by the pyserial. We don't see on the monitor. 
  InferenceResults result = run_parallel_inference_nointe(patcharr, params);
  Serial.print(result.manual_sum, 6);
  Serial.print(",");
  Serial.println(result.manual_sum_offset, 6);
}



void run_mnist_test_realarray(String patch, bool use_offset) {

  // indicate which rows we are using and which row we are using for always on row
  uint8_t patcharr[12];
  const uint8_t kernel_rows[] = {3, 4, 6, 8, 9, 12}; //actual rows I am using
  const uint8_t baseline_row = 10;
  const uint8_t kernel_len = sizeof(kernel_rows) / sizeof(kernel_rows[0]);


  InferenceParams params = {};
  params.v_read = 0.9f;
  params.t_unit_us = 4652;
  params.max_scale = 128;
  params.baseline_row = baseline_row;
  params.use_offset = use_offset;

  String stream = "";
  int comma = 0;
  String value = "";

  

  // substring gives a string at that index to the end. Strings are 0 indexed.
  if (use_offset) {
  stream = patch.substring(15); // "PATCHBATCHOFFS,#ofpatches\n .,.,.\n .,.,. \n"
  } else {
    stream = patch.substring(11);  // "PATCHBATCH,#ofpatches\n .,.,.\n .,.,. \n"
  }

  int numofpatches = stream.toInt();

  for (int iters = 0; iters < numofpatches; ++iters) {

    for (int i = 0; i < 12; ++i) {
      patcharr[i] = 0;
    } 

    String patchline = Serial.readStringUntil('\n');
    patchline.trim();
    if (patchline.length() == 0) {
      Serial.print("BATCH_INPUT_TIMEOUT:");
      Serial.println(iters);
      return;
    }

    // making patch string into int array for input to our array
    for (int i = 0; i < kernel_len; ++i) {
      // indexOf gives the index of the first comma it sees
      comma = patchline.indexOf(',');
      uint8_t val;

      if (comma == -1) { // when we are on the last number, there will be no comma
        val = patchline.toInt();
      } else {
        val = patchline.substring(0, comma).toInt(); // substring with bounds specified gives from start to end but not including end.
        patchline = patchline.substring(comma + 1);
      }
      patcharr[kernel_rows[i]-1] = val; // -1 because patcharr[0] is row 1, [1] is row 2, etc...
    }
    // fill array with zeros because iinference expects array of 12
    // row 10 for the baseline subtraction, which must be on in the entire duration of the patch
    uint8_t patch_max = 0;
    for (int i = 0; i < kernel_len; ++i) {
      uint8_t idx = kernel_rows[i] -1;
      // parse patcharr[i]
      if (patcharr[idx] > patch_max) {
        patch_max = patcharr[idx];
      }
    }

    //int row10max = max((uint8_t)1,patch_max);

    if (patch_max == 0) {
      Serial.println("0.000000,0.000000");
      continue;
    }

    patcharr[baseline_row - 1] = patch_max;

    // run inference
    // print that gets read immediately by the pyserial. We don't see on the monitor. 

    InferenceResults result = run_parallel_inference_nointe_real_array(patcharr, params);
    //InferenceResults result = run_parallel_inference_nointe_bitser(patcharr, params);
    Serial.print(result.manual_sum, 6);
    Serial.print(",");
    Serial.println(result.manual_sum_offset, 6);
  }
  Serial.println("BATCH_DONE");
}


// This test 
// ==========================================================================
void run_cnn_test_resistor(String patch)  {
  String stream = "";
  uint8_t patcharr[12];
  int comma = 0;
  String value = "";

  // substring gives a string at that index to the end. Strings are 0 indexed.

  stream = patch.substring(9);  // "PATCHCNN,"

  // making patch string into int array for input to our array
  for (int i = 0; i < 9; ++i) {
    // indexOf gives the index of the first comma it sees
    comma = stream.indexOf(',');

    if (comma == -1) { // when we are on the last number, there will be no comma
      patcharr[i] = stream.toInt();
    } else {
      patcharr[i] = stream.substring(0, comma).toInt(); // substring with bounds specified gives from start to end but not including end.
      stream = stream.substring(comma + 1);
    }
  }
  // fill array with zeros because iinference expects array of 12
  patcharr[9] = 0;
  patcharr[10] = 0;
  patcharr[11] = 0;

  // run inference
  InferenceParams params = {};
  params.v_read = 0.6f; // 0.005 for resistor array
  params.t_unit_us = 4652;
  params.max_scale = 32;
  params.use_offset = false;

  // print that gets read immediately by the pyserial. We don't see on the monitor. 
  InferenceResults result = run_parallel_inference_nointe_CNN(patcharr, params);
  Serial.print(result.manual_sum, 6);
  Serial.print(",");
  Serial.println(result.col_2_sum, 6);
}

void run_cnn_set_weights(String patch) {
  String stream = "";
  float weights[18];
  int comma = 0;
  String value = "";

  // substring gives a string at that index to the end. Strings are 0 indexed.
  stream = patch.substring(8);  // "WEIGHTS,"

  // making patch string into int array for input to our array
  for (int i = 0; i < 18; ++i) {


    // indexOf gives the index of the first comma it sees
    comma = stream.indexOf(',');

    if (comma == -1) { // when we are on the last number, there will be no comma
      weights[i] = stream.toFloat();
    } else {
      weights[i] = stream.substring(0, comma).toFloat(); // substring with bounds specified gives from start to end but not including end.
      stream = stream.substring(comma + 1);
    }
  }

  
  // set weights
  float pulse_length = 3500.0f;
  float v_read = 0.6f;

  IsppParams params = {};
  params.v_read = 0.6f;
  params.v_start = 0.8f;
  params.v_step = 0.005f;
  params.v_max = 1.5f;
  params.tolerance = 0.00000000250000;

  params.pulse_length = 3500.0f; // our adc read time is consistently about 2417 us. test 13. 
  params.max_pulses = 200;

  for (int col = 2; col > 0; --col) {
    for (int row = 9; row > 0; --row) {
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

      // IsppResult results = run_ispp_cell(i, 3, 0.00000004000000, params);
      int row_idx = row - 1;
      int col_idx = col - 1;
      int weight_idx = col_idx * 9 + row_idx;
      IsppResult results = run_ispp_cell(row, col, weights[weight_idx], params);



      Serial.print("Final conductance: ");
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
  // send back to python indicating that weights have been set and are ready.
  Serial.println("ACK");

}


void run_cnn_test_onecol(String patch) {

  const uint8_t kernel_rows[] = {3, 4, 6, 8, 9, 12}; //actual rows I am using
  const uint8_t baseline_row = 10;
  const uint8_t kernel_len = sizeof(kernel_rows) / sizeof(kernel_rows[0]);

  // Change this only if your usable CNN column changes.
  const uint8_t cnn_col = 3;

  String stream = patch.substring(12); // "PATCHCNNONE,"

  uint8_t patcharr[12] = {};
  for (int i = 0; i < 11; ++i) {
    patcharr[i] = 0;
  }
  int comma = 0;

  for (int i = 0; i < kernel_len; ++i) {
    comma = stream.indexOf(',');

    if (comma == -1) {
      patcharr[kernel_rows[i]-1] = stream.toInt();
    } else {
      patcharr[kernel_rows[i]-1] = stream.substring(0, comma).toInt();
      stream = stream.substring(comma + 1);
    }
  }

  uint8_t patch_max = 0;
    for (int i = 0; i < kernel_len; ++i) {
      uint8_t idx = kernel_rows[i] -1;
      // parse patcharr[i]
      if (patcharr[idx] > patch_max) {
        patch_max = patcharr[idx];
      }
    }
  patcharr[baseline_row - 1] = patch_max;

  InferenceParams params = {};
  params.v_read = 0.9f;
  params.t_unit_us = 4652;
  params.max_scale = 32;
  params.baseline_row = baseline_row;
  params.use_offset = false;



  InferenceResults result =
      run_parallel_inference_nointe_CNN_onecol(
          patcharr,
          params,
          cnn_col
      );

  Serial.println(result.manual_sum, 6);
}

void run_cnn_set_weights_onecol(String patch) {

  const uint8_t kernel_rows[] = {3, 4, 6, 8, 9, 10, 12}; //actual rows I am using
  const uint8_t baseline_row = 10;
  const uint8_t kernel_len = sizeof(kernel_rows) / sizeof(kernel_rows[0]);

  String stream = patch.substring(11); // "CNNWEIGHTS,"

  float weights[12];
  for (int i = 0; i < 12; ++i) {
    weights[i] = 0;
  }
  int comma = 0;

  for (int i = 0; i < kernel_len; ++i) {

    if (kernel_rows[i] == baseline_row) {
        weights[baseline_row - 1] = 0.000000035f;
        continue;
    }

    comma = stream.indexOf(',');

    if (comma == -1) {
      weights[kernel_rows[i]-1] = stream.toFloat();
    } else {
      weights[kernel_rows[i]-1] = stream.substring(0, comma).toFloat();
      stream = stream.substring(comma + 1);
    }
  }

  const uint8_t cnn_col = 3;
  const float pulse_length = 3500.0f;
  const float v_read = 0.9f;

  IsppParams params = {};
  params.v_read = v_read;
  params.v_start = 0.8f;
  params.v_step = 0.005f;
  params.v_max = 1.5f;
  params.tolerance = 0.0000000003;
  params.pulse_length = pulse_length;
  params.max_pulses = 200;

  bool all_success = true;


  for (uint8_t row = 0; row < kernel_len; ++row) {
    // This uses your existing reset approach for each target cell.
    float v_write = 0.01f;

    for (int i = 0; i < 150; ++i) {
      dac_set_voltage(AD5689_ADDR_DAC_A, v_write);
      dac_set_voltage(AD5689_ADDR_DAC_B, v_write);

      sr595_select_multiple_rows(
          (uint16_t)(1u << (kernel_rows[row] - 1))
      );

      deselect_all_columns();

      digitalWriteFast(PIN_VP, HIGH);
      digitalWriteFast(PIN_ISPP, HIGH);

      delayMicroseconds(pulse_length);

      digitalWriteFast(PIN_ISPP, LOW);
      digitalWriteFast(PIN_VP, LOW);

      sr595_deselect_all();
      deselect_all_columns();

      dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
      dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

      v_write += 0.01f;

      delayMicroseconds(2 * pulse_length);
    }

    Serial.print("Programming CNN row ");
    Serial.println(kernel_rows[row]);

    IsppResult result = run_ispp_cell(
        kernel_rows[row],
        cnn_col,
        weights[kernel_rows[row] - 1],
        params
    );

    Serial.print("Final conductance: ");
    Serial.println(result.final_readback, 12);
    if (!result.success) {
      all_success = false;

      Serial.print("PROGRAM_FAIL: row ");
      Serial.println(kernel_rows[row]);
    }
  }

  sr595_deselect_all();
  deselect_all_columns();

  digitalWriteFast(PIN_ISPP, LOW);
  digitalWriteFast(PIN_VP, LOW);

  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);

  if (all_success) {
    Serial.println("ACK");
  } else {
    Serial.println("ERROR:CNN_WEIGHT_PROGRAMMING_FAILED");
  }
}
