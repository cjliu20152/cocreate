#
# Author :: Alex Ethier <aethier@mitre.org>
# Author :: Michael Joseph Walsh <github.com@nemonik.com>
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


from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from ..models import VMPlayground
from ..forms import VMPlaygroundForm, VMPlaygroundDescriptionForm, VMPlaygroundUserAccessForm, VMPlaygroundGroupAccessForm

from . import util
from ..util import single_user_mode

"""
View controllers for playground data
"""

@single_user_mode
def index(request):
    """
    Show the list of playgrounds for this user.
    """

    # determine all of the playgrounds this user has access to
    groupids = [group.id for group in request.user.groups.all()]
    print ("Group ids: " + str(groupids))
    playgrounds = VMPlayground.objects.filter(creator = request.user) | VMPlayground.objects.filter(access_users__id = request.user.id) | VMPlayground.objects.filter(access_groups__id__in = groupids)

    # determine all of the demo boxes from a set of playgrounds
    demos = []
    for playground in playgrounds:
        demos = demos + playground.getDemos()

    context = {
        "playgrounds": playgrounds,
        "demos": demos
    }

    return render(request, "playgrounds.html", util.fillContext(context, request))

@single_user_mode
def add(request):
    """
    Add a new playground.
    """
    if request.method == 'GET':
        form = VMPlaygroundForm()
    elif request.method == 'POST':
        form = VMPlaygroundForm(request.POST)

        if form.is_valid():
            # hooray, let's create the playground
            playground = VMPlayground.objects.create(
                name = form.data['name'],
                creator = request.user,
                description = form.data['description'],
                description_is_markdown = form.data.get('description_is_markdown', False),
                environment = form.data['environment'],
            )
            playground.save()
            return HttpResponseRedirect(reverse("playground", args=[playground.id]))
        else:
            pass

    opts = {"form": form}
    return render(request, "addPlayground.html", util.fillContext(opts, request))

@single_user_mode
def remove(request, playground_id):
    """
    Remove a playground.
    """

    playground = get_object_or_404(VMPlayground, pk = playground_id)

    for sandbox in playground.sandboxes.all():
        sandox.delete()

    playground.delete()

    return HttpResponseRedirect(reverse("playgrounds"))

@single_user_mode
def playground(request, playground_id):
    """
    Show the details for this playground.
    """
    playground = get_object_or_404(VMPlayground, pk = playground_id)
    opts = {"playground": playground}

    return render(request, "newPlaygroundDetails.html", util.fillContext(opts, request))

@single_user_mode
def alterUserAccess(request, playground_id):
    """
    Alter the access control list for a playground.
    """
    playground = get_object_or_404(VMPlayground, pk = playground_id)

    if request.method == 'GET':
        form = VMPlaygroundUserAccessForm(instance = playground)
    elif request.method == 'POST':
        form = VMPlaygroundUserAccessForm(request.POST, instance=playground)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("playground", args=[playground.id]))
        else:
            pass

    opts = {"form": form, "playground": playground }
    return render(request, "alterPlaygroundUserAccess.html", util.fillContext(opts, request))

@single_user_mode
def alterGroupAccess(request, playground_id):
    """
    Alter the access control list for a playground.
    """
    playground = get_object_or_404(VMPlayground, pk = playground_id)

    if request.method == 'GET':
        form = VMPlaygroundGroupAccessForm(instance = playground)
    elif request.method == 'POST':
        form = VMPlaygroundGroupAccessForm(request.POST, instance=playground)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("playground", args=[playground.id]))
        else:
            pass

    opts = {"form": form, "playground": playground }
    return render(request, "alterPlaygroundGroupAccess.html", util.fillContext(opts, request))

@single_user_mode
def editDesc(request, playground_id):
    """
    Alter or edit the description of the playground
    """

    playground = get_object_or_404(VMPlayground, pk = playground_id)

    if request.method == 'GET':
        form = VMPlaygroundDescriptionForm(instance = playground)
    elif request.method == 'POST':
        form = VMPlaygroundDescriptionForm(request.POST)

        if form.is_valid():
            playground.description_is_markdown = form.data['description_is_markdown']
            playground.description = form.data['description']
            playground.save()
            return HttpResponseRedirect(reverse("playground", args=[playground.id]))
        else:
            pass

    opts = {"form": form, "playground": playground }
    return render(request, "editPlaygroundDesc.html", util.fillContext(opts, request))
