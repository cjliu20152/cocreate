#!/bin/bash

#
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

#
# Bash shell script wrapper for Packer creation of CoCreate:Lite Base image
#

imageName="CoCreateLite Base"

function delete_prior_image {
  existingImageId=$1
  aws ec2 deregister-image --image-id "$existingImageId"

  # Takes some time to deregister...  Wait it out.
  echo "Waiting for AMI to become deregistered..."
  while [ -n "$existingImageId" ]; do
      existingImageId=`aws ec2 describe-images --filters "Name=name,Values=${imageName}" --query "Images[*].{ID:ImageId}" --output text`
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

existingImageId=`aws ec2 describe-images --filters "Name=name,Values=${imageName}" --query "Images[*].{ID:ImageId}" --output text`

if [ ! -z "${existingImageId}" ]; then
    if [ -f "$1" ]; then
        if  [ ! "$1" = "-f" ]; then
            echo "-f to force"
            exit
        else
            delete_prior_image $existingImageId
        fi
    else
        while true; do
            read -p "Do you wish to delete the existing ${imageName} AMI? [y/N] " yn
            case $yn in
                [Yy]* ) delete_prior_image $existingImageId; break;;
                [Nn]* ) echo "Nothing done. Goodbye"; exit;;
                * ) echo "Please answer yes or no.";;
            esac
        done
    fi
fi

# Retrieve CentOS 7 base
SOURCE_AMI=`aws --region $AWS_REGION ec2 describe-images --owners aws-marketplace --filters Name=product-code,Values=aw0evgkw8e5c1q413zgy5pjce --query "Images[*].{ID:ImageId}" --output text`

echo "Creating ${imageName} AMI..."

# Execute Packer to build ami
packer build \
  -var "account_id=$AWS_ACCOUNT_ID" \
  -var "aws_access_key_id=$AWS_ACCESS_KEY_ID" \
  -var "aws_secret_key=$AWS_SECRET_ACCESS_KEY" \
  -var "aws_region=$AWS_REGION" \
  -var "cocreate_base_ami_id=$COCREATE_BASE_AMI_ID" \
  -var "source_ami=$SOURCE_AMI" \
  ./cocreate_base.json

echo "Took $SECONDS seconds to create CoCreateLite Base AMI."
echo "Done. Goodbye."
