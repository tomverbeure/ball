
# RP2040 instructions

## MicroPython

* Install on RP2040: [Drag and Drop MicroPython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython)

    * Press BOOTSEL button while plugging in RP 2040
    * Drag and drop MicroPython UF2 intro RP 2040 folder
    * RP 2040 will automatically reboot and MicroPython should be up and running

* Connect to RP 2040 over serial port

    * `sudo screen /dev/ttyACM0` (quit with CTRL-A K)

* Open all permissions on `/dev/ttyACM*`

    * Create file `/dev/udev/rules.d/50-myusb.rules` with just 1 line: `KERNEL=="ttyACM[0-9]*",MODE="0666"`
    * This is the big hammer approach, taken from 
      [here](https://askubuntu.com/questions/58119/changing-permissions-on-serial-port). The alternative
      with using group permissions (`sudo adduser tom dialout` didn't work for whatever reason...)
    * You should now be able to do `screen /dev/ttyACM0`    

* Using the serial console (`screen`), check that you can toggle the RP2040 LED. Cut and paste
  the following into the console:

    ```python
import time
from machine import Pin

led = Pin(25, Pin.OUT)

while True:
    led.toggle()
    time.sleep(0.5)
    ```
    
* Install [`ampy`](https://github.com/scientifichackers/ampy). It allows you to 
  copy scripts to MicroPython:

    `pip3 install --user adafruit-ampy`

* Copy `main.py`, which contains the LED blinking code, to the RP2040:

    `ampy -p /dev/ttyACM0 put main.py`

    The LED should start blinking immediately, also after plugging in the RP2040.
    However, you can't connect anymore with the serial console...

* To stop main.py from running, you need to erase the flash completely, and then reinstall
  MicroPython. You erase the flash by uploading 'flash_nuke.uf2'.

* To run a script from the command line without starting automatically after rebooting, do:

    `ampy -p /dev/ttyACM0 run test.py`

  `test.py` can be any name as long as it's not `main.py` or `boot.py`.

    

