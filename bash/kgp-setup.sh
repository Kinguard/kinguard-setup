#! /bin/bash

#! /bin/bash -x
#
# Typical usage: wget https://www.kinguardproject.org/download/dev/setup/kgp-setup.sh -qO - | sh
#


echo "Kinguard setup script"
SEED="kgp.preseed"
REPO="kgp-tmp.list"
KEY="kinguard-keyring_1.0_all.deb"

DPKG="/usr/bin/dpkg"
APT="/usr/bin/apt"
BINS="${DPKG} ${APT}"

ARCHS="amd64 arm64 armhf"

DISTS="debian raspbian"
DIST_CODENAMES="buster"

BOOTPKGS="kinguard nextcloud21"

DLS="${SEED} ${REPO} ${KEY}"
SERVER="https://www.kinguardproject.org/download/dev/setup/"

KGP_HOME="/tmp/kgp-setup/"

echo "Checking preconditions"

if [ ! -e /etc/os-release ]
then
	echo "Missing os information file"
	exit
fi

for BIN in ${BINS}
do
	if [ ! -x ${BIN} ]
	then
		echo "Missing Debian tool: (${BIN})"
		exit;
	fi
done

# Check OS
source /etc/os-release
SUP_DIST=0
for DIST in ${DISTS}
do
	if [ ${DIST} = ${ID} ]
	then
		SUP_DIST=1
	fi
done

if [ $SUP_DIST -eq 0 ]
then
	echo "Currently unsupported distribution: ${ID}"
	exit
fi

echo "Running supported distribution ${ID}"

# Check version
SUP_CODENAME=0
for CODE in ${DIST_CODENAMES}
do
	if [ ${CODE} = ${VERSION_CODENAME} ]
	then
		SUP_CODENAME=1
	fi
done

if [ $SUP_CODENAME -eq 0 ]
then
	echo "Currently unsupported version: ${VERSION_CODENAME}"
	exit
fi

echo "Running supported version ${VERSION_CODENAME}"


# Check architecture
THISARCH=$(${DPKG} --print-architecture)
SUP_ARCH=0
for ARCH in ${ARCHS}
do
	if [ $ARCH = $THISARCH ]
	then
		SUP_ARCH=1
	fi
done

if [ ${SUP_ARCH} -eq 0 ]
then
	echo "Currently unsupported architecture: ${THISARCH}"
	exit
fi

echo "Running on supported arch ${THISARCH}"


# Check root
if [ `id -u` != 0 ]
then
	echo "You need to be root to run this"
	sudo $0 $@
	exit
fi

# Make sure apt is up2date
apt-get -q -y update

dpkg -l wget 2> /dev/null 1>&2 || apt-get install wget

echo "Setting up temp storage"
rm -rf ${KGP_HOME}
mkdir -p ${KGP_HOME}

exec 2>> /tmp/kgp-install.txt

cd ${KGP_HOME}

for DL in ${DLS}
do
	echo "Download: ${SERVER}${DL}"
	wget -q "${SERVER}${DL}"
done

echo "Installing kinguard keyring"
dpkg -i "${KGP_HOME}${KEY}"

echo "Preseeding install"

debconf-set-selections < "${KGP_HOME}${SEED}"

echo "Setup temporary apt sources"

cp ${KGP_HOME}${REPO} /etc/apt/sources.list.d/

echo "Starting installation"

export DEBIAN_FRONTEND=noninteractive

apt-get -q -y -o Dpkg::Options::="--force-confnew" install ${BOOTPKGS}

echo "Clean up setup environment"

rm -f /etc/apt/sources.list.d/${REPO}
rm -rf ${KGP_HOME}

echo "Setup should be completed. Please reboot to finalize install"
