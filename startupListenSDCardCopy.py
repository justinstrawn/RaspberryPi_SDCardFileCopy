import os, sys, time, math;

import RPi.GPIO as GPIO

def pinOutput(pinNumber, outputValue):
	GPIO.output(pinNumber, outputValue);

def pinSetup(pinNumber):
	GPIO.setup(pinNumber, GPIO.OUT)   # Set LedPin's mode is output
	pinOutput(pinNumber, GPIO.LOW)

pin_ledActivity = 12
pin_ledErrorActivity = 22

IOD01 = None;
IOD02 = None;

def Setup():
	GPIO.setmode(GPIO.BOARD) # Numbers GPIOs by physical location
	pinSetup(pin_ledActivity);
	pinSetup(pin_ledErrorActivity);

def Destroy():
	pinOutput(pin_ledActivity, GPIO.LOW)
	pinOutput(pin_ledErrorActivity, GPIO.LOW)
	GPIO.cleanup();

def activityBlinkSlow(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.HIGH);
	time.sleep(1.2);
	pinOutput(pinNumber, GPIO.LOW);

def activityBlinkFast(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.HIGH);
	time.sleep(0.2);
	pinOutput(pinNumber, GPIO.LOW);
	
def activityBlinkSuccess(pin=pin_ledActivity):
	for i in range(0,12):
		activityBlinkFast();
		time.sleep(0.2);
		
def activityBlinkMiniSuccess(pin=pin_ledActivity):
	for i in range(0,4):
		activityBlinkFast();
		time.sleep(0.2);
		
def activityBlinkError(msg=None):
	if msg:
		print "[SDCC] [ERROR]", msg;
	for i in range(0,4):
		activityBlinkFast(pin_ledErrorActivity);
		time.sleep(0.5);

def getIODeviceList():
	return [];

def resetIODFound():
	pass;

def verifyIOD(device):
	return True;

def Loop():
	
	print "[SDCC] [INFO] Startup..";
	activityBlinkSuccess(pin_ledErrorActivity);
	activityBlinkSuccess();
	
	while 1:
		time.sleep(1);
		while IOD01 == None or IOD02 == None:
			time.sleep(1);
			IODeviceList = getIODeviceList();
			if len(IODeviceList) <= 0:
				print "[SDCC] [INFO] Still waiting for first device";
				continue;
				
			if IOD01 == None:
				if len(IODeviceList) == 1:
					IOD01 = IODeviceList[0];
					print "[SDCC] [INFO] found first device, setting: ", IOD01;
					activityBlinkMiniSuccess();
				else:
					activityBlinkError(msg="IOD01 is none but more than one device! Resetting.." + str(IODeviceList));
					resetIODFound();
				continue;
			
			elif IOD02 == None:
				if len(IODeviceList) <= 1:
					print "[SDCC] [INFO] Still waiting for seco device";
					continue;
				
				if len(IODeviceList) == 2:
					if IOD01 == IODeviceList[0]:
						IOD02 = IODeviceList[0];
						print "[SDCC] [INFO] found second device, setting: ", IOD02;
						activityBlinkMiniSuccess();
					elif IOD01 == IODeviceList[1]:
						IOD02 = IODeviceList[0];
						print "[SDCC] [INFO] found second device, setting: ", IOD02;
						activityBlinkMiniSuccess();
					else:
						activityBlinkError(msg="About to set IOD02 but IOD01 no longer found!" + str(IODeviceList));
						resetIODFound();
				else:
					activityBlinkError(msg="IOD02 is none but more than two devices! " + str(IODeviceList));
					resetIODFound();

				continue;
		
		if not verifyIOD(IOD01) or not verifyIOD(IOD02):
				activityBlinkError(msg="Verify failed " + str(IOD01) + "/" + str(IOD02) + " = " + str(verifyIOD(IOD01)) + "/" + str(verifyIOD(IOD02)) );
				resetIODFound();
		
		time.sleep(1);
		# shutdown


if __name__ == '__main__':
	Setup()
	try:
		Loop();
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
	finally:
		Destroy()
