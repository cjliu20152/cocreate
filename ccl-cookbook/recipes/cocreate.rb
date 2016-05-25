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


bash "remove_cocreatelite_directory" do
    code "rm -rf " + node['cocreatelite']['install_location']
    action :run
end

remote_directory node['cocreatelite']['install_location'] do
    source "cocreatelite"
    owner node['cocreatelite']['default_user']
end

# Git is required for berkshelf to pull in dependencies
package "git" do
  action :install
end

package "python34" do
  action :install
end

package "python34-devel" do
  action :install
end

# install zeromq. package in the repo don't work
bash 'install_zeromq' do
    user 'root'
    cwd '/tmp'
    code <<-EOC
      yum -y install libtool gcc-c++ glib* unzip wget
      yum -y groupinstall "Development Tools"
      mkdir zeromq
      cd zeromq
      wget https://download.libsodium.org/libsodium/releases/libsodium-1.0.3.tar.gz
      tar -xvf libsodium-1.0.3.tar.gz
      cd libsodium-1.0.3
      ./configure
      make clean
      make
      make install
      echo "# Hello!!!!" >> /root/.bashrc
      echo 'export sodium_CFLAGS="-I/usr/local/include"' >> /root/.bashrc
      echo 'export sodium_LIBS="-L/usr/local/lib"' >> /root/.bashrc
      echo 'export CPATH=/usr/local/include' >> /root/.bashrc
      echo 'export LIBRARY_PATH=/usr/local/lib' >> /root/.bashrc
      echo 'export LD_LIBRARY_PATH=/usr/local/lib' >> /root/.bashrc
      echo 'export LD_RUN_PATH=/usr/local/lib' >> /root/.bashrc
      echo 'export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig' >> /root/.bashrc
      echo 'export CFLAGS="-I/usr/local/include"' >> /root/.bashrc
      echo 'export LDFLAGS="-L/usr/local/lib -lsodium"' >> /root/.bashrc
      source /root/.bashrc
      echo '/usr/local/lib' > tee -a /etc/ld.so.conf.d/libsodium.conf
      cd /tmp/zeromq/
      wget https://github.com/zeromq/libzmq/archive/master.zip
      unzip master.zip
      cd libzmq-master
      ./autogen.sh
      ./configure
      make clean
      make
      make install
      ldconfig
    EOC
end

bash 'install_cocreate' do
    user node['cocreatelite']['default_user']
    cwd node['cocreatelite']['install_location']
    code <<-EOH
        virtualenv --python=/usr/bin/python3.4 .env
        .env/bin/pip install -r requirements.txt
        .env/bin/python3.4 manage.py makemigrations
        .env/bin/python3.4 manage.py migrate
    EOH
end

# Fix permissions for migrate script.
file "/opt/cocreate/migrate.sh" do
    mode '0755'
    owner node['cocreatelite']['default_user']
end

# Clean cookbooks directory
bash "clean_cookbooks" do
    code "rm -rf /root/cookbooks"
    action :run
end

bash "clean_berkshelf" do
    code "rm -rf /root/.berkshelf"
    action :run
end

remote_directory "/root/cookbooks" do
    source "cookbooks"
    owner node['cocreatelite']['default_user']
end

bash "make_berkshelf_directory" do
    code "mkdir -p /root/.berkshelf"
    action :run
end

remote_directory "/root/.berkshelf/cookbooks" do
    source "cookbooks"
    owner node['cocreatelite']['default_user']
end

# Clean ssh directory
directory "ssh_dir" do
    path "/root/.ssh"
    recursive true
    action :delete
end

# Make ssh directory
directory "ssh_dir" do
    path "/root/.ssh"
    action :create
end

# Fix permissions for runserver script.
file "/opt/cocreate/runserver.sh" do
    mode '0755'
    owner node['cocreatelite']['default_user']
end

# Fix permissions for omnibusd script.
file "/opt/cocreate/omnibusd.sh" do
    mode '0755'
    owner node['cocreatelite']['default_user']
end

# Create log directory for systemd services to log to
directory '/var/log/cocreate' do
  owner 'root'
  group 'root'
  mode '0755'
  action :create
end

# execute 'systemctl daemon-reload on systemd unit install
execute 'systemd-reload' do
  command 'systemctl daemon-reload'
  action :nothing
end

cookbook_file '/etc/systemd/system/cocreate.service' do
  source 'cocreate.service'
  mode '664 '
  notifies :run, 'execute[systemd-reload]', :immediately
end

service 'cocreate' do
  provider Chef::Provider::Service::Systemd
  supports :status => true, :start => true, :stop => true, :restart => true
  action [ :enable, :start ]
end

#bash 'systemd_cocreate' do
#    user 'root'
#    code <<-EOH
#      systemctl daemon-reload
#      systemctl enable cocreate.service
#      systemctl start cocreate.service
#    EOH
#end


#Systemd omnibusd service file installation
cookbook_file '/etc/systemd/system/omnibusd.service' do
  source 'omnibusd.service'
  mode '664'
  notifies :run, 'execute[systemd-reload]', :immediately
end

#bash 'systemd_omnnibusd' do
#    user 'root'
#    code <<-EOH
#      systemctl daemon-reload
#      systemctl enable omnibusd.service
#      systemctl start omnibusd.service
#    EOH
#end

#execute 'systemd-reload' do
#  command 'systemctl daemon-reload'
#end
#
#execute 'start_cocreate' do
#  command 'systemctl start omnibusd.service'
#end

service 'omnibusd' do
  provider Chef::Provider::Service::Systemd
  supports :status => true, :start => true, :stop => true, :restart => true
  action [ :enable, :start ]
end

# Configure iptables
iptables_rule 'http' do
  action :enable
end

iptables_rule 'django-omnibus' do
  action :enable
end

bash 'open_ports_in_selinux' do
    user 'root'
    code <<-EOC
      semanage port -a -t http_port_t -p tcp 4242
    EOC
end
