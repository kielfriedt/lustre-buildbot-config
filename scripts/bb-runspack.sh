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
wget $BB_URL/yaml/day$num.yaml
./bin/spack install bzip2
ls
pwd
./bin/spack test-suite day$num.yaml
