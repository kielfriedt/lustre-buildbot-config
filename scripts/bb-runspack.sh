#!/bin/bash
set -e -x

# Check for a local cached configuration.
if test -f /etc/buildslave; then
    . /etc/buildslave
else
   echo "Missing configuration /etc/buildslave.  Assuming BB and spack are"
   echo "already installed and this is a persistent buildslave."
   exit 1
fi
./bin/spack compilers
# generate random number
num=$(( RANDOM % (7 - 1 + 1 ) + 1 ))
while [ ! -f day$num.yaml ]
do
  echo "yaml file missing, trying again."
  wget $BB_URL/yaml/day$num.yaml
  sleep 1
done
ls -al
cat day$num.yaml
./bin/spack install bzip2
./bin/spack test-suite day$num.yaml
echo "returning"
