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
wget $BB_URLyaml/day$num.yaml
ls -al
./bin/spack install bzip2
./bin/spack test-suite day$num.yaml
