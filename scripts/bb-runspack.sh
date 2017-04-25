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
if [ -n "$1" ]; then
	yaml="$1"
fi

while [ ! -f "$yaml" ]
do
  echo "yaml file missing, trying again."
  wget "$BB_URLyaml/$yaml"
  sleep 1
done
cat "$yaml"
./bin/spack test-suite "$yaml"
echo "returning"
fi
