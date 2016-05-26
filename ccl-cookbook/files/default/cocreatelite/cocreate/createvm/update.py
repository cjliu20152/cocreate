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


#update.py
#a test callback function for testing createvm.py
def updateProgress(rq, percent, message, *url):
        print("Current progress for " + rq + ": " + str(percent) + "%, " + message)
