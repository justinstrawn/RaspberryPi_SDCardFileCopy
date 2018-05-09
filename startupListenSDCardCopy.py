# Justin Strawn 2018

import os, sys, time, math;

import RPi.GPIO as GPIO
import dbus;
import subprocess;
import hashlib;
import shutil;

def pinOutput(pinNumber, outputValue):
	GPIO.output(pinNumber, outputValue);

def pinSetupOutput(pinNumber):
	GPIO.setup(pinNumber, GPIO.OUT)
	pinOutput(pinNumber, GPIO.LOW)
	
def pinSetupInput(pinNumber):
	GPIO.setup(pinNumber, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	
def pinInput(pinNumber):
	return GPIO.input(pinNumber)
	
	
pin_ledActivity = 36
pin_ledErrorActivity = 32
pin_switchAutoActivity = 40

IOD01 = None;
IOD02 = None;

def Setup():
	GPIO.setwarnings(True);
	GPIO.setmode(GPIO.BOARD) # Numbers GPIOs by physical location
	pinSetupOutput(pin_ledActivity);
	pinSetupOutput(pin_ledErrorActivity);
	pinSetupInput(pin_switchAutoActivity);

def Destroy():
	pinOutput(pin_ledActivity, GPIO.LOW)
	pinOutput(pin_ledErrorActivity, GPIO.LOW)
	GPIO.cleanup();

def Shutdown():
	print "Shutting Down";
	Destroy();
	commd = "sudo shutdown --no-wall -P now";
	os.system(commd);
	

def activityBlinkSlow(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.HIGH);
	time.sleep(0.4);
	pinOutput(pinNumber, GPIO.LOW);

def activityBlinkFast(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.HIGH);
	time.sleep(0.1);
	pinOutput(pinNumber, GPIO.LOW);
	
def activityBlinkFastOff(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.LOW);
	time.sleep(0.1);
	pinOutput(pinNumber, GPIO.HIGH);
	
def activityBlinkVeryFastOff(pinNumber=pin_ledActivity):
	pinOutput(pinNumber, GPIO.HIGH);
	time.sleep(0.001);
	pinOutput(pinNumber, GPIO.LOW);
	
def activityBlinkSuccess(pin=pin_ledActivity):
	for i in range(0,8):
		activityBlinkFast();
		time.sleep(0.1);
		
def activityBlinkMiniSuccess(pin=pin_ledActivity):
	for i in range(0,4):
		activityBlinkFast();
		time.sleep(0.1);
		
def activityBlinkMiniSuccessOff(pin=pin_ledActivity):
	for i in range(0,4):
		activityBlinkFastOff();
		time.sleep(0.1);
		
def activityBlinkError(msg=None):
	if msg:
		print "[SDCC] [ERROR]", msg;
	for i in range(0,4):
		activityBlinkFast(pin_ledErrorActivity);
		time.sleep(0.3);

def commandOutput(commd):
	o = subprocess.Popen(commd.split(" "), stdout=subprocess.PIPE,stderr=subprocess.PIPE);
	sout,eout = o.communicate();
	return str(sout)+str(eout);
	
def canReadDir(dir):
	# raspbian hacks
	try:
		os.listdir(dir);
	except:
		return False;
	if "permission denied" in commandOutput("ls -d "+dir).lower():
		return False;
	return True;
	
def getIODeviceList():
	dir_base_medias = ["/media/pi/"]; 
	vs = [];
	for dir_base_media in dir_base_medias:
		v =  [dir_base_media+x+"/" for x in os.listdir(dir_base_media) if not x.startswith(".") and os.path.isdir(dir_base_media+x) and not x.lower() == "pi"];
		v2 = [];
		for i in v:
			if canReadDir(i):
				v2.append(i);
		vs = vs + v2;
	return vs;
	
def resetIODFound():
	global IOD01, IOD02;
	IOD01 = None;
	IOD02 = None;

def verifyIOD(device):
	return True;

def getSwitchAutoActivity():
	return pinInput(pin_switchAutoActivity);
	
def md5file(fname):
	hash_md5 = hashlib.md5();
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
				hash_md5.update(chunk);
	return hash_md5.hexdigest();



def Loop():
	global IOD01, IOD02;
	activityBlinkSuccess(pin_ledErrorActivity);
	activityBlinkSuccess();
	
	while 1:
		time.sleep(1);
		
		while not getSwitchAutoActivity():
			print "[SDCC] Waiting for auto activity switch to turn on";
			pinOutput(pin_ledActivity, GPIO.LOW)
			pinOutput(pin_ledErrorActivity, GPIO.HIGH)
			time.sleep(2);
			continue;
			
		pinOutput(pin_ledActivity, GPIO.LOW)
		pinOutput(pin_ledErrorActivity, GPIO.LOW)
		
		while IOD01 == None or IOD02 == None:
			activityBlinkVeryFastOff();
			time.sleep(1);
			IODeviceList = getIODeviceList();
			if len(IODeviceList) <= 0:
				print "[SDCC] Still waiting for first device";
				continue;
				
			if IOD01 == None:
				if len(IODeviceList) == 1:
					IOD01 = IODeviceList[0];
					print "[SDCC] found first device, setting: ", IOD01;
					activityBlinkMiniSuccessOff();
				else:
					activityBlinkError(msg="IOD01 is none but more than one device! Resetting.." + str(IODeviceList));
					resetIODFound();
				continue;
			
			elif IOD02 == None:
				if len(IODeviceList) <= 1:
					print "[SDCC] Still waiting for seco device";
					continue;
				
				if len(IODeviceList) == 2:
					if IOD01 == IODeviceList[0]:
						IOD02 = IODeviceList[1];
						print "[SDCC] found second device, setting: ", IOD02;
						activityBlinkMiniSuccessOff();
					elif IOD01 == IODeviceList[1]:
						IOD02 = IODeviceList[0];
						print "[SDCC] found second device, setting: ", IOD02;
						activityBlinkMiniSuccessOff();
					else:
						activityBlinkError(msg="About to set IOD02 but IOD01 no longer found!" + str(IODeviceList));
						resetIODFound();
				else:
					activityBlinkError(msg="IOD02 is none but more than two devices! " + str(IODeviceList));
					resetIODFound();

				continue;
		
		if not verifyIOD(IOD01) or not verifyIOD(IOD02):
				activityBlinkError(msg="Verify failed");
				resetIODFound();
				continue;
				

		
		ident_time = time.time();
		
		print "[SDCC] Looping through files", IOD01, IOD02;
		files_source = {};
		for x in [x for x in os.listdir(IOD01) if not x.startswith(".")]:
			if os.path.isdir(IOD01+x):
				continue;
				
			x_dest = x;
			ext = x[::-1];
			ext = ext[:ext.find(".")];
			ext = ext[::-1];

			if os.path.isfile(IOD02+x):
				md51 = md5file(IOD01+x);
				md52 = md5file(IOD02+x);
				if md51 == md52:
					print "[SDCC] FOUND SAME FILE, SKIPPING";
					continue;
				else:
					x_dest = x.replace("."+ext,"")+"_"+str(int(ident_time))+"."+ext;
				
			files_source[IOD01+x] = IOD02+x_dest;
		
		print "[SDCC] Copying files";
		pinOutput(pin_ledActivity, GPIO.HIGH);
		for file_source, file_dest in files_source.items():
			print "[SDCC] copying file ", file_source, " ->", file_dest;
			shutil.copy(file_source, file_dest);
			activityBlinkVeryFastOff();
			
			
		print "[SDCC] Verifying files";
		for file_source, file_dest in files_source.items():
			if not os.path.isfile(file_dest):
				activityBlinkError(msg="No file verify " + file_source + "/" + file_dest);
			else:
				pass;
			pass;
			
			
		print "[SDCC] Success..";
		pinOutput(pin_ledActivity, GPIO.LOW);
			
		activityBlinkSuccess();
		activityBlinkSlow();
		
		pinOutput(pin_ledActivity, GPIO.LOW);
		
		time.sleep(1);

		Shutdown();
		break;


if __name__ == '__main__':
	Setup()

	try:
		Loop();
	except KeyboardInterrupt:
		Destroy()
		
