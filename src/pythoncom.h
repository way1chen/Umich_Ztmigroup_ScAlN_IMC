#ifndef PYTHONCOM_H
#define PYTHONCOM_H

#include <Arduino.h>
#include "inference.h"

void run_patch_sanity_suite(String patch, bool use_offset);

void run_mnist_test_realarray(String patch, bool use_offset);

void run_cnn_test_resistor(String patch);


#endif