# Install the user interface and set the VM to use the UI mode by default
bash "install_gnome_gui" do
	user "root"
	code "yum groupinstall -y 'GNOME Desktop' 'Graphical Administration Tools'"
	action :run
end

bash "make_gui_default" do
	user "root"
	code "ln -sf /lib/systemd/system/runlevel5.target /etc/systemd/system/default.target"
	action :run
end
