# CoCreate:Lite

## <a name="overview"></a>Name

CoCreate:Lite - provides an easy path for integrating and testing your applications within operationally realistic server configurations by leveraging the AWS EC2 and Chef cookbooks designed and tested for working within the NGA.

## <a name="description></a>Decription

CoCreate:Lite, the base AMI, and Chef Cookbooks are provided to manage the lifecycles of Applications at present in AWS EC2.

![CoCreateLite demo](demo.gif)

## <a name="versioning"></a>Versioning

Releases of CoCreate:Lite will comply with the Semantic Versioning specification at [http://semver.org/][semver]. CoCreate:Lite is currently under active development; see TODO.txt, if it exists, at the root of the project for a tentative roadmap. Patches will be worked in a branch prior to being tagged and released.

## <a name="releases"></a>Releases

Releases are distributed via the github project page.

## <a name="clone"></a>Clone this project

Clone the CoCreate:Lite project via:

    git clone https://github.com/ngageoint/cocreate.git

A `git clone` command will not retrieve submodules automatically. As of now there are no submodules, but more Chef Cookbooks will be released and be added to this project as submodules.

Alternatively, using the `--recursive` flag when cloning the repository to also retrieve submodules via:

	git clone --recursive https://github.com/ngageoint/cocreate.git

## Contributing

If you plan to contribute to CoCreate:Lite, please install and use [Git Secrets](https://github.com/awslabs/git-secrets) to prevent you from committing passwords and other sensitive information to the repository.

See the CONTRIBUTING.md file at the root of this project for more details on contributing.

## <a name="dependencies"></a>Dependencies and Necessary Configuration

This section enumerates the necessary command-line tools you must install, and suggests an AWS VPC configuration involving an OpenVPN serever to utilize CoCreate:Lite safely on private, isolated section of the AWS cloud.

### <a name="installing_cmd_line_tools"></a>Installing Command-line Tools

Download and install the following command-line tools for your platform:

* VirtualBox <https://www.virtualbox.org/wiki/Downloads>,
* Vagrant <https://www.vagrantup.com/downloads.html>,
* Packer <https://www.packer.io/downloads.html>, and
* AWS CLI <https://aws.amazon.com/cli/>.

Install the following Vagrant plugin(s):

    vagrant plugin install vagrant-vbguest

### <a name="as_account"></a>Amazon AWS account

You will need an [Amazon Web Services account](https://aws.amazon.com).

We strongly encourage you to utilize [IAM Best Practices](http://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html?icmpid=docs_iam_console) to constrain the damage an adversary can do, if your AWS root credentials were to be mistakenly disclosed.

Also, we'd advise utilizing AWS's [Trusted Advisor Dashboard](https://console.aws.amazon.com/trustedadvisor/home#/dashboard) to gauge how securely your AWS account is configured.

### <a name="configuring_a_vpc"></a>Configuring an Amazon Virtual Private Cloud (VPC) 

We encourage you to not run CoCreate:Lite with a public IP, but preferably on private, isolated section of the AWS cloud with direct access to the Internet or via a [Vagrant](#creating_box) by creating a VPC with public and private subnets by using the Amazon VPC Wizard.

1.  Open the Amazon VPC console at <https://console.aws.amazon.com/vpc/>.

2.  In the navigation bar, on the top-right, make sure you remain in the same region for the entire time you are following these instructions, as you cannot spin up instances into your VPC from a different region.

3.  In the navigation pane, choose **VPC dashboard**, and then choose **Start VPC Wizard**.

4.  Choose the second option, **VPC with Public and Private Subnets,** and then choose **Select**.

5.  On the configuration page, enter a name for your VPC in the **VPC name** field; for example, `My VPC`. You can leave the rest of the configuration settings set to their defaults, and choose **Create VPC**.  It will take a few minutes to spin up your VPC.

### <a name="utilizing_a_vpn"></a>Utilizing a VPN

We suggest spinning up a VPN server on your VPC's public subnet to access your EC2 instances spun up on your VPC's private subnet.  There are several ways such as a spinning up a linux EC2 instance and configuring OpenVPN yourself, but in the following section, we will describe procuring an OpenVPN Amazon Machine Iomage (AMI) template from the Amazon Marketplace and configuring it.

1.  Open the Amazon EC2 console at <https://console.aws.amazon.com/ec2/>.

2.  From the console dashboard, choose **Launch Instance**.

3.  On the **Choose an Amazon Machine Image (AMI)** page, select **AWS Marketplace**, and search for `OpenVPN Access Server (HVM)`, and then click **Select**.

4.  On the **Choose an Instance Type** page, select the free-tier `t2.micro`, and then click **Next: Configure Instance Details**.  The license that comes with this AMI only supprts two VPN connections, if you plan on more than two VPN connections you may want to select a more powerful type.  If it is just you, the free-tier should suffice.

5.  On the **Configure Instance Details** page, select the [VPC you created earlier](#configuring_a_vpc) for **Network**, select the VPC's public subnet for **Subnet**, select **Enable** for **Auto-assign Public IP**, and then click **Next: Add Storage**.

6.  On the **Add Storage** page, increase **Size (GiB)** to `30`, and then click **Next: Tag Instance**.

7.  On the **Tag Instance** page, enter a **Name** of `OpenVPN`, and then click **Next: Configure Security Group**.

8.  On the **Configure Security Group** page, approve the security groups provided by clicking **Click Review and Launch**.

9.  On the **Review Instance Launch** page, you can review your instance launch details or go back to edit changes for each section.

     1.  If things look fine, click **Launch**.

     2.  After clicking **Launch**, a dialog will open instructing you to **Select an existing key pair or create a new key pair**.  In my case, I've selected my existing key pair, acknowledged that I have access to the selected private key file, and then click **Launch Instance** to continue, then wait for the instance to be provisioned and configured.

Once the `OpenVPN` instance has spun up:

1.   You can optionally allocate an **Elastic IP** and associate it with your `OpenVPN` EC2 instance, otherwise skip to step 2. AWS bills for Elastic IP usage, but utilizing an Elastic IP for the `OpenVPN` EC2 instance offers you the convience of not entering a new public IP into your VPN client, if the `OpenVPN` was to be stopped and restarted, or terminating and creating a new VPN server instance.

       1.  In the navigation pane, under **NETWORK & SECURITY**, choose **Elastic IPs**.

       2.  Choose **Allocate New Address**.

       3.  Choose **Yes, Allocate**, and close the confirmation dialog box.

       4.  Select the Elastic IP address you just allocated, choose **Actions**, and then select ***Associate Address**.

       5.  In the **Associate Address** dialog box, enter `OpenVPN` for **Instance**, select the instance id associated with, and then choose **Associate**.

2.   In the EC2 Console, select the `OpenVPN` instance, choose the **Action**, select **Networking**, and the  **Change Source/Dest. Check**. In the **Disable Source/Destination Check**, choose **Yes, Disable**.

3.   Then secure shell into the `OpenVPN` instance by utilizing the private key of the key pair you selected for the the instance on its creation, like so:

          ssh -i <path to private key> openvpnas@<public IP of OpenVPN instance>

4.   When you first secure shell in you will be presented with the OpenVPN Access Server End User License Agreement to approve.  Respond `yes`, and then accept all the defaults presented yo you by pressing the return key.

5.   Then change the password of `openvpn` user by entering:

        sudo passwd openvpn

     Remember this password as you will utilize it to retrieve the VPN Client and admin the server.

6.   Open a web browser and type `https://` into the address bar followed by the `OpenVPN` EC2 instance's public IP. Your browser may alert you to a concern involving the server's use of a self-signed certificate, just ignore the warnings, and then athenticate with the user `openvpn` and the password you provided earlier.

7.   Download and install the client.  THe browser tab will likely hang after the client is configured for your serve, so just close thhe tab.

8.   Use the client to connect.  You now will access to instances you will later spin up on your VPC's private subnet.

### <a name="creating_security_groups"></a>Creating Security Groups

Before creating an AWS EC2 instance for CoCreate:Lite, you will need to create three security groups.  As a refresher, an [AWS Security Group](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html) acts as a virtual firewall that controls the traffic access (both in and outbound access to CoCreate:Lite).  

You will need a rule to permit:

*  [secure shell](https://en.wikipedia.org/wiki/Secure_Shell) access,
*  another for [Hypertext Transfer Protocol (HTTP)](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol), and
*  one for CoCreate:Lite's [WebSocket](https://en.wikipedia.org/wiki/WebSocket) server.

The following enumerates how to create these:

1.  Open the Amazon EC2 console at <https://console.aws.amazon.com/ec2/>.

2.  In the navigation pane, under **NETWORK & SECURITY**, choose **Security Groups**.

3.  My preference is to create rule per protocol vice a security group of rules per instance.

4.  Choose **Create Security Group** to create the first of three rules.

5.  Complete the **Create Security Group** dialog by submitting the following **HTTP** security group details:

    Security Group Name | Description                         | VPC
    :------------------ | :---------------------------------: | :------------------:
    HTTP                | http access (ports: 80, 8000, 8080) | You created earlier.

    Enter the following **Inbound** rules by clicking **Add Rule** in the tabset found in the lower portion of the **Create Security Group** dialog:

    Type             | Protocol      | Port Range | Source
    :--------------- | :-----------: | :--------: | :----------------:
    HTTP             | TCP           | 80         | Anywhere 0.0.0.0/0
    Custom TCP Rule  | TCP           | 8000       | Anywhere 0.0.0.0/0
    Custom TCP Rule  | TCP           | 8080       | Anywhere 0.0.0.0/0

    Accept the default for **Outbound** permissive rule, and choose **Create**.

6.  Choose **Create Security Group** to create the second of three rules.

7.  Complete the **Create Security Group** dialog by submitting the following **SSH** security group details:

    Security Group Name | Description         | VPC
    :------------------ | :-----------------: | :------------------:
    SSH                 | Secure Shell Access | You created earlier.

    Enter the following **Inbound** rule by clicking **Add Rule** in the tabset found in the lower portion of the **Create Security Group** dialog:

    Type             | Protocol      | Port Range | Source
    :--------------- | :-----------: | :--------: | :----------------:
    SSH              | TCP           | 22         | Anywhere 0.0.0.0/0

    Accept the default for **Outbound** permissive rule, and choose **Create**.

8.  Choose **Create Security Group** to create the last of three rules.

9.  Complete the **Create Security Group** dialog by submitting the following **django-omnibus** security group details:

    Security Group Name | Description      | VPC
    :------------------ | :--------------: | :-----------------:
    django-omnibus      | Websocket Server | You created earlier.

    Enter the following **Inbound** rule by clicking **Add Rule** in the tab set found in the lower portion of the **Create Security Group** dialog:

    Type             | Protocol      | Port Range | Source
    :--------------- | :-----------: | :--------: | :----------------:
    Custom TCP Rule  | TCP           | 4242       | Anywhere 0.0.0.0/0

    Accept the default for **Outbound** permissive rule, and choose **Create**.

### <a name="creating_key_pairs"></a>Creating Key Pairs

Before utilizing CoCreate:Lite, you will need to create a Key Pair, so that you can secure shell into the sandboxes (i.e., an AWS EC2 instances) created by CoCreate:Lite., and CoCreate:Lite itself. Amongst several options, you can utilize the [AWS CLI](http://docs.aws.amazon.com/cli/latest/reference/ec2/create-key-pair.html), import your own, or create a new Key Pair via the EC2 Console: 

1.  Open the Amazon EC2 console at <https://console.aws.amazon.com/ec2/>.

2.  In the navigation pane, under **NETWORK & SECURITY**, choose **Key Pairs**.

4.  Choose **Create Key Pair**.

5.  Enter the name `CoCreate:Lite` for the new key pair in the **Key pair name** field of the **Create Key Pair** dialog box, and then choose **Create**.

6.  Your browser will then automatically download the private key file. The base file name is the name you specified as the name of your key pair, and the file name extension is .pem.  Save the private key file in a safe place as you will utilize it to secure shell into the sandboxes (i.e., an AWS EC2 instances) created by CoCreate:Lite.

7.  If you will use an SSH client on OS X or UNIX to connect to your Linux instance, use the following command to set the permissions of your private key file so that it can only be read by you:

        chmod 400 <private key pem file>

### <a name="creating_amis_via_packer"></a>Creating AMIs via Packer

The following steps enumerate the creation of EC2 AMIs for CoCreate:Lite and CoCreate:Lite Base.

1.  Make sure you've installed the [previously enumerated command-line tools](#installing_cmd_line_tools).

2.  Open a UNIX shell at the root of the project and configure your shell environment by setting AWS_REGION, AWS_ACCESS_KEY, and AWS_SECRET_ACCESS_KEY, and AWS_ACCOUNT_ID environment variables, like so:

        export AWS_REGION=us-west-2
        export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
        export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        export AWS_ACCOUNT_ID=XXXXXXXXXXXX

    Or utilize AWS CLI and set AWS_ACCOUNT_ID environment variable, like so:

        aws configure
        export AWS_ACCOUNT_ID=XXXXXXXXXXXX

   to set these values.

3.  Create the CoCreate:Lite Base AMI via executing:

        cd base
        ./build.sh

4.  Wait for the CoCreate:Lite Base AMI to become ready.

5.  And then create the CoCreate:Lite AMI via executing:

        cd cocreatelite
        ./build.sh

6.  Wait for the CoCreate:Lite AMI to become ready.

7.  Open the Amazon EC2 console at <https://console.aws.amazon.com/ec2/>.

9.  In the navigation pane, under **IMAGES**, select **AMIs** and you will see the images listed.


## Spinning up a CoCreate:Lite Vagrant

You have the option of spinning up a CoCreate:Lite in a local Vagrant development environment hosted on VirtualBox vice spinning up an EC2 instance to manage the lifecycle of applications hosted in Amazon Elastic Compute Cloud (EC2).

Make sure you've installed the [previously enumerated command-line tools](#installing_cmd_line_tools).

We advise creating a [VPC with public and private subnets](#configuring_a_vpc), and utilize [a VPN Server EC2 instance in the public subnet](#utilizing_a_vpn) to access your private subnet.

### <a name="creating_box"></a>Create a CentOS 6.7-86 Vagrant box

The Cocreate:Lite Vagrant will build up from a Centos-6.7-86 Vagrant box, to create this Vagrant box utilize Packer via executing the following in a UNIX shell:

    cd packer/vagrant
    build.sh

Packer will drop `centos-6-7-x64-virtualbox.box` Vagrant box into the current path.  You will need to add this box to the list of known Vagrant boxes via executing:

    vagrant box add --name ngageoint/centos-6.7-64 centos-6-7-x64-virtualbox.box

### <a name="spinning_up_vagrant"></a>Spinning up CoCreate:Lite in a Vagrant

At the root of the project, utilize the provided vagrantfile to spin up CoCreate:Lite in a Vagrant via executing the following in a UNIX shell:

    vagrant up

It will take a rather lengthy amount of time for the Vagrant to spin up.

    vagrant ssh
    sudo /etc/init.d/cocreate start
    sudo /etc/init.d/omnibusd start

Then point your browser to <http://127.0.0.1:8080>.

### <a name="stopping_destroying_cleaning_up_vagrant"></a>Stopping, Destroying, and Cleaning Up

To stop the CoCreate:Lite Vagrant:

    vagrant stop

To delete the CoCreate:Lite Vagrant virtual machine:

    vagrant destroy

To delete the `ngageoint/centos-6.7-64` box :

    cd packer/vagrant
    rm centos-6-7-x64-virtualbox.box
    vagrant box remove  ngageoint/centos-6.7-64

## Spinning up CoCreate:Lite in the Amazon Elastic Compute Cloud (EC2)

The following sections explains how to provision and configure a CoCreate:Lite EC2 instance utilizing [the AMIs you previously created](#creating_amis_via_packer).  We may make these AMIs available in the AWS Marketplace atsome later date.

We advise creating a [VPC with public and private subnets](#configuring_a_vpc), and utilize [a VPN Server EC2 instance in the public subnet](#utilizing_a_vpn) to access your private subnet.

### <a name="spinning_up_ec2"></a>Spinning up CoCreate:Lite

1.  Open the Amazon VPC console at <https://console.aws.amazon.com/vpc/>.

2.  From the console dashboard, choose **Launch Instance**.

5.  On the **Choose an Amazon Machine Image (AMI)** page, select **My AMIs** from tab and the choose **Select** for the `CoCreateLite` AMI.

6.  On the **Choose an Instance Type** page,

    1.  Filter by **All Generation**,
    2.  Select **t2.small**; or **t2.micro**, so as to not have to pay AWS, and
    3.  Then click **Next: Configure Instance Details**

7.  On the **Configure Instance Details** page,

    1.  Select **Disable** for **Auto-assign Public IP**, if you are utilizing the [VPN described earlier](#installing_openvpn), and
    2.  Then click **Next: Add Storage**

8.  On the **Add Storage** page, increase **Size (GiB)** to `30`, and then click **Next: Tag Instance**.

9.  On the **Tag Instance** page,

     1.  Enter a name like `My CoCreate:Lite` for the instance, and
     2.  Then click **Next: Configure Security Group**

10.  On the **Configure Security Group** page,

     1.  Toggle **Select an existing security group**,
     2.  Select **django-omnibus**, **http**, and **ssh**, and
     3.  Then click **Review and Launch**

11.  On the **Review Instance Launch** page, you can review your instance launch details, and go back to edit changes for each section.

     1.  If things look fine click **Launch**.

     2.  After clicking **Launch**, a modal will pop instructing you to **Select an existing key pair or create a new key pair**.  In my case, I've selected my existing key pair, acknowledged that I have access to the selected private key file, and click **Launch Instance** to continue.

     3.  You will be greeted by a **Launch Status** page, you can click on the link provided to monitor progress. Once the hourglass is gone under **Status Checks**, you will know whether or not your new CoCreate:Lite instance is ready for use.

12.  Use the EC2 Console to retrieve the private IP for CoCreate:Lite, and enter it into a web browser.

## <a name="using_cocreatelite"></a>Using CoCreate:Lite

CoCreate:Lite, the base AMI, and provided Chef Cookbooks permit you to create "Sandboxes" in "Playgrouds".  At present, CoCreate:Lite is coupled to AWS EC2, so a Sandbox is an EC2 instance and "Playgrounds" are metaphor of grouping instances.

The following sub-sections enumerate how to use CoCreate:Lite to add and delete CoCreate:Lite Sandboxes.

### <a name="entering_aws_keys"></a>Entering your AWS Credentials.

To use CoCreate:Lite You will need to provide your AWS credentials, so that the application can manage the lifecycles of your Sanboxes.

1.  Connect your VPN Client to [the OpenVPN EC2 instance](#utilizing_a_vpn) you configured earlier.

2.  Open the Amazon VPC console at <https://console.aws.amazon.com/vpc/>.

3.  Retrieve the private ip of the running CoCreate:Lite EC2 instance, and enter into your web browser.

4.  Once the page loads, select **AWS Key** from the **Settings** dropdown in the upper right-hand corner of the page.

5.  Once the page loads, complete the forms to submit and save your **Access Key** and **Secret Key**.

### <a name="adding_a_sandbox"></a>Adding a Sandbox

1.  Connect your VPN Client to [the OpenVPN EC2 instance](#utilizing_a_vpn) you configured earlier.

2.  Open the Amazon VPC console at <https://console.aws.amazon.com/vpc/>.

3.  Retrieve the private ip of the running CoCreate:Lite EC2 instance, and enter into your web browser.

4.  Once the page loads, choose **Playgrounds** in navbar.

5.  Once the page loads, choose **Default Playground** to open the playground, and select **Add Sandbox**.

6.  On the sanbox page,

    1.  Enter a name for your new sandbox isntance; for example, `Test CCL`.

    2.  Select the application to be installed for the **Instance Application** field; for example, `CCL Test`.

    3.  Select an instance operating system for the **Instance Operating System** field, for example, `CoCreateLite Base`.

    4.  Select an instance type for the **Instance Type** field, for example `t2.small`.

    5.  Select a VPC for the **Instance VPC** field, for example [the one you configured earlier](#configuring_a_vpc).

    6.  Choose the security group(s) to enable for your instance from those listed under **Security Groups**, select atleast **SSH**. (As a reminder you will use the `CoCreate:Lite` key pair [created previously](#creating_key_pairs) to SSH into any instance CoCreate:Lite spins up.)

    7.  Select your VPC's private subnet for the **Instance Subnet** field.

    8.  Choose **Submit Request**.

    9.  A modal will open to permit you to monitor the provisioning and configuring of your instance until it is completed. You can choose **Close** in the bottom right of the modal to dismiss the modal without interrupting the instance's creation.

### <a name="deleteing_a_sandbox"></a>Deleteing a Sandbox

1.  Connect your VPN Client to [the OpenVPN EC2 instance](#utilizing_a_vpn) you configured earlier.

2.  Open the Amazon VPC console at <https://console.aws.amazon.com/vpc/>.

3.  Retrieve the private ip of the running CoCreate:Lite EC2 instance, and enter into your web browser.

4.  Once the page loads, choose **Playgrounds** in navbar.

5.  Once the page loads, choose **Default Playground** to open the playground, and choose the white-x with the red box around it to delete the instance.
