from django.contrib import admin
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

from .models import SandboxRequest, PlaygroundRequest, SandboxTemplate, Notification, VMSandbox, VMPlayground

admin.site.register(VMSandbox)
admin.site.register(VMPlayground)

@admin.register(SandboxRequest)
class SandboxRequestAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('playground_name', 'sandbox_name', 'requested_by', 'justification')
        }),
        
        ("Configure", {
            'fields': ('sandbox_lifetime', 'template_name')
        }),
        
        ("Approve/Disapprove", {
            'fields': ('request_status',)
        })
    )
    
    exclude = ("sandbox",)
    readonly_fields = ("playground_name", "template_name", "sandbox_name", "sandbox", "requested_by", "justification")
    
    def template_name(self, inst):
        """
        Retrieve the template name through a few redirects
        """
        return inst.template.name
        
    def playground_name(self, inst):
        """
        Retrieve the playground name through a few redirects
        """
        
        return inst.sandbox.playground.name
    
    list_display = ("playground_name", "sandbox_name", "sandbox_lifetime", "template_name", "request_status")
    list_display_links = ("sandbox_name",)
    list_editable = ("request_status",)
    
    def save_model(self, request, obj, form, change):
        """
        We're passing the object through, but we also want to send an email
        to the requestor.
        """
        obj.save()
        
        # pull out the requestor email
        owner_email = obj.requested_by.email
        
        sandbox_request_uri = request.build_absolute_uri(reverse('sandbox-details', args=(obj.id,)))
        
        if 'request_status' in form.changed_data:
            error = False
            if obj.request_status == 'err':
                error = True
            n = Notification(owner=obj.requested_by,
                             msg='Administrator changed request status to ' + obj.get_request_status_display(),
                             related_model_type='srq',
                             related_model_id=obj.id,
                             object_name=obj.sandbox_name,
                             error=error)
            n.save()
        
        # compose and send
        if owner_email != "":
            admin_email = "no-reply@mitre.org"
            if len(settings.ADMINS) > 0:
                admin_email = settings.ADMINS[0][1]
                
            # send the mail
            send_mail(
                "Your Sandbox request has been updated!",
                "You can view your Sandbox request at " + sandbox_request_uri,
                admin_email,
                [owner_email],
                html_message = get_template("sandboxRequestToUser.html").render(Context({"sandbox_request_uri": sandbox_request_uri}))
            )
        
@admin.register(PlaygroundRequest)
class PlaygroundRequestAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'requested_by', 'justification')
        }),
                
        ("Approve/Disapprove", {
            'fields': ('request_status',)
        })
    )
    
    readonly_fields = ("name", "requested_by", "justification")
    
    list_display = ("name", "requested_by", "request_status")
    list_editable = ("request_status", )
    
@admin.register(SandboxTemplate)
class SandboxTemplateAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'recipe', 'version')
        }),
    )
    
    list_display = ("name", "version", "recipe", )
    list_editable = ("name", "version", "recipe", )    