#
# Author :: Patrick Dwyer <patricknevindwyer@gmail.com> 
# Author :: Alexander Ethier <aethier@mitre.org>
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


#!/bin/bash

{
source env/bin/activate
python3.4 manage.py migrate
} || {
python3.4 manage.py migrate
} || {
python3.4 manage.py syncdb --noinput
python3.4 manage.py migrate
} || {
python3.4 manage.py makemigrations
python3.4 manage.py migrate
} || {
python3.4 manage.py -h
python3.4 manage.py migrate
}
exit 0
