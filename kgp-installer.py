#!/usr/bin/env python3

from functools import partial
import pathlib
import urwid
import json
import os


from kgpmodules import disks, misc, network as net
from kgpmodules.widgets import *

basedir = str(pathlib.Path(__file__).parent.absolute())

print("Basedir is: "+basedir)

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
	
	
		self.selwin = SelectWindow(
			netifs, dsks, 
			self._showconfirm, 
			self._terminate)
		self.startwin = StartWindow(self._createconfig, self._showselect)
	
		self.loop = urwid.MainLoop(self.selwin, palette, unhandled_input=exit_on_q)

	def run(self):
		self.loop.run()
	
	def _showconfirm(self):
		self.net = self.selwin.getNetif()
		self.dsk = self.selwin.getDisk()
		self.part = disks.defaultpartition(self.dsk)
		
		self.startwin.update(self.dsk, self.net)

		self.loop.widget = self.startwin

	def _showselect(self):
		self.loop.widget = self.selwin
	
	def _terminate(self):
		raise urwid.ExitMainLoop()

	def _createconfig(self):
		cfg = {}
		cfg["default"] = {
			"storagedevice": self.dsk, 
			"storagepartition": self.part,
			"networkdevice" : self.net
		}

		print(json.dumps(cfg, indent=4))

if __name__ == "__main__":

	if os.geteuid() != 0:
		print("You need root privileges to run this")
		exit(1)

	app = App()

	app.run()
