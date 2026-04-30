#include "integrator.h"

void integrator_init() {
  pinMode(PIN_RESET1, OUTPUT);
  digitalWriteFast(PIN_RESET1, LOW);
  pinMode(PIN_RESET2, OUTPUT);
  digitalWriteFast(PIN_RESET2, LOW);
  pinMode(PIN_RESET3, OUTPUT);
  digitalWriteFast(PIN_RESET3, LOW);
}

void reset_integrator() {
  // reset the integrator
  digitalWriteFast(PIN_RESET1, HIGH);
  digitalWriteFast(PIN_RESET2, HIGH);
  digitalWriteFast(PIN_RESET3, HIGH);
}

void set_integrator() {
  // set the integrator to accumulation mode
  digitalWriteFast(PIN_RESET1, LOW);
  digitalWriteFast(PIN_RESET2, LOW);
  digitalWriteFast(PIN_RESET3, LOW);
}

void pulse_integrator_reset(float reset_pulse_length) {

  if (reset_pulse_length < 0.0f) {
    return;
  }
  reset_integrator();
  delay(reset_pulse_length);
  set_integrator();

}
