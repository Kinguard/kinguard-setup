#!/usr/bin/env python3

from functools import partial
import subprocess
import threading
import pathlib
import urwid
import time
import json
import os


from kgpmodules import disks, misc, network as net
from kgpmodules.widgets import *

basedir = str(pathlib.Path(__file__).parent.absolute())

palette = [
	('banner', 'black', 'light gray'),
	('streak', 'black', 'dark red'),
	('bg', 'black', 'dark blue'),]

def exit_on_q(key):
	if key in ('q', 'Q'):
		raise urwid.ExitMainLoop()

class App:

	def __init__(self):
		# Check correct version
		os = misc.osInfo()
		#if os["ID"] not in ("debian", "raspbian") or os["VERSION_CODENAME"]!="buster":
		#	print("Only Debian Buster/Raspbian supported atm.")
		#	exit(1)
	
		# For local testing
		if os["ID"] != "ubuntu" or os["VERSION_CODENAME"]!="focal":
			print("Only Debian Buster supported atm.")
			exit(1)
	
		# Currently supported architectures armhf, arm64 and amd64
		arch = misc.getArch()
		if arch not in ("armhf", "arm64", "amd64"):
			print("Currently unsupported architecture: "+arch)
			exit(1)
		
		netifs = net.listnetifs()
		if len(netifs) == 0:
			print("No suitable network device found!")
			exit(1)
	
	
		dsks = disks.listdisks()
		if len(dsks) == 0:
			print("No suitable storage device found!")
			exit(1)
	
		self.thread = None

		self.selwin = SelectWindow(
			netifs, dsks, 
			self._showconfirm, 
			self._terminate)

		self.startwin = StartWindow(self._showwait, self._showselect)
		self.wait = WaitWindow("Please wait, install in progress")
		self.info = InfoWindow("Installation done. System needs to reboot to complete.", "Reboot", self._terminate) 
	
		self.loop = urwid.MainLoop(self.selwin, palette, unhandled_input=exit_on_q)

	def run(self):
		self.loop.run()
		if self.thread:
			self.thread.join()
	
	def _showconfirm(self):
		self.net = self.selwin.getNetif()
		self.dsk = self.selwin.getDisk()
		self.part = disks.defaultpartition(self.dsk)
		
		self.startwin.update(self.dsk, self.net)

		self.loop.widget = self.startwin

	def _showselect(self):
		self.loop.widget = self.selwin

	def _showreboot(self):
		self.loop.widget = self.info

	def _showwait(self):
		#print("Wait")
		self.loop.widget = self.wait
		self.thread = threading.Thread(target=self._dosetup)
		self.thread.start()
		#print("Done")

	def _terminate(self):
		raise urwid.ExitMainLoop()

	def _dosetup(self):
		cfg = {}
		cfg["default"] = {
			"storagedevice": self.dsk, 
			"storagepartition": self.part,
			"networkdevice" : self.net
		}

		print(json.dumps(cfg, indent=4))
		op = subprocess.check_output([basedir+"/scripts/test.sh"]).decode("utf-8")
		#print("Output was: "+op)
		time.sleep(5)
		self._showreboot()
		self.loop.draw_screen()

if __name__ == "__main__":

	if os.geteuid() != 0:
		print("You need root privileges to run this")
		exit(1)

	app = App()

	app.run()
