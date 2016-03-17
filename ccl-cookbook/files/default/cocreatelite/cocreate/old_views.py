from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.views.decorators.http import require_POST
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context
from .models import SandboxRequest, Sandbox, PlaygroundRequest, Playground, Notification, SandboxTemplate, SandboxAWSOptions, SshKey
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from .forms import SandboxRequestForm, PlaygroundForm, SshKeyForm
import random
import datetime
import json
import requests

def index(request):
    """
    Index page for the user. This should only be shown post login. If a user visits this page
    prior to login, they should be redirected to the login/register page. 
    
    The index is the primary view into the world for everyone. We need to gather some details
    on which Playgrounds (and sandboxes) are available for this user. This depends on the
    role of the user.
    """
    
    # we need to determine which playgrounds the user can see, which we handle by a
    # foreign key or wildcard (depending on user role)
    playgrounds = Playground.objects.filter(owner__username = request.user.username).all()
    opts = {
        "playgrounds": playgrounds
    }
    
    return render(request, "index.html", fillContext(opts, request))

def fillContext(opts, req):
    """
    Given a set of already filled in options for a context render, fill in some of the additional
    details.
    """
    nopts = {
        "notification_unread_count": getNotificationCount(req),
        "version": settings.VERSION,
        "request": req
    }
    
    for (k, v) in nopts.items():
        if k not in opts:
            opts[k] = v
    return opts
    
def getNotificationCount(request):
    return Notification.objects.unreadCountForUser(request.user.id)

@login_required
def playgroundList(request):
    # we need to determine which playgrounds the user can see, which we handle by a
    # foreign key or wildcard (depending on user role)
    playgrounds = Playground.objects.filter(owner__username = request.user.username).all()
    opts = {
        "playgrounds": playgrounds, 
        "nav": "playgrounds"
    }
    
    return render(request, "playgrounds.html", fillContext(opts, request))

@login_required
def feedbackView(request):
    opts = {
        "nav": "feedback"
    }
    
    return render(request, "feedback.html", fillContext(opts, request))

@login_required
def dataDepotView(request):
    opts = {
        "nav": "datadepot"
    }
    
    return render(request, "datadepot.html", fillContext(opts, request))

def registerView(request):
    return render(request, "register.html", fillContext({}, request))

@login_required
def playgroundDetails(request, playground_id):
    """
    Show the details of a playground. The user needs to either be an admin, or the owner of this
    playground, otherwise they get redirected to the portal root.
    """
    showDetails = True
    playground = Playground.objects.get(id=playground_id)
    
    if playground is None:
        showDetails = False
    
    if not (request.user.is_staff or request.user.is_superuser) and (playground.owner != request.user):
        showDetails = False
    
    if not showDetails:
        return HttpResponseRedirect("/")
    else:
        sandbox_requests = SandboxRequest.objects.filter(sandbox__playground__id=playground_id)
        opts = {
                "playground": playground, 
                "sandbox_requests": sandbox_requests, 
                "nav": "playgrounds"
            }

        request.session['current_playground_id'] = playground_id
        return render(
            request, 
            "playgroundDetails.html", 
            fillContext(opts, request)
        )

@login_required    
def sandboxDetails(request, sandbox_id):
    """
    Show the detailed information about the sandbox: parent playground, request details, etc.
    """
    showDetails = True
    sandbox = Sandbox.objects.get(id=sandbox_id)
    
    if sandbox is None:
        showDetails = False
    
    if not (request.user.is_staff or request.user.is_superuser) and (sandbox.owner != request.user):
        showDetails = False
    
    if not showDetails:
        return HttpResponseRedirect("/")
    else:        
        sandbox_request = SandboxRequest.objects.filter(sandbox=sandbox)[0]
        opts = {
                "sandbox": sandbox, 
                "sandbox_request": sandbox_request, 
                "nav": "playgrounds"
            }

        return render(
            request, 
            "sandboxDetails.html",
            fillContext(opts, request)
        )

@login_required
def notificationList(request):
    """
    Find a list of notifications, and make them useful for display.
    """
    notices = Notification.objects.unreadForUser(request.user.id)

    opts = {
            "notifications": notices, 
            "nav": "notifications"
        }
    
    return render(
        request, 
        "notifications.html", 
        fillContext(opts, request)
    )
    
@login_required
def notificationMarkAllRead(request):
    """
    Mark all the notifications for this user as read.
    """
    Notification.objects.markAllReadForUser(request.user.id)
    return HttpResponseRedirect("/notifications")
    
