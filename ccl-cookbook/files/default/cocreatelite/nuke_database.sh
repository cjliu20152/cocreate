#
# Author :: Patrick Dwyer <patricknevindwyer@gmail.com> 
# Author :: Alex Ethier <aethier@mitre.org>
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


#!/bin/sh
export DJANGO_SETTINGS_MODULE="cocreate.settings"
echo 'Deleting db.sqlite3'
rm ./db.sqlite3

echo 'Making new migrations'
./manage.py makemigrations

echo 'Running manage.py migrate'
./manage.py migrate

echo 'Creating superuser cocreate'
./manage.py createsuperuser --noinput --username cocreate --email=bkeyes@mitre.org

echo 'Setting cocreate password'
./setCoCreatePassword.py cocreate

echo 'Loading fixtures'
./manage.py loaddata cocreate/fixtures/sandbox_templates.json
