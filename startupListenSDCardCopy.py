import os, sys, time, math;

import RPi.GPIO as GPIO



def pinOutput(pinNumber, outputValue):
	GPIO.output(pinNumber, outputValue);

def pinSetup(pinNumber):
	GPIO.setup(pinNumber, GPIO.OUT)   # Set LedPin's mode is output
	pinOutput(pinNumber, GPIO.LOW)

pin_ledActivity = 12

def Setup():
	GPIO.setmode(GPIO.BOARD) # Numbers GPIOs by physical location
	pinSetup(pin_ledActivity);

def Destroy():
	pinOutput(pin_ledActivity, GPIO.LOW)
	GPIO.cleanup();

def activityBlinkSlow():
	pinOutput(pin_ledActivity, GPIO.HIGH);
	time.sleep(1.2);
	pinOutput(pin_ledActivity, GPIO.LOW);

def activityBlinkFast()
	pinOutput(pin_ledActivity, GPIO.HIGH);
	time.sleep(0.2);
	pinOutput(pin_ledActivity, GPIO.LOW);
	
def activityBlinkFastMultiple()
	for i in range(0,8):
		activityBlinkFast();
		time.sleep(0.2);




if __name__ == '__main__':
  setup()
  try:
    loop();
  except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
    destroy()
