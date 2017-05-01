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
	if [ "$1" -eq "1" ]; then
		performance="-p"
	else
		performance=""
	fi
fi
if [ -n "$2" ]; then
	yaml="$2"
fi


while [ ! -f "$yaml" ]
do
  echo "yaml file missing, trying again."
  wget "$BB_URL/yaml/$yaml"
  sleep 1
done
cat "$yaml" 
if [ -n "$3" ]; then
	site="$3"
	./bin/spack test-suite  --site="$site" "$performance" "$yaml"
else
	./bin/spack test-suite "$performance" "$yaml"
fi
echo "returning"
