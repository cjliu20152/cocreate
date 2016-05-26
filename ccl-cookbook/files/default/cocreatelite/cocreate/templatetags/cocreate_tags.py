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


from django import template
from cocreate.models import SandboxRequest

register = template.Library()
   
@register.assignment_tag
def get_request_progress_display(percent_complete):
    if percent_complete == 100:
        return 'Completed'
    return str(percent_complete) + '%'

@register.assignment_tag
def get_progress_color(percent_complete):
    if percent_complete == 100:
        return 'black'
    return 'lightgreen'

@register.assignment_tag
def get_sandbox_id_from_request(request_id):
    request = SandboxRequest.objects.get(id=request_id)
    return request.sandbox.id
