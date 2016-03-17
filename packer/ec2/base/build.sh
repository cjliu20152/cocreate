#!/bin/bash

#
# Copyright (c) 2016, The MITRE Corporation. All rights reserved.
# See LICENSE for complete terms.
#

#
# Shell script to create CoCreate:Lite Base image
#
#
# @author Michael Joseph <github.com@nemonik.com>
#

function delete_prior_image {
  existingImageId=$1
  aws ec2 deregister-image --image-id "$existingImageId"

  # Takes some time to deregister...  Wait it out.
  echo "Waiting for AMI to become deregistered..."
  while [ -n "$existingImageId" ]; do
      existingImageId=`aws ec2 describe-images --filters "Name=name,Values=CoCreateLite Base" --query "Images[*].{ID:ImageId}" --output text` 
      sleep 10s
  done
}

# Retrieve AWS Credentials either from environment of configuration file
[ -z "$AWS_REGION" ] && AWS_REGION=`aws configure get region`
[ -z "$AWS_REGION" ] && echo "Need to set AWS_REGION" && exit 1;

[ -z "$AWS_ACCESS_KEY_ID" ] && AWS_ACCESS_KEY_ID=`aws configure get aws_access_key_id`
[ -z "$AWS_ACCESS_KEY_ID" ] && echo "Need to set AWS_ACCESS_KEY_ID" && exit 1;

[ -z "$AWS_SECRET_ACCESS_KEY" ] && AWS_SECRET_ACCESS_KEY=`aws configure get aws_secret_access_key`
[ -z "$AWS_SECRET_ACCESS_KEY" ] && echo "Need to set AWS_SECRET_ACCESS_KEY" && exit 1;

[ -z "$AWS_ACCOUNT_ID" ] && AWS_ACCOUNT_ID=`aws iam get-user --output text | awk '{print $NF}'`
[ -z "$AWS_ACCOUNT_ID" ] && echo "Need to set AWS_ACCOUNT_ID" && exit 1;

existingImageId=`aws ec2 describe-images --filters "Name=name,Values=CoCreateLite Base" --query "Images[*].{ID:ImageId}" --output text`

if [ ! -z "${existingImageId}" ]; then
    while true; do
        read -p "Do you wish to delete the existing CoCreateLite Base AMI? [y/N] " yn
        case $yn in
            [Yy]* ) delete_prior_image $existingImageId; break;;
            [Nn]* ) echo "Nothing done. Goodbye"; exit;;
            * ) echo "Please answer yes or no.";;
        esac
    done
fi

# Retrieve CentOS base for CoCreate:Lite base
SOURCE_AMI=`aws ec2 describe-images --filters --filters "Name=name,Values=CentOS 6 x86_64 (2014_09_29) EBS HVM-74e73035-3435-48d6-88e0-89cc02ad83ee-ami-a8a117c0.2" --query "Images[*].{ID:ImageId}" --output text`

# Execute Packer to build ami
packer build \
  -var "account_id=$AWS_ACCOUNT_ID" \
  -var "aws_access_key_id=$AWS_ACCESS_KEY_ID" \
  -var "aws_secret_key=$AWS_SECRET_ACCESS_KEY" \
  -var "aws_region=$AWS_REGION" \
  -var "source_ami=$SOURCE_AMI" \
  ./cocreate_base.json

  echo "Took $SECONDS seconds to create CoCreateLite Base AMI."
  echo "Done. Goodbye."
