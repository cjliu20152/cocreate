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
