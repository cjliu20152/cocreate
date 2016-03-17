"""
API Endpoints for RESTful JSON based data access.
"""
from django.http import JsonResponse
from django.http import HttpResponse
import requests
from ..util import single_user_mode
from django.conf import settings
from boto3.session import Session
from botocore.exceptions import ClientError
import json
from subprocess import Popen, PIPE, call
import os
import os.path
import time
import platform
import hashlib
import shutil
import subprocess
from omnibus import api

from ..models import UserConfig

#AMIS = ["ami-ed1204dd"] # Hardcoded list of tested amis
    # This is a Centos AMI that is known to work with geoq.  Various other AMIs won't work, some issues are:
    # - Not all ami's support user-data
    # - Only Centos/Rhel 6 work with some of our third party cookbooks
    # - Some ami's use root as the initial login user instead of ec2-user


# TODO: Should these be int settings.py vice being crammed in here?
#
COOKBOOK_PATH = os.path.expanduser("~/cookbooks/") # The cookbook path is the path to where you clone cookbooks on your machine (we should probably ask for this)
ENVIRONMENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'environments'))
VAGRANT_PATH = os.path.expanduser("~/vagrant_vms/")
DEFAULT_REGION="us-west-2"

COCREATELITE_KEYNAME = 'CoCreate:lite'
PRIVATE_KEY_PATH = os.path.expanduser('~/.ssh/id_rsa')


def getSessionClient(request):

    access_key = UserConfig.objects.findOrCreate_AwsKey(request.user).val
    secret_key = UserConfig.objects.findOrCreate_AwsSecret(request.user).val

    session = Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=DEFAULT_REGION)
    #ec2 = session.client('ec2', verify='cacerts.txt')
    ec2 = session.client('ec2')
    return ec2

def errorWithMessage(s):
    return {"error": True, "msg": s}

    
def nodeControllerError(r):
    return errorWithMessage("Error reaching node controller (HTTP Error %d)" % r.status_code)


def aws_instanceTypes(request):
    """
    Determine the different instance types available
    """
    instanceTypes =   {"InstanceTypes": [
    "t1.micro",
    "m1.small",
    "m1.medium",
    "m1.large",
    "m1.xlarge",
    "m3.medium",
    "m3.large",
    "m3.xlarge",
    "m3.2xlarge",
    "t2.micro",
    "t2.small",
    "t2.medium",
    "m2.xlarge",
    "m2.2xlarge",
    "m2.4xlarge",
    "cr1.8xlarge",
    "i2.xlarge",
    "i2.2xlarge",
    "i2.4xlarge",
    "i2.8xlarge",
    "hi1.4xlarge",
    "hs1.8xlarge",
    "c1.medium",
    "c1.xlarge",
    "c3.large",
    "c3.xlarge",
    "c3.2xlarge",
    "c3.4xlarge",
    "c3.8xlarge",
    "cc1.4xlarge",
    "cc2.8xlarge",
    "g2.2xlarge",
    "cg1.4xlarge",
    "r3.large",
    "r3.xlarge",
    "r3.2xlarge",
    "r3.4xlarge",
    "r3.8xlarge"
    ]}
    return JsonResponse(instanceTypes)


def isee_instanceTypes(request):
    """
    Mimic the data format of the AWS results:
        
        {"InstanceTypes":["name_001", ..., "name_xxx"]}
    """
    isee_types = ["small", "medium", "large", "x-large"]
    return JsonResponse({"InstanceTypes": isee_types})
 

def aws_amis(request):
    """
    Determine available AMIs
    """

    #ec2 = getSessionClient(request)
    #json = ec2.describe_images(ImageIds=AMIS)
    #print(json)

    ##
    ## For now just the "packer cocreate base" will be returned.
    ##

    access_key = UserConfig.objects.findOrCreate_AwsKey(request.user).val
    secret_key = UserConfig.objects.findOrCreate_AwsSecret(request.user).val

    session = Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=DEFAULT_REGION)

    ec2 = session.client('ec2')

    json = ec2.describe_images(
        DryRun=False,
        Owners=[
            'self',
        ],
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    'CoCreateLite Base',
                ]
            },
        ]
    )

    return JsonResponse(json)


def aws_vpcs(request):
    """
    Determine available VPCs for an instances
    """
    print("entered aws_vps")
    ec2 = getSessionClient(request)
    print("***********************************")
    print(ec2.describe_vpcs())
    print("***********************************")
    print("exiting aws_vps")
    return JsonResponse(ec2.describe_vpcs())


