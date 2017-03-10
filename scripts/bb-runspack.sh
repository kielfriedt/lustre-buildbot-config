#!/bin/bash

# Check for a local cached configuration.
if test -f /etc/buildslave; then
    . /etc/buildslave
else
   echo "Missing configuration /etc/buildslave.  Assuming BB and spack are"
   echo "already installed and this is a persistent buildslave."
   exit 1
fi
# generate random number
num=$(( RANDOM % (7 - 1 + 1 ) + 1 ))
wget https://raw.githubusercontent.com/kielfriedt/spack-buildbot-config/tree/cdash/scripts/yaml/day$num.yaml .
./spack/bin/spack test-suite day$num.yaml
