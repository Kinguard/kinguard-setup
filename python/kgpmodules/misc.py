#! /usr/bin/env python3

import subprocess

def getArch():
	arch = subprocess.check_output(["dpkg","--print-architecture"])
	return arch.decode("utf-8").rstrip()

def osInfo():
	ret = {}
	f = open("/etc/os-release")
	for line in f:
		key,val = line.rstrip().split("=")
		ret[key] = val

	return ret


def main():
	info=osInfo()

	for key in info:
		print("%s:%s" % (key, info[key]))

	print("Architecture is " + getArch())

if __name__ == "__main__":
	main()
