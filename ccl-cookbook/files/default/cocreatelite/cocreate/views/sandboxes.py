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


"""
View controllers for sandbox creation/modification/etc
"""

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, resolve
from django.conf import settings
from django.utils.six.moves.urllib.parse import urlparse

from ..models import VMPlayground, VMSandbox, Repository

from . import util

from ..util import single_user_mode

import requests
import json

from .api import aws_create, stop_instance, start_instance, terminate_instance


@single_user_mode
def details(request, playground_id, sandbox_id):
    """
    Retrieve details on the given sandbox
    """
    sandbox = get_object_or_404(VMSandbox, pk = sandbox_id)
    
    opts = {"sandbox": sandbox, "playground" : sandbox.playground}
    
    return render(request, "newSandboxDetails.html", util.fillContext(opts, request))
    
@single_user_mode
def add(request, playground_id):
    """
    Depending on the type of playground, route the proper add sandbox form
    
    # VMSandbox Model
    
    The sandbox request will end up filling in the VMSandbox object, with the
    following information:
    
        name
        logical_name - generated
        creator
        created_at - auto
        playground
        metadata - JSON payload for creation
        keys - associated pub key objects
    """
    playground = get_object_or_404(VMPlayground, pk = playground_id)
    
    opts = {"playground": playground}
    
    if request.method == "GET":
        # select the properly instrumented form for sandbox request
        if playground.environment in ["aws", "awsp"]:
            return render(request, "addSandboxAWS.html", util.fillContext(opts, request))
        elif playground.environment == "isee":
            return render(request, "addSandboxISEE.html", util.fillContext(opts, request))
        else:
            return JsonResponse({"error": True, "msg": "Unknown deployment environment encountered"})
    else:
        # process the response into a sane object in the DB, and then respond for reroute
        if playground.environment in ["aws", "awsp"]:
            
            instance_id = aws_create(request, playground)
            print("instance_id  " + instance_id)
    
            # basic sandbox object
            sandbox = VMSandbox.objects.create(
                name = request.POST['name'],
                logical_name = util.generateLogicalName(request.POST['name']),
                creator = request.user,
                playground = playground,
                metadata = getAllMetadata(instance_id, request.POST, ['recipe', 'ami', 'sshKey', 'subnet', 'vpc', 'type', 'secGroups[]', 'name'])
            )
            
            if request.POST['repository']:
                repo = Repository.objects.get(pk = request.POST['repository'])
                sandbox.repository = repo

            sandbox.save()         

            if hasattr(settings, 'CHEF_CONTROLLER_URL') and not settings.CHEF_CONTROLLER_URL:
                # send out our request
                sandbox_req = requests.post(settings.CHEF_CONTROLLER_URL + "/create", data=json.loads(sandbox.metadata))    

                return JsonResponse({"error": not sandbox_req.status_code == 200})
            else:
                return JsonResponse({})
            
        elif playground.environment == "isee":
            
            sandbox = VMSandbox.objects.create(
                name = request.POST['name'],
                logical_name = util.generateLogicalName(request.POST['name']),
                creator = request.user,
                playground = playground,
                metadata = filterPOSTToJSON(request.POST, ['recipe', 'sshKey', 'name'])
            )
            
            if request.POST['repository']:
                repo = Repository.objects.get(pk = request.POST['repository'])
                sandbox.repository = repo
            sandbox.save()
            
            # pass the request to the Queueing backend

            return JsonResponse({"error": False})
        else:
            print("playground.environment not handled", flush=True)
            return JsonResponse({"error": True, "msg": "Unknown deployment environment encountered"})

@single_user_mode
def pause(request, playground_id, sandbox_id):
    """
    Pause the VM
    """
    
    # Get the sandbox
    sandbox = get_object_or_404(VMSandbox, pk = sandbox_id)
    instanceId = sandbox.awsInstanceId()
    
    # Pause the box
    stop_instance(request, instanceId)
    
    # Pause the model
    sandbox.pause()
    
    return chooseRedirect(request, playground_id, sandbox_id)

@single_user_mode
def start(request, playground_id, sandbox_id):
    """
    Start the VM
    """
    
    # Get the sandbox
    sandbox = get_object_or_404(VMSandbox, pk = sandbox_id)
    instanceId = sandbox.awsInstanceId()
    
    # Start the box
    start_instance(request, instanceId)
    
    # Start the model
    sandbox.start()
    
    return chooseRedirect(request, playground_id, sandbox_id)

@single_user_mode
def reboot(request, playground_id, sandbox_id):
    """
    Reboot the VM
    """
    sandbox = get_object_or_404(VMSandbox, pk = sandbox_id)
    
    #sandbox.reboot()
    
    return chooseRedirect(request, playground_id, sandbox_id)


@single_user_mode
def delete(request, playground_id, sandbox_id):
    """
    Remove the VM - InstanceId stored in the metadata.awsid field
    """
    
    # Get the sandbox
    sandbox = get_object_or_404(VMSandbox, pk = sandbox_id)
    instanceId = sandbox.awsInstanceId()
    sandbox_name = sandbox.name

    playground = get_object_or_404(VMPlayground, pk = playground_id)
    playground_name = playground.name
   
    # Terminate the box
    terminate_instance(request, instanceId, playground_name, sandbox_name)
    
    # Terminate the model
    sandbox.delete()
    
    return HttpResponseRedirect(reverse("playground", args=[playground_id]))


@single_user_mode
def toggleDemo(request, playground_id, sandbox_id):
    """
    Toggle the demo state of the box
    """
    sandbox = get_object_or_404(VMSandbox, pk = sandbox_id)
    
    sandbox.is_demo = not sandbox.is_demo
    sandbox.save()
    
    return chooseRedirect(request, playground_id, sandbox_id)

def chooseRedirect(request, playground_id, sandbox_id):
    """
    Determine whether we redirect to the playground detail or sandbox detail
    """
    next = request.META.get('HTTP_REFERER', None) or None
    
    redirectToPlayground = True
    
    if next is not None:
        match = resolve(urlparse(next)[2])
        
        if match is not None:
            if match.view_name.startswith("sandbox"):
                redirectToPlayground = False
    
    if redirectToPlayground:
        return HttpResponseRedirect(reverse("playground", args=[playground_id]))
    else:
        return HttpResponseRedirect(reverse("sandbox-details", args=[playground_id, sandbox_id]))
    
    
    
"""
Utility methods
"""
def filterPOSTToJSON(body, fields):
    """
    Extract a post body by field name into a sane format for JSON dump
    """
    filtered = {}
    for k in fields:
        fk = k
        if k.endswith('[]'):
            fk = k[:-2]
            filtered[fk] = body.getlist(k)
        else:
            filtered[fk] = body[k]
    return json.dumps(filtered)


# we can probably find a better way to do this, but when creating an AWS sandbox, make sure the id gets added to the metadata

def getAllMetadata(instance_id, body, fields):
    filtered = {}
    for k in fields:
        fk = k
        if k.endswith('[]'):
            fk = k[:-2]
            filtered[fk] = body.getlist(k)
        else:
            filtered[fk] = body[k]
    filtered['dns'] = {
        "PrivateDnsName": "",
        "PublicDnsName": ""
    }
    filtered['ip'] = {
        "PrivateIpAddress": ""
    }
    filtered['sshkeyname'] = ""
    
    filtered['awsid'] = instance_id
    return json.dumps(filtered)
