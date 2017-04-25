#!/bin/bash
set -xe

# Check for a local cached configuration.
if test -f /etc/buildslave; then
    . /etc/buildslave
else
   echo "Missing configuration /etc/buildslave.  Assuming BB and spack are"
   echo "already installed and this is a persistent buildslave."
   exit 1
fi
./bin/spack compilers
while [ ! -f xsdk.yaml ]
do
  echo "yaml file missing, trying again."
  wget $BB_URL/yaml/xsdk.yaml
  sleep 1
done
cat xsdk.yaml
./bin/spack test-suite xsdk.yaml
echo "returning"