@login_required
def profileView(request):
    """
    Most of the user information is managed by the Single Sign On service - we can
    extend some bits of the User through additional models.
    """
    return render(request, "profile.html", fillContext({}, request))    

@login_required
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
            print ("Added SSH Key for user with ID (%d)" % (request.user.id))
            return HttpResponseRedirect("/accounts/profile")
        else:
            print ("Form is invalid")
            
    opts = {"form": form}
    return render(request, "addSshKey.html", fillContext(opts, request))

@login_required
def removeSshKey(request, sshkey_id):
    sshkey = SshKey.objects.get(pk=sshkey_id)
    
    if sshkey.user == request.user:
        sshkey.delete()
    
    return HttpResponseRedirect("/accounts/profile")

def listSshKeys(request, user_id):
    
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": True, "msg": "Invalid user id"})
        
    keys = []
    for sshkey in user.sshkeys.all():
        if sshkey.isValid():
            keys.append(
                {
                    "name": sshkey.name,
                    "fingerprint": sshkey.fingerprint(),
                    "id": sshkey.id
                }
            )
    res = {
        "error": False,
        "keys": keys
    }
    return JsonResponse(res)

def getSshKey(request, user_id, sshkey_id):
    
    try:
        user = User.objects.get(pk=user_id)
        key = SshKey.objects.get(pk = sshkey_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": True, "msg": "Invalid user or key id"})
    
    if user != key.user:
        return JsonResponse({"error": True, "msg": "Invalid User and Key association"})
    
    return JsonResponse(
        {
            "name": key.name,
            "fingerprint": key.fingerprint(),
            "key": key.key
        }
    )
    
@permission_required('cocreate.change_sandboxrequest', login_url="/login")
def requestRandomSandbox(request):
    """
    Generate a random sandbox request and status object.
    """
    sreq = SandBoxRequest.objects.create(
        requested_by = request.user,
        sandbox_name = "floob" + str(random.randint(0,1000)),
        lifetime = datetime.datetime.now().date()
    )
    
    stat = SandboxRequestStatus.objects.create(
        request = sreq,
        status = SandboxRequestStatus.SUBMITTED
    )
    
    return HttpResponse("Ok.")
    
@login_required
def requestRandomPlayground(request):
    """
    Generate a random sandbox request and status object.
    """
    preq = Playground.objects.create(
        owner = request.user,
        name = "Co-Create Playground " + str(random.randint(0, 1000))
    )
        
    preq_req = PlaygroundRequest.objects.create(
        requested_by=request.user,
        name="Playground request",
        justification="\n\n".join(simpleipsum(4)),
        playground=preq
    )
    
    """
    for x in range(0, random.randint(1,10)):
        sbox = Sandbox.objects.create(
            name = "Co-Create Sandbox " + str(random.randint(0,1000)),
            owner = request.user,
            playground = preq
        )
        
        sbox_req = SandboxRequest.objects.create(
            requested_by=request.user,
            sandbox_name=sbox.name,
            justification="tbd",
            sandbox_lifetime=datetime.datetime.now()+datetime.timedelta(days=300),
            space_needed="20GB",
            sandbox=sbox
        )
    """

    print("Added random playground for %s" % (request.user.username))
    return HttpResponse("Ok. Added playground for " + request.user.username)    

@login_required
def clearPlaygrounds(request):
    """
    Clear out the existing playgrounds. This is _totally_ destructive, so, you know,
    take this out after initial dev work is complete.
    """
    Playground.objects.all().delete()
    return HttpResponse("Ok. Cleared out the playgrounds.")

def simpleipsum(paragraphs=1):
    """
    Dead simple ipsum generator.
    """
    words = open("/usr/share/dict/words", "r").read().splitlines()
    
    output = []
    
    for para in range(0, paragraphs):
        output.append(" ".join(random.sample(words, random.randint(5,15))) + ".")
    return output
    
@login_required
def requestPlayground(request):
    """
    Playgrounds consume no real resources, so users can request as many as they like. When creating
    the playground, the user specifies the deployment target, which is then static.
    """
    if request.method == 'GET':
        form = PlaygroundForm()
    elif request.method == 'POST':
        form = PlaygroundForm(request.POST)
        
        if form.is_valid():
            # hooray, let's create the playground
            playground = Playground.objects.create(
                name = form.data['name'],
                description = form.data['description'],
                owner = request.user,
                environment = form.data['environment']
            )
            playground.save()
            return HttpResponseRedirect("/playground/" + str(playground.id))
            
    opts = {"form": form}
    return render(request, "playgroundRequest.html", fillContext(opts, request))

def scheduleSandboxDeployment(request, sbr):
    """
    Given a newly created sandbox request, schedule the deployment with the backend. This
    will also handle any quota checking, notifications, and environment specific prep.
    """
    if sbr.sandbox.playground.environment == 'locl':
        # local deploy, no formal request
        sbr.request_status = 'avl'
        sbr.save()
    else:
        # environment deploy, let's kick it to the admins
        sandbox_request_uri = request.build_absolute_uri(reverse('admin:cocreate_sandboxrequest_change', args=(sbr.id,)))
        mail_admins(
            "Sandbox Request for Review",
            "There's a new request for review at " + sandbox_request_uri,
            html_message = get_template("sandboxRequestToAdmins.html").render(Context({"sandbox_request_uri": sandbox_request_uri}))
        )

@login_required
def requestAWSSandbox(request):
    if request.method == 'POST':
        playground_id = request.session['current_playground_id']
        playground = Playground.objects.get(id=playground_id)
        
        # create a sandbox request
        sb = SandboxRequest()
        sb.requested_by = request.user
        sb.sandbox_name = request.POST['name']
        sb.justification = "AWS sandbox"
        sb.sandbox_lifetime = "2016-01-01"
        
        # create the sandbox
        sb.sandbox = Sandbox.objects.create(
            name = sb.sandbox_name,
            owner = request.user,
            playground = playground
        )
        
        sb.save()
        
        # create the AWS options record
        sao = SandboxAWSOptions()
        sao.name = sb.sandbox_name
        sao.recipe = request.POST['recipe']
        sao.ami = request.POST['ami']
        sao.vpc = request.POST['vpc']
        sao.json = filterPOSTToJSON(request.POST, ['recipe', 'ami', 'sshKey', 'subnet', 'vpc', 'type', 'secGroups[]', 'name'])
        sao.request = sb
        
        sao.save()
        
        # save it, send it
        
        print ("Post:", request.POST)
        print ("JSON:", sao.json)

        # now decide what to do based on the deployment environment
        #scheduleSandboxDeployment(request, sb)
        awsWentOK = requestAWSInstance(json.loads(sao.json))
        
        return JsonResponse({"error": not awsWentOK})
    else:
        return JsonResponse({"error": False})

def filterPOSTToJSON(body, fields):

    filtered = {}
    for k in fields:
        fk = k
        if k.endswith('[]'):
            fk = k[:-2]
            filtered[fk] = body.getlist(k)
        else:
            filtered[fk] = body[k]
    return json.dumps(filtered)

def requestAWSInstance(props):
    """
    Request an AWS instance from the node Chef controller using the given
    options.
    """
    req = requests.post(settings.CHEF_CONTROLLER_URL + "/create", data=props)
    print ("AWS Request POSTed")
    if req.status_code == requests.codes.ok:
        print ("...ok")
        return True
    else:
        # we have a problem
        print ("...not ok (%d)" % (req.status_code))
        print (req.text)
        return False

    
@login_required
def requestSandbox(request):
    if request.method == 'POST':
        form = SandboxRequestForm(request.POST, request=request)
        [print("%s=%s" % (k, v)) for k, v in form.data.items()]
        if form.is_valid():
            # create the basic request structure
            playground_id = request.session['current_playground_id']
            playground = Playground.objects.get(id=playground_id)
            sb = SandboxRequest()
            sb.requested_by = request.user
            sb.sandbox_name = form.data['sandbox_name']
            sb.justification = form.data['justification']
            sb.sandbox_lifetime = form.data['sandbox_lifetime']
            sb.template = SandboxTemplate.objects.get(id=int(form.data['template']))
            sb.sandbox = Sandbox.objects.create(
                name=sb.sandbox_name,
                owner=request.user,
                playground=playground
            )
            sb.save()
            
            # now decide what to do based on the deployment environment
            scheduleSandboxDeployment(request, sb)
            
            return HttpResponseRedirect('/playground/' + playground_id)
    else:
        form = SandboxRequestForm()
    opts = {"form": form}
    return render(request, "sandboxRequest.html", fillContext(opts, request))

@login_required
def awsRequestView(request):
    return render(request, "awsCreateInstance.html", fillContext({}, request))

@login_required
def awsRequestStatusView(request):
    return render(request, "awsStatus.html", fillContext({}, request))

@login_required
def awsStatusOfInstance(request, instance_name):
    return render(request, "awsStatus.html", fillContext({"instanceName": instance_name}, request))