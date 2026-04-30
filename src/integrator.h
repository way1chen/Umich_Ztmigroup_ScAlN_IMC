#ifndef INTEGRATOR_H
#define INTEGRATOR_H

#include <Arduino.h>

#define PIN_RESET1 23
#define PIN_RESET2 1
#define PIN_RESET3 0

void integrator_init();

void reset_integrator();
void set_integrator();
void pulse_integrator_reset(float reset_pulse_length);

// maybe later:
// float read_output_channel(uint8_t channel);
// void read_all_outputs(float outputs[3]);

#endif