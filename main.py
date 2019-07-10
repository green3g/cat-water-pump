from tplink_smarthome.plug import TPLinkSmartPlug
from time import sleep
from gpiozero import MotionSensor
from signal import pause
from threading import Timer
import subprocess
from os import getpid

# Simple command
#subprocess.call([
#		'/bin/systemd-notify',
#		'--pid=' + str(getpid()),
#		'WATCHDOG=1'
#	], shell=True)

SENSOR_PIN = 4
TIMEOUT = 5

device = TPLinkSmartPlug(host='192.168.0.159', connect=True)
pir = MotionSensor(SENSOR_PIN)

from threading import Timer

class Watchdog:
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self

class SmartPlugMotionDevice(object):
	def __init__(self, pir, device):
		self.timer = None
		self.pir = pir
		self.device = device
		pir.when_motion = self.activate
		pir.when_no_motion = self.deactivate

	def activate(self):
		print('Motion detected, activating device')
		self.cancel()
		self.device.turn_on()
		
	def deactivate(self):
		print('No motion, deactivating device')
		self.timer = Timer(TIMEOUT, self._deactivate)
		self.timer.start()
		print(f'Timer started for {TIMEOUT} seconds')
	
	def _deactivate(self):
		self.device.turn_off()
		self.timer = None
		
	def cancel(self):
		if self.timer:
			print('Canceling existing timer')
			self.timer.cancel()
			self.timer = None
	
if __name__ == '__main__':
	motion_device = SmartPlugMotionDevice(pir, device)
	
	pause()




