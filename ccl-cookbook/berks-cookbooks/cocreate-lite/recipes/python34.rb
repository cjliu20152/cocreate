# Installs Python 3.4

remote_file "/var/tmp/Python-3.4.3.tar.xz" do
	source "https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz"
end

# zlib, zlib-devel, openssl, openssl-devel are required for pip.  sqlite and sqlite-devel are required for django framework.
package ["zlib", "zlib-devel", "openssl", "openssl-devel", "sqlite", "sqlite-devel"]  do
  action :install
end

bash "extract_python" do
    code "tar xvf /var/tmp/Python-3.4.3.tar.xz -C /usr/local/src/"
    action :run
end

bash "configure_python" do
	cwd "/usr/local/src/Python-3.4.3"
	code "./configure --prefix=/usr/local"
	action :run
end

bash "make_python" do
	cwd "/usr/local/src/Python-3.4.3"
	code "make && make install"
	action :run
end

# Only required for root user
# Append /usr/local/bin to root's path
cookbook_file "/etc/profile.d/path.sh" do
	source "path.sh"
	action :create
end

