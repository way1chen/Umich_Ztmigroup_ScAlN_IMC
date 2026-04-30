/*
 * Mi Lab ScAlN Memristor Array 
 * ============================================
 * A 12-row × 3-column ScAlN Memristor crossbar array
 * --------------------------------------------
 */

#include <Arduino.h>
#include <SPI.h>
#include "ad5689.h"
#include "ad7689.h"
#include "sr595.h"
#include "array_ops.h"
#include "analog_io.h"
#include "tests.h"
#include "ispp.h"
#include "integrator.h"
#include "pythoncom.h"

// The ADC we are using instead now
#include "ads1115.h"
#include <Wire.h>

#define PIN_PU 32 // pull up pin for turning on before 3.3V switch
#define PIN_RST 31 // connects to RESET# of the DAC

bool systemEnabled = false; 
bool hardwareInitialized = false;
bool armed = false;

// ============================================================
// --- HARDWARE SETUP ---
// Initial hardware setup, initializing all the digital parts 
// ============================================================
void setup_hardware() {
  // --- SPI Init ---
  // sets up MOSI/MISO/clock
  SPI.begin(); // for ADC
  SPI1.begin(); // for DAC and SR

  Wire.begin();
  Wire.setClock(100000); // was 400000 before
  delay(20);

  // Set RST to high for DAC to work
  pinMode(PIN_RST, OUTPUT);
  digitalWriteFast(PIN_RST, HIGH);

  // --- DAC Init (AD5689) ---
  ad5689_reset(SPI1, PIN_CS_DAC);  // software reset to known state
  delay(1);                 

  // Use internal 2.5V reference
  // Switch to AD5689_REF_OFF if using external reference
  ad5689_set_internal_ref(SPI1, PIN_CS_DAC, AD5689_REF_ON);

  // Set both outputs to 0V safe state
  dac_set_voltage(AD5689_ADDR_DAC_A, 0.0f);  // TOP_DRIVE = 0V
  dac_set_voltage(AD5689_ADDR_DAC_B, 0.0f);  // BOT_DRIVE = 0V
  Serial.println("DAC initialized. TOP_DRIVE=0V, BOT_DRIVE=0V");

  // --- ADC Init (AD7689) ---
  // uint16_t initCfg = ADC_BASE_CFG | AD7689_CH(0);
  // ad7689_init(SPI, PIN_CS_ADC, adcSettings, initCfg);
  // Serial.println("ADC initialized.");

  delay(20);

  // Checking ads1115 initialization state
  if (!adc_init()) {
    Serial.println("ERROR: ADS1115 init failed.");
    Serial.println("Scanning I2C bus...");
    uint8_t found = 0;
    for (uint8_t addr = 1; addr < 127; addr++) {
      Wire.beginTransmission(addr);
      uint8_t error = Wire.endTransmission();

      if (error == 0) {
        Serial.print("Found device at 0x");
        if (addr < 16) Serial.print("0");
        Serial.println(addr, HEX);
        found++;
      }
    }
    if (found == 0) {
      Serial.println("No I2C devices found.");
    } else {
      Serial.println("I2C scan complete.");
    }
    hardwareInitialized = false;
    return;
  } 

  Serial.print("ADS1115 initialized at I2C address 0x");
  Serial.println(ADS1115_I2C_ADDR, HEX);

 
  // --- Shift Register Init (74HC595 on SPI1) ---
  // This sets up SPI1 and deselects all rows
  sr595_init();
  Serial.println("Shift registers initialized. All rows deselected.");

  // --- Analog Switch GPIO Init ---
  // This sets ISPP, VP, CC1-3 to LOW (safe state)
  array_gpio_init();
  Serial.println("Analog switches initialized. All safe state.");

  // --- Integrator components init ---
  integrator_init();
  Serial.println("Integrator module initialized. RESET pins are LOW, ready to accumulate.");

  Serial.println("\nSetup complete.\n");
  hardwareInitialized = true;

}

// ============================================================
// --- SETUP ---
// Setting up the initial system. This is what gets called first
// ============================================================
void setup() {
  Serial.begin(115200); // baud rate
  while (!Serial && millis() < 3000);  // Wait for Serial Monitor (up to 3s)
  Serial.println("=== AlScN Memristor Array Ready ===");

  pinMode(PIN_PU, OUTPUT);
  digitalWriteFast(PIN_PU, HIGH);
  Serial.println("System Initialized. Pin 32 default state: HIGH.");
  Serial.println("Awaiting 'on' command to pull LOW...");



}

// ============================================================
// -- MAIN LOOP --
// Main loop for the user interface and correct board setup
// ============================================================
void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    if (input.equalsIgnoreCase("on")) {
      digitalWriteFast(PIN_PU, LOW);
      armed = true;
      Serial.println("PIN_PU is now LOW. Now turn on physical 3.3V, then type 33.");
    }
    else if (input.equalsIgnoreCase("33")) {
      if (armed) {
        systemEnabled = true;
        if (!hardwareInitialized) {
          setup_hardware();
        }

        if (!hardwareInitialized) {
          Serial.println("Hardware setup did not complete successfully.");
          return;
        }

        Serial.println("3.3V confirmed ON. Board ready to run.");

        Serial.println("Choose a test to run.");
        print_test_menu();

      } else {
        Serial.println("Type 'on' first before typing 33.");
      }
    }
    else if (input.equalsIgnoreCase("off")) {
      
      digitalWriteFast(PIN_PU, HIGH);
      Serial.println("COMMAND RECEIVED: Pin 32 is now HIGH.");

      systemEnabled = false;
      armed = false;
      hardwareInitialized = false;

    } else if (systemEnabled) {

      String theinput = input;
      if (theinput.startsWith("PATCH,")) {
        run_patch_sanity_suite(theinput);

        print_test_menu();

      } else {
        int test_id = theinput.toInt();

        if (test_id >= TEST_SAFE_BOOT && test_id <= TEST_END) {
          run_test((uint8_t)test_id);

          print_test_menu();

        } else {
          Serial.println("Unknown command.");
        }
      } 
    }
  }

}