#! /usr/bin/env python3

import os
import subprocess

def _sizeof_fmt(num, suffix='B'):
	for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
		if abs(num) < 1024.0:
			return "%3.1f%s%s" % (num, unit, suffix)
		num /= 1024.0
	return "%.1f%s%s" % (num, 'Yi', suffix)

def _getdisks():
	disks = []
	base = "/sys/class/block"
	devs = os.listdir( base )
	for dev in devs:
		devstr = base+"/"+dev
		# Skip partitions
		if os.path.isfile(base+"/"+dev+"/partition"):
			continue
		disks.append(dev)
	return disks


def _getdiskname(path):
	#/sys/class/block/mmcblk0/device/name
	name = "N/A"
	try:
		if os.path.isfile(path+"/device/model"):
			fpath = path+"/device/model"
		elif os.path.isfile(path+"/device/name"):
			fpath = path+"/device/name"	
		else:
			return name

		f = open(fpath)
		name = f.readline().rstrip()
		f.close()
	except FileNotFoundError:
		pass 
	return name

def _getdiskmeta(disk):
	meta = {}
	meta["syspath"] = "/sys/class/block/"+disk;
	meta["devpath"] = "/dev/"+disk;

	meta["isphysical"] = os.path.islink(meta["syspath"]+"/device")

	if meta["isphysical"]:
		meta["model"] = _getdiskname(meta["syspath"])
	else:
		meta["model"] = "Virtual device"

	f = open(meta["syspath"]+"/size")
	meta["blocks"] = int(f.readline())
	meta["size"] = _sizeof_fmt(meta["blocks"]*512)
	f.close()

	f = open(meta["syspath"]+"/removable")
	meta["removable"] = int(f.readline())>0
	f.close()

	return meta


class Disks:
	def __init__(self):
		self.disks = {}
		self.diskdevs = _getdisks()
		root = self._getrootdisk()

		for disk in self.diskdevs:
			self.disks[disk] = _getdiskmeta(disk)
			self.disks[disk]["isroot"] = disk == root

	def __iter__(self):
		return self.disks.__iter__()

	def __getitem__(self, key):
		return self.disks[key]

	def _getrootdisk(self):
		lines = subprocess.check_output(["mount"]).decode("utf-8").split("\n")
		part = ""
		for line in lines:
			items = line.split()
			if len(items) == 0 or items[2] != "/":
				continue
			part = items[0]
	
		if part == "":
			return ""
	
		# Find which on which disk partition is 
		for disk in self.diskdevs:
			if "/dev/"+disk in part:
				return disk
		return ""


def defaultpartition(disk):
	if disk[:2] == "sd":
		return "1"

	return "p1"


def listdisks():

	devs = Disks()
	retval = []

	# Find a candidate install-device
	biggest = {}
	for dev in devs:
		disk = devs[dev]
		# Skip removable, virtual and root devices
		if disk["removable"] or not disk["isphysical"] or disk["isroot"] :
			continue

		if not biggest or disk["blocks"] > devs[biggest]["blocks"]:
			biggest = dev

	for dev in devs:
		disk = devs[dev]
		# Skip removable, virtual and root devices
		if disk["removable"] or not disk["isphysical"] or disk["isroot"] :
			continue

		retval.append(["%s, %s (%s)" %(disk["model"], disk["size"], disk["devpath"]), dev , dev==biggest])
	
	return retval

