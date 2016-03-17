cocreate_directory = node['cocreatelite']['install_location']

bash "remove_cocreatelite_directory" do
    code "rm -rf " + cocreate_directory
    action :run
end

remote_directory "/opt/cocreate" do
    source "cocreatelite"
    owner node['cocreatelite']['default_user']
end

# Make the default user the owner and give them write access to the db.sqlite3 file
#file cocreate_directory + "db.sqlite3" do 
#	owner node['cocreatelite']['default_user']
#	mode 0755
#	action :create
#end

# Git is required for berkshelf to pull in dependencies
package "git"  do
  action :install
end

bash "install_cocreate_dependencies" do
    code "pip3.4 install -r requirements.txt"
    user node['cocreatelite']['default_user']
    cwd "/opt/cocreate"
    action :run
end

# Fix permissions for migrate script.
file "/opt/cocreate/migrate.sh" do
    mode '0755'
    owner node['cocreatelite']['default_user']
end

# Apply Django Migrations.
bash "apply_django_migrations" do
    code "./migrate.sh"
    user node['cocreatelite']['default_user']
    cwd "/opt/cocreate"
    action :run
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

# Add codev to known hosts.
cookbook_file "/root/.ssh/known_hosts" do
    source "known_hosts"
    mode "0644"
    owner node['cocreatelite']['default_user']
end

# Add service script to manage CoCreate:lite
cookbook_file "/etc/init.d/cocreate" do
    source "ops/cocreate"
    mode "0755"
    owner node['cocreatelite']['default_user']
end

# Add service script to manage omnibusd
cookbook_file "/etc/init.d/omnibusd" do
    source "ops/omnibusd"
    mode "0755"
    owner node['cocreatelite']['default_user']
end

# Start up cocreate as a service
service "cocreate" do
    action [ :enable, :start ]
end

# Start up omnibusd as a service
service "omnibusd" do
    action [ :enable, :start ]
end

service "iptables" do
  action [ :disable, :stop ]
end
