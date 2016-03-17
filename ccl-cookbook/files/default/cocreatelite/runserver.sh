#!/bin/sh
source /opt/cocreate/env/bin/activate
nohup /usr/local/bin/python3.4 /opt/cocreate/manage.py runserver 0.0.0.0:80 >> /var/log/cocreate/cocreate.log 2>&1
