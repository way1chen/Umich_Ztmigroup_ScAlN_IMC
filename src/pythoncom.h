#ifndef PYTHONCOM_H
#define PYTHONCOM_H

#include <Arduino.h>
#include "inference.h"

void run_patch_sanity_suite(String patch, bool use_offset);

void run_mnist_test_realarray(String patch, bool use_offset);

void run_cnn_test_resistor(String patch);

void run_cnn_set_weights(String patch);

void run_cnn_test_onecol(String patch);
void run_cnn_set_weights_onecol(String patch);


#endif