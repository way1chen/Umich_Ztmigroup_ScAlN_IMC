# ScAlN Ferroelectric In-memory Computing array 




Raspberry Pi

Make sure to do sudo poweroff before disconnecting the shell. 

Use nano as the text editor for code.

Setting up:

- Clone the repo
- On Arduino IDE, File -> Preferences and paste link: https://www.pjrc.com/teensy/package_teensy_index.json
- On package manager download Teensy 4.1
- Connect to teensy port and recognize which COM# port you are connected to
- Go to teensycom.py and set MNIST dataset download to True
- Change the port number to your COM#
- pip install -r requirements.txt in terminal
- Run teensycom.py
