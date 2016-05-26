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


from django.shortcuts import render
from . import util
from ..util import single_user_mode
from ..models import VMPlayground

@single_user_mode
def index(request):
    """
    Index page for the user.

    The index is the primary view into the world for everyone. We need to gather some details
    on which Playgrounds (and sandboxes) are available for this user. This depends on the
    role of the user.

    We also include relevant group messages.
    """
    opts = {}

    # find the default playground for this user
    ps = VMPlayground.objects.filter(creator = request.user)
    opts['playground'] = ps[0]

    # we need to determine which playgrounds the user can see, which we handle by a
    # foreign key or wildcard (depending on user role)
    return render(request, "index.html", util.fillContext(opts, request))

@single_user_mode
def help(request):
    """
    Toss up the help screen
    """
    return render(request, "help.html", util.fillContext({}, request))
