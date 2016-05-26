#
# Author :: Patrick Dwyer <patricknevindwyer@gmail.com> 
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


from ..models import UserConfig
from ..forms import AwsForm
from ..forms import ProxyForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from . import util

from ..util import single_user_mode

@single_user_mode
def proxy(request):

    http_conf = UserConfig.objects.findOrCreate_ProxyHttp(request.user)
    https_conf = UserConfig.objects.findOrCreate_ProxyHttps(request.user)
    opts = { "http_proxy": http_conf, "https_proxy": https_conf }
    return render(request, "proxy.html", util.fillContext(opts, request))

@single_user_mode
def edit_proxy(request):

    http_conf = UserConfig.objects.findOrCreate_ProxyHttp(request.user)
    https_conf = UserConfig.objects.findOrCreate_ProxyHttps(request.user)

    if request.method == 'GET':
        form = ProxyForm(initial={"http_proxy": http_conf.val, "https_proxy": https_conf.val })
    elif request.method == 'POST':
        form = ProxyForm(request.POST, initial={"http_proxy": http_conf.val, "https_proxy": https_conf.val })

        if form.is_valid():
            print (form.cleaned_data['http_proxy'])
            print (form.cleaned_data['https_proxy'])

            http_conf.val = form.cleaned_data['http_proxy']
            https_conf.val = form.cleaned_data['https_proxy']

            http_conf.save()
            https_conf.save()
            return HttpResponseRedirect(reverse("proxy"))
        else:
            pass

    opts = {"form": form, "http_proxy": http_conf, "https_proxy": https_conf }
    return render(request, "editProxy.html", util.fillContext(opts, request))


@single_user_mode
def awsKey(request):

    conf = UserConfig.objects.findOrCreate_AwsKey(request.user)
    opts = {"awspublic": conf }
    return render(request, "awsKey.html", util.fillContext(opts, request))

@single_user_mode
def edit_awsKey(request):

    public_conf = UserConfig.objects.findOrCreate_AwsKey(request.user)
    private_conf = UserConfig.objects.findOrCreate_AwsSecret(request.user)


    if request.method == 'GET':
        form = AwsForm(initial={"aws_public": public_conf.val, "aws_secret": private_conf.val})
    elif request.method == 'POST':
        form = AwsForm(request.POST, initial={"aws_public": public_conf.val, "aws_secret": private_conf.val})

        if form.is_valid():
            print (form.cleaned_data['aws_public'])
            print (form.cleaned_data['aws_secret'])

            public_conf.val = form.cleaned_data['aws_public']
            private_conf.val = form.cleaned_data['aws_secret']

            public_conf.save()
            private_conf.save()
            return HttpResponseRedirect(reverse("awskey"))
        else:
            pass

    opts = {"form": form, "awspublic": public_conf, "awssecret": ""}
    return render(request, "editAwsKey.html", util.fillContext(opts, request))
