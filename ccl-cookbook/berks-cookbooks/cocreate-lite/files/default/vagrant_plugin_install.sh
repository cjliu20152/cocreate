#!/bin/bash

# The Chef community considers randomely failing plugin installs to be acceptable:
# https://github.com/tmatilai/vagrant-proxyconf/issues/78
# https://github.com/emyl/vagrant-triggers/issues/32
# https://github.com/GM-Alex/vagrant-winnfsd/issues/33
# http://biercoff.com/magical-fix-for-vagrant-nethttpnotfound-no-gems-found-matching-error/
# https://github.com/berkshelf/vagrant-berkshelf/issues/197
#
# While I expect higher standards from any developer, we have to make due with the below abomination until these people get their shit together.
PLUGIN_COUNT=0
COUNT=0

while [ $PLUGIN_COUNT -lt 6 -a $COUNT -lt 5 ]; do
    COUNT=$((COUNT+1))
    echo "Attempting to install vagrant plugins (attempt $COUNT)."
    vagrant plugin install vagrant-aws
    vagrant plugin install vagrant-awsinfo
    vagrant plugin install vagrant-berkshelf
    vagrant plugin install vagrant-proxyconf
    vagrant plugin install vagrant-triggers

    PLUGIN_COUNT=`vagrant plugin list | grep 'vagrant-aws\|vagrant-awsinfo\|vagrant-berkshelf\|vagrant-proxyconf\|vagrant-share\|vagrant-triggers' | wc -l`
done

exit 0
