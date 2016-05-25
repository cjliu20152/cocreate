#
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


#!/usr/bin/env python
import django
import sys
from django.contrib.auth.models import User

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('Enter a password to be set')
        sys.exit(1)
    django.setup()
    user = User.objects.get(username='cocreate')
    user.set_password(sys.argv[1])
    user.save()
