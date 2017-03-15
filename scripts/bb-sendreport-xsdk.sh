#!/bin/bash
# Check for a local cached configuration.
if test -f /etc/buildslave; then
    . /etc/buildslave
else
   echo "Missing configuration /etc/buildslave.  Assuming BB and spack are"
   echo "already installed and this is a persistent buildslave."
   exit 1
fi
for x in `ls var/spack/cdash/$1`; do curl -k -d @var/spack/cdash/$x $XSDK_URL; done
