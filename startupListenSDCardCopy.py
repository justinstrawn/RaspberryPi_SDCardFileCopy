import os, sys, time, math;

import RPi.GPIO as GPIO

def pinOutput(pinNumber, outputValue):
	GPIO.output(pinNumber, outputValue);

def pinSetupOutput(pinNumber):
	GPIO.setup(pinNumber, GPIO.OUT)   # Set LedPin's mode is output
	pinOutput(pinNumber, GPIO.LOW)
	
def pinSetupInput(pinNumber):
	GPIO.setup(pinNumber, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
def pinInput(pinNumber):
	return GPIO.input(pinNumber)
	
	
pin_ledActivity = 12
pin_ledErrorActivity = 22
pin_switchAutoActivity = 16

IOD01 = None;
IOD02 = None;

def Setup():
	GPIO.setmode(GPIO.BOARD) # Numbers GPIOs by physical location
	pinSetupOutput(pin_ledActivity);
	pinSetupOutput(pin_ledErrorActivity);
	pinSetupInput(pin_switchAutoActivity);

def Destroy():
	pinOutput(pin_ledActivity, GPIO.LOW)
	pinOutput(pin_ledErrorActivity, GPIO.LOW)
	GPIO.cleanup();

def Shutdown():
	Destroy();
	

def activityBlinkSlow(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.HIGH);
	time.sleep(1.2);
	pinOutput(pinNumber, GPIO.LOW);

def activityBlinkFast(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.HIGH);
	time.sleep(0.2);
	pinOutput(pinNumber, GPIO.LOW);
	
	
def activityBlinkVeryFastOff(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.LOW);
	time.sleep(0.001);
	pinOutput(pinNumber, GPIO.HIGH);
	
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

def getSwitchAutoActivity():
	return pinInput(pin_switchAutoActivity);

def Loop():
	
	print "[SDCC] [INFO] Startup..";
	activityBlinkSuccess(pin_ledErrorActivity);
	activityBlinkSuccess();
	
	
	while 1:
		time.sleep(1);
		
		while not getSwitchAutoActivity():
			pinOutput(pin_ledActivity, GPIO.LOW)
			pinOutput(pin_ledErrorActivity, GPIO.HIGH)
			continue;
			
		pinOutput(pin_ledActivity, GPIO.LOW)
		pinOutput(pin_ledErrorActivity, GPIO.LOW)
		
		while IOD01 == None or IOD02 == None:
			activityBlinkVeryFastOff();
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
				continue;
		
		files_source = {};
		# for dir+sourcefile
			# if destination has file:
				# if files are same:
					# skip
				#else
					# rename to _date
				
			# {source -> destination }
		
		pinOutput(pin_ledActivity, GPIO.HIGH);
		
		for file_source, file_dest in files_source.items():
			print "copying files ", file_source, " ->", file_dest;
			activityBlinkVeryFastOff();
			
		
		for file_source, file_dest in files_source.items():
			# verify file
			pass;
			
		pinOutput(pin_ledActivity, GPIO.LOW);
			
		activityBlinkSuccess();
		activityBlinkSlow();
		
		time.sleep(1);
		
		Shutdown();


if __name__ == '__main__':
	Setup()
	try:
		Loop();
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.

		Destroy()
