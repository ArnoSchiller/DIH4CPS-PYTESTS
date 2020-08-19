"""
LEDRing: This class controls the LED ring connected via arduino nano. 
            Running this script will start a loop which activates and 
            deactivates the LED every few secounds.  

Requirements:
- RPi.GPIO: pip install Jetson.GPIO

@authors:   Arno Schiller (AS)
@email:     schiller@swms.de
@version:   v0.0.1
@license:   ...

VERSION HISTORY
Version:    (Author) Description:                                           Date:
v0.0.1      (AS) First initialize. Added functions to activate/deactivate   19.08.2020\n
                the LED ring by setting GPIO to HIGH or LOW.                          \n
"""


import RPi.GPIO as GPIO
import time

class LEDRing:
    # Pin Definitions
    ledring_pin = 18  # BOARD pin 12, BCM pin 18
    
    def __init__(self):
        # Pin Setup:
        # Board pin-numbering scheme
        GPIO.setmode(GPIO.BCM)
        # set pin as an output pin with optional initial state of HIGH
        GPIO.setup(self.ledring_pin, GPIO.OUT, initial=GPIO.HIGH)

    def activate(self):
        GPIO.output(self.ledring_pin, GPIO.HIGH)
        time.sleep(0.5)

    def deactivate(self):
        GPIO.output(self.ledring_pin, GPIO.LOW)


    # vllt für den destruktor: GPIO.cleanup()

def testLoop():
    led = LEDRing()
    sleep_time = 2
    number_loops = 10
    counter = 0
    while counter <= number_loops:
        led.activate()
        time.sleep(sleep_time)
        led.deactivate()
        time.sleep(sleep_time)
        counter += 1

if __name__ == '__main__':
    testLoop()
