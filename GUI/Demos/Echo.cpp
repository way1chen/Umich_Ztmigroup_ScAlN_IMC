//For testing serial communication
#include <Arduino.h>



void setup() {
  Serial.begin(115200);
}

void loop() {
  //Echos incoming serial data
  if(Serial.available()){
    auto ser_in = Serial.read();
    Serial.write(ser_in);
  }
}