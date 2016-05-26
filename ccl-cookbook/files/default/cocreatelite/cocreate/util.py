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


from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import UserConfig, VMPlayground

DEFAULT_DESCRIPTION = """
## Welcome to CoCreate:Lite

All of your VM instances in CoCreate:Lite are organized into __Playgrounds__ and __Sandboxes__. A
_Sandbox_ is an individual Virtual Machine running a specific application or suite of tools. A group
of _Sandboxes_ is organized into a _Playground_.

This is your default __Playground__, a good place to start. You can add more _Playgrounds_ as you need;
each _Playground_ is meant to be a collection of components that together form an Application or Service.

For more details, check the [help section](/help)
"""

def single_user_mode(function=None):
    """
    Decorator for enabling single user mode throughout the code base.
    """
    def _dec(view_func):
        def _view(request, *args, **kwargs):

            # force into single user autenticated mode
            if not request.user.is_authenticated():
                # make sure a user exists
                if len(User.objects.filter(username = "default")) <= 0:
                    user = create_single_user()

                # authenticate the user
                user = authenticate(username="default", password="default")
                login(request, user)

                print ("logged in the default user")

            # slip stream the config top level mcguffin
            request.has_aws_key = has_aws_key

            # pass on the results of the view function
            return view_func(request, *args, **kwargs)

        # snip ourselves out of the inspection hierarchy
        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    return _dec(function)

def create_single_user():
    """
    Create all the bits and pieces we need for the default user.
    """

    # basic user object
    user = User.objects.create_user("default", "default@localhost", "default")

    print ("Created default user")

    # add an AWS key stub configuration item
    awskey = UserConfig.objects.findOrCreate_AwsKey(user)

    # add a default Playground
    vmp = VMPlayground.objects.create(
        name = "Default Playground",
        creator = user,
        description = DEFAULT_DESCRIPTION,
        description_is_markdown = True,
        environment = "awsp"
    )
    vmp.save()

    print ("Created default playground")

    return user

def has_aws_key():
    awskey = UserConfig
    return False
