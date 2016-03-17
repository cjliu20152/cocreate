#
# Copyright (c) 2016, The MITRE Corporation. All rights reserved.
# See LICENSE for complete terms.
#

#
# A shell script to provision the base image for Vagrant
#
# @author Michael Joseph <github.com@nemonik.com>
#

sed -i "s/^.*requiretty/#Defaults requiretty/" /etc/sudoers

# update and install RPMs
yum -y update
yum -y install kernel-devel-`uname -r` gcc  dkms make  perl bzip2 wget nano

# configure vagrant
mkdir -pm 700 /home/vagrant/.ssh
curl -L https://raw.githubusercontent.com/mitchellh/vagrant/master/keys/vagrant.pub -o /home/vagrant/.ssh/authorized_keys
chmod 0600 /home/vagrant/.ssh/authorized_keys
chown -R vagrant:vagrant /home/vagrant/.ssh

# install VBox Guest Additions
VBOX_VERSION=$(cat /home/vagrant/.vbox_version)
mount -o loop /home/vagrant/VBoxGuestAdditions_$VBOX_VERSION.iso /mnt
sh /mnt/VBoxLinuxAdditions.run
umount /mnt
cat  /var/log/vboxadd-install.log

# cleanup
yum -y clean all
rm -rf /home/vagrant/VBoxGuestAdditions_*.iso
rm -rf /tmp/rubygems-*

