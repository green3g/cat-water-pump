from tplink_smarthome.plug import TPLinkSmartPlug
from time import sleep
from gpiozero import MotionSensor
from signal import pause
from threading import Timer
import subprocess
from os import getpid	
import sdnotify

# Simple command
#subprocess.call([
#		'/bin/systemd-notify',
#		'--pid=' + str(getpid()),
#		'WATCHDOG=1'
#	], shell=True)

SENSOR_PIN = 4
TIMEOUT = 60
HOST_IP = '192.168.0.159'


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
		print('Activating device')
		self.cancel()
		self.device.connect()
		self.device.turn_on()
		self.device.close()
		print('Device activated')
		
	def deactivate(self, immediate=False):
		if immediate:
			self._deactivate()
			return
		print('Setting deactivation timer')
		self.timer = Timer(TIMEOUT, self._deactivate)
		self.timer.start()
		print(f'Timer started for {TIMEOUT} seconds')
	
	def _deactivate(self):
		print('Deactivating device')
		self.device.connect()
		self.device.turn_off()
		self.device.close()
		print('Device deactivated')
		self.timer = None
		
	def cancel(self):
		if self.timer:
			print('Canceling existing timer')
			self.timer.cancel()
			self.timer = None
	
if __name__ == '__main__':
	
	# initialization variables
	initialized = False
	device = None
	pir = None
	motion_device = None
	
	print("Test starting up...")
	pir = MotionSensor(SENSOR_PIN)
	
	while not initialized:
		try:
			device = TPLinkSmartPlug(host=HOST_IP)
			motion_device = SmartPlugMotionDevice(pir, device)
			print('Testing activation...')
			motion_device.activate()
			sleep(1)
			print('Testing deactivation...')
			motion_device.deactivate(immediate=True)
			print('Test successful!')
			initialized = True
		except:
			print('Network not up...')
			sleep(1)
	
	print("Test startup finished")

	# Inform systemd that we've finished our startup sequence...
	n = sdnotify.SystemdNotifier()
	n.notify("READY=1")

	count = 1
	while True:
		# print("Running... {}".format(count))
		n.notify("STATUS=Count is {}".format(count))
		count += 1
		sleep(2)



