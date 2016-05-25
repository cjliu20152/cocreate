#!/bin/sh

#
# Author :: Michael Joseph Walsh <github.com@nemonik.com>
#
# --------------------------------------------------------
#                          NOTICE
# --------------------------------------------------------
#
# This software was produced for the U. S. Government
# under Basic Contract No. W56KGU-15-C-0010, and is
# subject to the Rights in Noncommercial Computer Software
# and Noncommercial Computer Software Documentation
# Clause 252.227-7014 (FEB 2012)
#
# (c) 2016 The MITRE Corporation.  All rights reserved
#
# See LICENSE for complete terms.
#
# --------------------------------------------------------
#
# Public release case number 15-3259.
#

#
# install VBox Guest Additions
#

ln -s /usr/src/kernels/$(uname -r)/include/generated/uapi/linux/version.h /lib/modules/$(uname -r)/build/include/linux/version.h

mkdir /tmp/virtualbox
VBOX_VERSION=$(cat /home/vagrant/.vbox_version)
KERN_DIR=/usr/src/kernels/`uname -r`
MAKE='/usr/bin/gmake -i'
mount -o loop /home/vagrant/VBoxGuestAdditions_$VBOX_VERSION.iso /tmp/virtualbox
sh /tmp/virtualbox/VBoxLinuxAdditions.run
cat /var/log/vboxadd-install.log
umount /tmp/virtualbox
rm -R /tmp/virtualbox
rm /home/vagrant/*.iso
