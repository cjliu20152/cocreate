#!/bin/sh

#
# Copyright (c) 2016, The MITRE Corporation. All rights reserved.
# See LICENSE for complete terms.
#

#
# Shell script to install underlying dependencies so Chef provisioning can work
#
#
# @author: Michael Joseph Walsh <github.com@nemonik.com>
#

# sleep makes sure that the OS properly initializes.
sleep 30

# update and install dependencies for what follows
yum update
yum groupinstall -y 'development tools'
yum install -y wget curl tar git nano make gcc rsync cloud-init

# patch cloud-init config
sed -i.bak /etc/cloud/cloud.cfg -e 's/name: centos/name: ec2-user/'

# https://github.com/mitchellh/packer/issues/185
rm /root/.ssh/authorized_keys

# disable iptables
/etc/init.d/iptables stop
service iptables save
chkconfig iptables off

# disable selinux
echo 0 > /selinux/enforce
sed -i '/SELINUX=enforcing/c\SELINUX=disabled' /etc/selinux/config

# configure the network interface
cat > /etc/sysconfig/network-scripts/ifcfg-eth0 << EOF
TYPE=Ethernet
DEVICE=eth0
ONBOOT=yes
BOOTPROTO=dhcp
NM_CONTROLLED=no
PERSISTENT_DHCLIENT=1
EOF

echo "NOZERCONF=yes" >> /etc/sysconfig/network

# don't require tty
sed -i.bak /etc/sudoers -e 's/^.*requiretty/#Defaults requiretty/'

# I think that's it...
