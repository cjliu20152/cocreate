#
# Author :: Alex Ethier <aethier@mitre.org>
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

Vagrant.configure(2) do |config|

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
    vb.cpus = "1"
    vb.gui = true
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end

  config.vm.provider "vmware_fusion" do |vb|
    vb.gui = true
    vb.vmx["memsize"] = "1024"
    vb.vmx["numvcpus"] = "1"
    vb.vmx["vhv.enable"] = "TRUE"
  end

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
    config.cache.auto_detect = true
  end

  config.vm.network :private_network, ip: "192.168.2.2"

  config.vm.network "forwarded_port", guest: 80, host: 8081, protocol: "tcp", host_ip: '127.0.0.1'
  config.vm.network "forwarded_port", guest: 4242, host: 4242, protocol: "tcp", host_ip: '127.0.0.1'

#  config.vm.box="ngageoint/centos-7-2-1511"

  config.vm.box="packer/vagrant/centos-7-2-1511-x64-virtualbox.box"

  config.berkshelf.berksfile_path = "ccl-cookbook/Berksfile"
  config.berkshelf.enabled = true
  config.vm.synced_folder "ccl-cookbook/files/default", "/vagrant"
#  config.proxy.http = "PROXY_ADDRESS:PROXY_PORT"
#  config.proxy.https = "PROXY_ADDRESS:PROXY_PORT"

  config.vm.provision "chef_zero" do |chef|
    chef.cookbooks_path = "./ccl-cookbook"
    chef.add_recipe "cocreate-lite"
    chef.nodes_path = "/tmp"
    chef.log_level = :info
  end
end
