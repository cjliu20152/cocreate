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


from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse

from ..models import SshKey, Repository
from ..forms import SshKeyForm, RepositoryForm

from . import util
from ..util import single_user_mode

"""
View controllers for user profile data.
"""

@single_user_mode
def index(request):
    return render(request, "profile.html", util.fillContext({}, request))

@single_user_mode
def sshkeys(request):
    return render(request, "profile.html", util.fillContext({"showSshKeys": False}, request))

@single_user_mode
def repositories(request):
    return render(request, "profile.html", util.fillContext({"showRepositories": False}, request))
    
@single_user_mode
def addRepository(request):
    """
    Add a GIT repository for this user
    """
    if request.method == 'GET':
        form = RepositoryForm()
    elif request.method == 'POST':
        form = RepositoryForm(request.POST)
        
        if form.is_valid():
            # hooray, let's create the playground
            repo = Repository.objects.create(
                name = form.data['name'],
                uri = form.data['uri'],
                creator = request.user
            )
            repo.save()
            return HttpResponseRedirect(reverse("profile-repositories", args=[]))
        else:
            pass
            
    opts = {"form": form}
    return render(request, "addRepository.html", util.fillContext(opts, request))

@single_user_mode
def removeRepository(request, repository_id):
    repo = Repository.objects.get(pk=repository_id)
    if repo.creator == request.user:
        repo.delete()
    
    return HttpResponseRedirect(reverse("profile-repositories", args=[]))
        
@single_user_mode
def addSshKey(request):
    if request.method == 'GET':
        form = SshKeyForm()
    elif request.method == 'POST':
        form = SshKeyForm(request.POST)
        
        if form.is_valid():
            # hooray, let's create the playground
            sshkey = SshKey.objects.create(
                name = form.data['name'],
                key = form.data['key'],
                user = request.user
            )
            sshkey.save()
            return HttpResponseRedirect(reverse("profile-sshkeys", args=[]))
        else:
            pass
            
    opts = {"form": form}
    return render(request, "addSshKey.html", util.fillContext(opts, request))

@single_user_mode
def removeSshKey(request, sshkey_id):
    sshkey = SshKey.objects.get(pk=sshkey_id)
    print ("Starting removal of SSH Key")
    if sshkey.user == request.user:
        sshkey.delete()
        print ("SSH Key deleted!")
    else:
        print ("SSH Key and User mismatch!")
    
    return HttpResponseRedirect(reverse("profile-sshkeys", args=[]))
    