#
# Author :: Patrick Dwyer <patricknevindwyer@gmail.com> 
# Author :: Alex Ethier <aethier@mitre.org>
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


name             'cocreate-lite'
maintainer       'Emily Laughren'
maintainer_email 'elaughren@mitre.org'
license          'All rights reserved'
description      'CoCreate Lite Cookbook'
long_description 'Installs required software packages for running CoCreate Lite in a CentOS 7 VirtualBox.'
version          '0.2'

depends 'build-essential'
depends 'yum-epel'
depends 'python', '~> 1.4.6'
depends 'iptables', '~> 2.2.0'
depends 'vagrant', '~> 0.5.0'
depends 'chef-dk', '~> 3.1.0'
