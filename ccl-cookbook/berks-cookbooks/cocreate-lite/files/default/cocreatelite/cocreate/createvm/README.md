# CreateVM Library
The CreateVM library is a collection of scripts that support the creation and Chef bootstrapping of VMware Virtual Machines.
## Required Tools: 
-	pyVmomi- Python API for VMware (https://github.com/vmware/pyvmomi)
-	knife 
-	knife vsphere- knife plugin for vSphere (https://github.com/ezrapagel/knife-vsphere)

## Included Scripts
-	createvm.py
o	This contains the functions for cloning the base VM and bootstrapping the new VM.
-	pyvmutils.py
o	This script (from the pyVmomi github) contains utility functions for working with pyVmomi
-	update.py
o	This contains a callback function to use when testing createvm.
-	createvm.config
o	This contains the blank configuration file for the createvm script (the configuration in use on the dev server is in /opt/chef-tools/createvm/createvm.config). 

## Installation Instructions
To set up the createVM library on a new server:
1.	Install Chef and configure knife.
2.	Install knife vsphere.
3.	Install Python 3.4
4.	Install pyVmomi.
5.	Add the createvm folder to your path (or add it to a folder already on the path).  

## Interacting with worker.py
Currently, worker.py is running as a background process. When worker.py is running, if a new approved sandbox request is in the database, the createVM function is called.  If sandboxes aren't being created as expected, here are some troubleshooting tips:
-	Make sure worker.py is running: to see if worker.py is running, run ‘ps x’ and look for the python3 worker.py process.  If the process is not there, you can restart the process by running ‘nohup python3 –u worker.py test 2>&1 &’ from the folder where worker.py is located.
-	Check for unexpected errors: it is possible that an unexpected error occurred that stopped worker.py.  You can use the output of the script to try to determine what went wrong. To read the output of the worker.py script, run ‘tail –f nohup.out’ in the folder where the worker.py is located.  
-	Restart worker.py: If the worker.py process appears to be running but isn’t behaving correctly, kill the worker.py process and restart it.

## Deleting Sandboxes
To delete a sandbox, you need to delete the sandbox VM and delete the client and node in Chef.  You can do all three of these things by running ‘knife vsphere vm delete <name> -purge’.  You may also need to include the folder by adding ‘-f “Scan VMs/CoCreate Test”’.
