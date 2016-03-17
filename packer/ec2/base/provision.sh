#!/bin/sh

#
# Copyright (c) 2016, The MITRE Corporation. All rights reserved.
# See LICENSE for complete terms.
#

#
# Shell script to provision the CoCreate:lite base AMI..
#
#
# @author: Michael Joseph Walsh <github.com@nemonik.com>
#

# sleep makes sure that the OS properly initializes.
sleep 30

# update and install dependencies for what follows
yum update
yum groupinstall -y 'development tools'
yum install -y wget curl tar git nano make gcc rsync cloud-init oprofile

## install Python-3.4.3
## NOTE: might not be necessary
#wget https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz -O /var/tmp/Python-3.4.3.tar.xz
#tar xvf /var/tmp/Python-3.4.3.tar.xz -C /usr/local/src
#cd /usr/local/src/Python-3.4.3
#./configure --prefix=/usr/local
#make
#make altinstall
#
## adding Python-3.4.3 paths to default .bash_profile and update root's .bash_profile
#echo "export PATH=/usr/local/lib/python3.4/site-packages:/usr/local/bin:$PATH" >> /etc/skel/.bash_profile
#yes | cp /etc/skel/.bash_profile /root/.bash_profile
#source /root/.bash_profile

# patch cloud-init config
#sed -i.bak 's/.*name: centos.*/name: ec2-user/g' /etc/cloud/cloud.cfg
sed -i.bak /etc/cloud/cloud.cfg -e 's/name: centos/name: ec2-user/'

# https://github.com/mitchellh/packer/issues/185
rm /root/.ssh/authorized_keys

# disable iptables
/etc/init.d/iptables stop
service iptables save
chkconfig iptables off

# disable selinux
echo 0 > /selinux/enforce
#sed -i '/SELINUX=enforcing/c\SELINUX=permissive' /etc/selinux/config
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

# I think that's it...
