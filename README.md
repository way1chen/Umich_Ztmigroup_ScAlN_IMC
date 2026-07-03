# ScAlN IMC GUI

This project is centered on a PySide6 desktop GUI for interacting with an MCU over serial.

The app lets you:

- connect to a serial device,
- submit 20x20 grayscale images for image processing,
- submit 20x20 grayscale images for classification,
- view returned processed images and classification confidence values.

## What The GUI Does

The GUI has three main pages:

1. Connect
2. Image Processing
3. Image Classification

### Connect Page

Use this page to select and open a serial port.

- Choose a detected port.
- Click connect.
- Connection state is shown in the top bar.

### Image Processing Page

Use this page to:

- load or draw an image,
- select a processing mode,
- submit the image to the MCU,
- view the processed output image returned by firmware.

Input and output are both 20x20 grayscale payloads (400 bytes).

### Image Classification Page

Use this page to:

- load or draw an image,
- submit for classification,
- view 10 returned confidence scores (digits 0 through 9).

## Running The GUI

From [GUI](GUI):

```bash
python3 -m pip install -r requirements.txt
python3 -m main
```

Main entry points:

- [GUI/main.py](GUI/main.py)
- [GUI/gui/main_application.py](GUI/gui/main_application.py)
- [GUI/gui/core/serial_manager.py](GUI/gui/core/serial_manager.py)

## Serial Protocol Used By The GUI

The GUI sends these request formats:

- Processing: `PROCESS\n<MODE>\n<400 raw bytes>`
- Classification: `CLASSIFY\n<400 raw bytes>`

Expected firmware responses:

- Processing success: `OK|400\n` + 400 bytes output image
- Classification success: `OK\n` + one CSV line containing 10 float values
- Error: `ERROR:<message>\n`

## How To Use The Firmware Files In /firmware

The folder [GUI/firmware](GUI/firmware) contains a ready-to-adapt reference implementation for the GUI protocol.

### Files

1. [GUI/firmware/serial_manager.h](GUI/firmware/serial_manager.h)
2. [GUI/firmware/example.cpp](GUI/firmware/example.cpp)

### What They Provide

- A non-blocking serial parser for `PROCESS` and `CLASSIFY` commands.
- Payload framing for fixed 400-byte image transfers.
- Standardized response helpers (`OK`, `OK|400`, and `ERROR`).
- Virtual hooks you can override for your own processing and classifier logic.

### Typical Firmware Integration Flow

1. Copy [GUI/firmware/serial_manager.h](GUI/firmware/serial_manager.h) into your MCU project.
2. Use [GUI/firmware/example.cpp](GUI/firmware/example.cpp) as a template.
3. Subclass `SerialManager` and implement:
   - `onProcessImage` (or mode-specific `onBlurLight`, `onBlurHeavy`, `onSharpen`)
   - `onClassifyImage`
4. Keep image size at exactly 400 bytes.
5. Ensure classification response always returns 10 comma-separated floats.
6. Run `update()` continuously in your `loop()`.

## Example PlatformIO Firmware

A runnable example project is included in the sibling folder [GUI_test/platformio.ini](../GUI_test/platformio.ini), with matching protocol files in:

- [GUI_test/src/serial_manager.h](../GUI_test/src/serial_manager.h)
- [GUI_test/src/main.cpp](../GUI_test/src/main.cpp)

Use that example if you want a quick known-good firmware target for GUI testing.

## Troubleshooting

- Connect works but submit fails:
  Ensure the flashed firmware actually implements the GUI protocol (`PROCESS` / `CLASSIFY`).
- Unexpected header errors:
  Verify firmware response framing exactly matches `OK|400` for processing and `OK` + CSV for classification.
- Classification parse errors:
  Return exactly 10 valid float values separated by commas.
- Image payload errors:
  Keep payload at 20x20 grayscale = 400 bytes.

## Dependencies

Python dependencies are listed in [GUI/requirements.txt](GUI/requirements.txt):

- PySide6
- pyserial
