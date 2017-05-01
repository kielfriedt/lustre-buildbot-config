#!/bin/bash
# Check for a local cached configuration.
if test -f /etc/buildslave; then
    . /etc/buildslave
else
   echo "Missing configuration /etc/buildslave.  Assuming BB and spack are"
   echo "already installed and this is a persistent buildslave."
   exit 1
fi

echo $XSDK_URL
twodaysback=`date --date="2 days ago" "+%Y-%m-%d"`
onedayback=`date --date="1 days ago" "+%Y-%m-%d"`
currentday=`date "+%Y-%m-%d"`
correctdate=$currentday
if [ -d "spack-test-$currentday" ]; then
	correctdate=$currentday
elif [ -d "spack-test-$twodaysback" ]; then
	correctdate=$twodaysback
elif [ -d "spack-test-$onedayback" ]; then
	correctdate=$onedayback
else
	echo "folder can not be found."
	exit 1
fi
for x in `ls spack-test-$correctdate`; do curl -k -d @spack-test-$correctdate/$x $XSDK_URL; done