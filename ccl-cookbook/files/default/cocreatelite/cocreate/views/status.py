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


"""
View controllers for sandbox creation/modification/etc
"""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, resolve
from django.conf import settings

from ..models import VMPlayground, VMSandbox, Repository

from . import util

import redis
R = redis.StrictRedis(host="0.0.0.0", port=6379)
    
@login_required
def index(request):
    
    # pull together some stats
    opts = {
        "playgrounds": VMPlayground.objects.all(),
        "sandboxes": VMSandbox.objects.all(),
        "repositories": Repository.objects.all(),
        "scanners": getScannerStatus(),
        "services": getServicesStatus()
    }
    
    return render(request, "status.html", util.fillContext(opts, request))

def getServicesStatus():
    """
    Check on the service status for various components.
    """
    results = []
    
    try:
        R.ping()
        results.append({"name": "Redis", "exists": True})
    except:
        results.append({"name": "Redis", "exists": False})
    
    return results
    
def getScannerStatus():
    
    scanners = {
        "Ping": "scanner-status-ping"
    }
    
    results = []
    
    for scanner in scanners.items():
        exists = False
        try:
            exists = R.exists(scanner[1])
        except:
            exists = False
        
        res = {
            "name": scanner[0],
            "key": scanner[1],
            "exists": exists
        }
        results.append(res)
            
    return results
