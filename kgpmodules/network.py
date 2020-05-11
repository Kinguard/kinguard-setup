#!/usr/bin/env python3

import socket
import fcntl
import struct
import os

# https://stackoverflow.com/questions/2761829/python-get-default-gateway-for-a-local-interface-ip-address-in-linux
def _get_gateway_device():
	"""Read the default gateway directly from /proc."""
	with open("/proc/net/route") as fh:
		for line in fh:
			fields = line.strip().split()
			if fields[1] != '00000000' or not int(fields[3], 16) & 2:
				continue
			return fields[0]

# https://stackoverflow.com/questions/6243276/how-to-get-the-physical-interface-ip-address-from-an-interface
def _get_ip_address(iface):
	try:
		ifname=str.encode(iface[:15])
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(
			s.fileno(),
			0x8915,  # SIOCGIFADDR
			struct.pack('256s', ifname)
		)[20:24])
	except OSError:
		return("Unknown")

def listnetifs():
	ifs = []
	base = "/sys/class/net"
	devs = os.listdir( base )
	gwdev = _get_gateway_device()
	for dev in devs:
		ifs.append(["%s (%s)" %(dev,_get_ip_address(dev)), dev, dev == gwdev])

	return ifs
