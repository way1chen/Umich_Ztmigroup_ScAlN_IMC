#include "pythoncom.h"

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

  InferenceParams params = {};
  params.v_read = 0.005f;
  params.t_unit_us = 4652;
  params.max_scale = 128;
  params.use_offset = use_offset;

  String stream = "";
  uint8_t patcharr[12];
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

    String patchline = Serial.readStringUntil('\n');
    patchline.trim();

    // making patch string into int array for input to our array
    for (int i = 0; i < 9; ++i) {
      // indexOf gives the index of the first comma it sees
      comma = patchline.indexOf(',');

      if (comma == -1) { // when we are on the last number, there will be no comma
        patcharr[i] = patchline.toInt();
      } else {
        patcharr[i] = patchline.substring(0, comma).toInt(); // substring with bounds specified gives from start to end but not including end.
        patchline = patchline.substring(comma + 1);
      }
    }
    // fill array with zeros because iinference expects array of 12
    // row 10 for the baseline subtraction, which must be on in the entire duration of the patch
    uint8_t patch_max = 0;
    for (int i = 0; i < 9; ++i) {
      // parse patcharr[i]
      if (patcharr[i] > patch_max) {
        patch_max = patcharr[i];
      }
    }

    int row10max = max((uint8_t)1,patch_max);

    patcharr[9] = row10max;
    patcharr[10] = 0; // row 11
    patcharr[11] = 0; // row 12

    // run inference
    // print that gets read immediately by the pyserial. We don't see on the monitor. 

    InferenceResults result = run_parallel_inference_nointe_real_array(patcharr, params);
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
  params.v_read = 0.005f;
  params.t_unit_us = 4652;
  params.max_scale = 32;
  params.use_offset = false;

  // print that gets read immediately by the pyserial. We don't see on the monitor. 
  InferenceResults result = run_parallel_inference_nointe_CNN(patcharr, params);
  Serial.print(result.manual_sum, 6);
  Serial.print(",");
  Serial.println(result.col_2_sum, 6);
}


