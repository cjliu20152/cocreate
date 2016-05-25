#
# Author :: Alexander Ethier <aethier@mitre.org>
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


# Install vagrant and plugins

remote_file "/tmp/vagrant_1.8.1_x86_64.rpm" do
  source "https://releases.hashicorp.com/vagrant/1.8.1/vagrant_1.8.1_x86_64.rpm"
  action :create
end

rpm_package "vagrant" do
  source "/tmp/vagrant_1.8.1_x86_64.rpm"
  action :install
end

# Install gcc required for gem which vagrant plugins require.
package "gcc"  do
  action :install
end

# Install the required vagrant plugins and the dummy vagrant box
cookbook_file "/root/vagrant_plugin_install.sh" do
    source "vagrant_plugin_install.sh"
    mode "0755"
    owner node['cocreatelite']['default_user']
end

bash "Install vagrant plugins" do
    code "/root/vagrant_plugin_install.sh"
    user node['cocreatelite']['default_user']
    action :run
end

bash "add_dummy_box" do
    code "vagrant box add -f dummy https://github.com/mitchellh/vagrant-aws/raw/master/dummy.box"
    action :run
end