def aws_vpc_subnets(request, vpc_name):
    """
    Determine available subnets based on the VPC
    """
    ec2 = getSessionClient(request)
    print("aws_vpc_subnets =============>", JsonResponse(ec2.describe_subnets(Filters=[{'Name':'vpc-id', 'Values': [vpc_name]}])))
    return JsonResponse(ec2.describe_subnets(Filters=[{'Name':'vpc-id', 'Values': [vpc_name]}]))

    
def aws_vpc_secgroups(request, vpc_name):
    """
    Determine available security groups based on VPC
    """
    ec2 = getSessionClient(request)
    print(ec2.describe_security_groups(Filters=[{'Name':'vpc-id', 'Values': [vpc_name]}]))
    return JsonResponse(ec2.describe_security_groups(Filters=[{'Name':'vpc-id', 'Values': [vpc_name]}]))

    
def chef_cookbooks(request):
    """
    Determine available cookbooks
    """

    supported_recipes = [{"displayName": "Apache Webserver", "recipe": "nga-webserver"},
      {"displayName": "Baseline Security Patches", "recipe": "nga-baseline"},
      {"displayName": "EAW OWF", "recipe": "nga-ozone::owf"},
      {"displayName": "EAW App Mall", "recipe": "nga-ozone::omp"},    
      {"displayName": "GeoEvents", "recipe": "geoevents"},
      {"displayName": "GeoQ", "recipe": "geoq"},    
      {"displayName": "CoCreate Lite", "recipe": "cocreate-lite"},    
      {"displayName": "CCL Test", "recipe": "ccltest"},    
      {"displayName": "Tomcat Application Server", "recipe": "nga-appserver"}]

    # Only list cookbooks the user has actually installed on their system
    installed_recipes = []
    for ( recipe ) in supported_recipes:
        cookbook = recipe['recipe']
        repo = cookbook.split('::', 1)[0]
        if(os.path.isdir(COOKBOOK_PATH + repo)):
            installed_recipes.append(recipe)
        else:
            print("Could not find supported cookbook: " + repo)

    return JsonResponse({'recipes': installed_recipes})
    #return nodeProxyRequest("/chef/cookbooks/impl")


def keypairs(request):
    """
    Find available keypairs to install in instance at creation
    """
    ec2 = getSessionClient(request)
    return JsonResponse(ec2.describe_key_pairs())


def aws_recipeConfig(request, recipe_name):
    """
    Find the optimal configuration for a recipe
    """
    return JsonResponse({'default_configs': []})
    #return nodeProxyRequest("/aws/applicationConfig/" + recipe_name, debug=True)
 

def isee_recipeConfig(request, recipe_name):
    """
    Return a stub default config for the given recipe. The only really interesting
    piece right now is the instanceType.
    """
    return JsonResponse({"instanceType": "medium", "recipe": recipe_name})


@single_user_mode
def repositories(request):
    reps = []
    for repo in request.user.repositories.all():
        reps.append(
            {
                "name": repo.name,
                "uri": repo.uri,
                "id": repo.id
            }
        )
    return JsonResponse({"Repositories": reps})


def create_key_pair(ec2_client, key_name):
    """
    Creates a key pair named key_name in AWS EC2 using the ec2_client,
    and returns the resulting key pair.
    """

    key_pair = None

    try:
        key_pair = ec2_client.create_key_pair(KeyName=key_name)
    except ClientError:
                # Keypair already exists so create a new keypair, because
                # we've lost our private key used by Vagrant to ssh into
                # instances to configure
        ec2_client.delete_key_pair(KeyName=key_name)
        key_pair = ec2_client.create_key_pair(KeyName=key_name)

    return key_pair


def create_private_key(aws_access_key, aws_secret_key):
    """
    Creates a private key for CoCreate:lite's vagrant to use.
    """

    session = Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=DEFAULT_REGION)

    ec2_client = session.client('ec2')

    key_pair = None

    if not os.path.exists(PRIVATE_KEY_PATH):
        # the private key doesn't exit therefore create
        key_pair = create_key_pair(ec2_client, COCREATELITE_KEYNAME)
    elif not ec2_client.describe_key_pairs(Filters=[
            {
                'Name': 'key-name',
                'Values': [
                    COCREATELITE_KEYNAME,
                ]
            },
        ])['KeyPairs']:
        # the private key exists, but AWS has lost the associated key pair
        # some how. likely the user deleted it via the AWS keypair web interface
        key_pair = create_key_pair(ec2_client, COCREATELITE_KEYNAME)
    else:
        return

    with open(PRIVATE_KEY_PATH, 'w') as private_key_file:
        private_key_file.write(key_pair['KeyMaterial'])

    # REMOVE: used for debugging
    print(key_pair['KeyMaterial'], flush=True)


