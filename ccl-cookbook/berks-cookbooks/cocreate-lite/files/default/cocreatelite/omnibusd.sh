#!/bin/sh
source /opt/cocreate/env/bin/activate
nohup /usr/local/bin/python3.4 /opt/cocreate/manage.py omnibusd >> /var/log/cocreate/omnibusd.log 2>&1
