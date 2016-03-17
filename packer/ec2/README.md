# Creating CoCreate:Lite Amazon Machine Images (AMIs)

The contents of this folder is used to create CoCreate:Lite and CoCreate:Lite
Base AWS EC2 AMIs.

## Configuring your shell environment

You will need to set AWS_REGION, AWS_ACCESS_KEY, and AWS_SECRET_ACCESS_KEY, and
AWS_ACCOUNT_ID in your shell environment, like so:

    AWS_REGION=us-west-2
    AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
    AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    AWS_ACCOUNT_ID=XXXXXXXXXXXX

## Creating the AMIs in your account

You will need to first create the CoCreate:Lite Base AMI via executing:

    cd base
    ./build.sh

And then create the CoCreate:Lite AMI itself:

    cd cocreatelite
    ./build.sh

