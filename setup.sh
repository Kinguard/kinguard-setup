#! /bin/bash

export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true
export LC_ALL=C LANGUAGE=C LANG=C

cp -a skeleton/* /

dpkg -i data/kinguard-keyring_1.0_all.deb

debconf-set-selections < data/kgp.preseed

apt update && apt -y upgrade

apt -y purge exim4 exim4-base exim4-config exim4-daemon-light

apt -y install kinguard

# Cleanup
rm /etc/apt/sources.list.d/kgp-tmp.list
rm /etc/apt/preferences.d/kgp-pin-installer.pref
touch /etc/opi/firstboot

/usr/share/opi-postsetup/kgp-postsetup

reboot
