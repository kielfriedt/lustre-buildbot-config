#!/bin/bash
# Check for a local cached configuration.
if test -f /etc/buildslave; then
    . /etc/buildslave
else
   echo "Missing configuration /etc/buildslave.  Assuming BB and spack are"
   echo "already installed and this is a persistent buildslave."
   exit 1
fi
echo $SPACK_URL
datetime=`date "+%Y-%m-%d"`
for x in `ls spack-test-$datetime`; do curl -k -d @spack-test-$datetime/$x $SPACK_URL; done