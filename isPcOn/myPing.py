 
#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os
import sys
import threading
import time

################################################
#
# Create web site
#
class Ping(object):
	"""
	Define IP address to ping and interval between ping.
	Give the result.
	"""
	def __init__(self, ip, delay):
		self._ip = ip
		self._delay = delay
		self._isOn = 0
		self.start()
	def _get_isOn(self):
		return(self._isOn)
	def _set_isOn(self, newStatus):
		self._isOn = newStatus
	isOn = property(	fget = _get_isOn, 
						fset = _set_isOn, 
						doc = "1 or 0" )
	def _get_ip(self):
		return(self._ip)
	ip = property(	fget = _get_ip, 
						#fset = _set_isOn, 
						doc = "IP address to ping" )
	def _get_delay(self):
		return(self._delay)
	delay = property(	fget = _get_delay, 
						#set = _set_isOn, 
						doc = "Time interval betwenn each ping, in seconds" )
	def _get_status(self):
		if (self._isOn == 1):
			return('ON')
		else:
			return('OFF')
	status = property(	fget = _get_status, 
						doc = "On or Off" )
						
	def start(self):
		pingReader = readPing(self)
		pingReader.start()
		time.sleep(1)				# 1 second at start, time to have the first data
		
class readPing(threading.Thread):
	"""
	Do the ping.
	"""
	def __init__(self, Ping): 
		threading.Thread.__init__(self)
		self.setDaemon(True)
		self._ping = Ping
        
	def run(self):
		while True:
			response = os.system("ping -c 1 " + self._ping.ip + " >> /dev/null")
			if (response == 0):
				self._ping.isOn = 1
			else :
				self._ping.isOn = 0
			time.sleep(self._ping.delay)

################################################
#
# Example
#
if __name__ == '__main__':
	mp = Ping("192.168.1.5", 20)
  	while 1:
		print(mp.ip + ' ' + mp.status)
		time.sleep(30)