def aws_create(request, playground):
    reqData = request.POST
    sgroups = str(reqData.getlist('secGroups[]', []))

    """
    Create the instance and initiate chef-zero using Vagrant

    """

    aws_access_key = UserConfig.objects.findOrCreate_AwsKey(request.user).val
    aws_secret_key = UserConfig.objects.findOrCreate_AwsSecret(request.user).val

    create_private_key(aws_access_key, aws_secret_key)    

    http_proxy = UserConfig.objects.findOrCreate_ProxyHttp(request.user).val
    https_proxy = UserConfig.objects.findOrCreate_ProxyHttps(request.user).val

    print("Printing create post", flush=True)
    print(request.POST)
    # Names rather than django ids are used since the sandbox id isn't generated until later.  This is a chicken/egg problem.
    sandbox_name = request.POST['name']
    m = hashlib.sha256()
    m.update(sandbox_name.encode('utf-8'))
    m.update(playground.name.encode('utf-8'))
    vm_id = m.hexdigest()

    # We already track sandbox's through the SandboxVM model, the check should occur there.
    if os.path.exists(VAGRANT_PATH + vm_id):
       print("VM already exists: " + VAGRANT_PATH + vm_id, flush=True)
       return "error" # Consider better error handling
    else:
       os.makedirs(VAGRANT_PATH + vm_id)

    # Fix Berksfile path resolution to work with both 'geoq' and 'geoq::default' formats
    berksfile_dirname = request.POST['recipe'].split("::")[0]

    #Generate the Vagrantfile in the cookbook directory
    file = open(VAGRANT_PATH + vm_id + '/Vagrantfile', 'w')
    file.write('Vagrant.configure(2) do |config|\n')
    if platform.system() == "Windows":
        file.write('  ENV["VAGRANT_DETECTED_OS"] = ENV["VAGRANT_DETECTED_OS"].to_s + " cygwin"\n')
    else:
        file.write('  ENV["VAGRANT_DETECTED_OS"] = ENV["VAGRANT_DETECTED_OS"].to_s\n')
    file.write('  config.ssh.username = "ec2-user"\n')

    file.write('  config.ssh.private_key_path = "' + PRIVATE_KEY_PATH + '"\n')
    file.write('  config.ssh.pty = true\n')
    # The Berksfile is located in the specific cookbook directory
    file.write('  config.berkshelf.berksfile_path = "' + COOKBOOK_PATH + berksfile_dirname + '/Berksfile"\n')
    file.write('  config.berkshelf.enabled = true\n')
    file.write('  config.vm.synced_folder "", "/vagrant", type: "rsync", rsync__exclude: ".git/"\n')
    file.write('  config.proxy.http = "' + http_proxy + '"\n')
    file.write('  config.proxy.https = "' + https_proxy + '"\n')
    file.write('  config.vm.box = "dummy"\n')
    file.write('  config.trigger.before [:reload, :up, :provision], stdout: true do\n')
    file.write('      SYNCED_FOLDER = ".vagrant/machines/default/aws/synced_folders"\n')
    file.write('      info "Trying to delete folder #{SYNCED_FOLDER}"\n')
    file.write('      # Delete synced folders as workaround to known vagrant bug.\n')
    file.write('      begin\n')
    file.write('          File.delete(SYNCED_FOLDER)\n')
    file.write('      rescue Exception => ex\n')
    file.write('          warn "Could not delete folder #{SYNCED_FOLDER}."\n')
    file.write('          warn ex.message\n')
    file.write('      end\n')
    file.write('  end\n')
    file.write('  config.vm.provider :aws do |aws|\n')
    file.write('    aws.user_data = "#!/bin/bash\\nsed -i -e \'s/^Defaults.*requiretty/# Defaults requiretty/g\' /etc/sudoers"\n')
    file.write('    aws.access_key_id = "'+ aws_access_key + '"\n')
    file.write('    aws.secret_access_key = "'+aws_secret_key+'"\n')
    file.write('    aws.keypair_name = "'+ COCREATELITE_KEYNAME +'"\n')
    file.write('    aws.instance_type = "'+ request.POST['type'] +'"\n')
    file.write('    aws.region = "'+ DEFAULT_REGION + '"\n')
    file.write('    aws.security_groups = '+ sgroups +'\n')
    file.write('    aws.ami = "'+ request.POST['ami'] + '"\n')
    file.write('    aws.subnet_id = "'+ request.POST['subnet']+'"\n')
    file.write('    aws.tags = {\n')
    file.write('      "Name" => "'+ request.POST['name'] +' "\n')
    file.write('    }\n')
    file.write('    aws.associate_public_ip = true\n')
    file.write('  end\n')
    file.write('  config.vm.provision "chef_zero" do |chef|\n')
    file.write('    chef.cookbooks_path = "'+ COOKBOOK_PATH + '"\n')
    file.write('    chef.nodes_path = "/tmp"\n')
    file.write('    chef.add_recipe "' + request.POST['recipe'] + '"\n')
    file.write('    chef.environment = "cocreatelite"\n')
    file.write('    chef.environments_path = "' + ENVIRONMENT_PATH + '"\n')
    file.write('  end\n')
    file.write('end')
    file.close()

    # TODO: a separate process using something like Celery or Twisted to 
    #       create/provision the new resource and provide better status info
    
    # Run 

    cwd_path = VAGRANT_PATH + vm_id
    aws_name = request.POST['name']

    # needed to force the provider in some environments (like mine)
    os.environ['VAGRANT_DEFAULT_PROVIDER'] = 'aws'
    os.environ['HOME'] = '/root'

    vagrant_cmd = 'vagrant up --no-provision --provider=aws'
    print("executing: " + vagrant_cmd, flush=True)
    api.publish('vagrants', aws_name, {'text': ''}) # omnibus appears to eat first event
    api.publish('vagrants', aws_name, {'text': vagrant_cmd})

    vagrantProcess = subprocess.Popen(vagrant_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd_path)

    print("bout to print stdout", flush=True)

    if vagrantProcess.stdout is not None:
        for line in iter(vagrantProcess.stdout.readline, b''):
            line = line.decode("utf-8").rstrip()
            print("<stdout> " + line, flush=True)
            api.publish('vagrants', aws_name, {'text': line})

    print("bout to print stderror", flush=True)

    if vagrantProcess.stderr is not None:
        for line in iter(vagrantProcess.stderr.readline, b''):
            line = line.decode("utf-8").rstrip()
            print("<stderr> " + line, flush=True)
            api.publish('vagrants', aws_name, {'text': line})

    # add space between
    api.publish('vagrants', aws_name, {'text': ''})


    vagrant_cmd = 'vagrant awsinfo -m default -p'
    print("executing: " + vagrant_cmd, flush=True)
    api.publish('vagrants', aws_name, {'text': vagrant_cmd})

    vagrantProcess = subprocess.Popen(vagrant_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd_path)

    instance_id = ''

    if vagrantProcess.stdout is not None:
        aws_info = ''
        for line in iter(vagrantProcess.stdout.readline, b''):
            line = line.decode("utf-8").rstrip()
            print("<stdout> " + line, flush=True)
            api.publish('vagrants', aws_name, {'text': line})  
            aws_info += line   
        
        # TODO:  so this will fail if aws_stdout doesn't hhave the expected string
        #        need to trap and better handle either here or by what calls this
        #        method
        
        instance_id = json.loads(aws_info)['instance_id']
        print("set instance_id = " + instance_id)        

    if vagrantProcess.stderr is not None:
        for line in iter(vagrantProcess.stderr.readline, b''):
            line = line.decode("utf-8").rstrip()
            print("<stderr> " + line, flush=True)
            api.publish('vagrants', aws_name, {'text': line})


    # add space between
    api.publish('vagrants', aws_name, {'text': ''})

    
    vagrant_cmd = 'vagrant provision'
    print("executing: " + vagrant_cmd, flush=True)
    api.publish('vagrants', aws_name, {'text': vagrant_cmd})
    vagrantProcess = subprocess.Popen(vagrant_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=cwd_path)

    if vagrantProcess.stdout is not None:
        for line in iter(vagrantProcess.stdout.readline, b''):
            line = line.decode("utf-8").rstrip()
            print("<stdout> " + line, flush=True)
            api.publish('vagrants', aws_name, {'text': line})


    if vagrantProcess.stderr is not None:
        for line in iter(vagrantProcess.stderr.readline, b''):
            line = line.decode("utf-8").rstrip()
            print("<stderr> " + line, flush=True)
            api.publish('vagrants', aws_name, {'text': line})

    # add space between 
    api.publish('vagrants', aws_name, {'text': ''})

    api.publish('vagrants', aws_name, {'text': 'Done.  Goodbye.'})

    return instance_id
    

def aws_instance_by_id(request):
    return JsonResponse()


def start_instance(request, awsInstanceId):
    ec2 = getSessionClient(request)
    ec2.start_instances(InstanceIds=[awsInstanceId])


def stop_instance(request, awsInstanceId):
    ec2 = getSessionClient(request)
    ec2.stop_instances(InstanceIds=[awsInstanceId])


def terminate_instance(request, awsInstanceId, playground_name, sandbox_name):

    m = hashlib.sha256()
    m.update(sandbox_name.encode('utf-8'))
    m.update(playground_name.encode('utf-8'))
    vm_id = m.hexdigest()

    shutil.rmtree(VAGRANT_PATH + vm_id)

    ec2 = getSessionClient(request)
    ec2.terminate_instances(InstanceIds=[awsInstanceId])

