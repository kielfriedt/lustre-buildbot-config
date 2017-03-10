#!/bin/bash
# Check for a local cached configuration.
if test -f /etc/buildslave; then
    . /etc/buildslave
else
   echo "Missing configuration /etc/buildslave.  Assuming BB and spack are"
   echo "already installed and this is a persistent buildslave."
   exit 1
fi
for x in `ls ./spack/var/spack/cdash$1`; do curl -d \@$x $SPACK_URL; rm $x; done