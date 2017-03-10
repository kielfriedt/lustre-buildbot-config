#!/bin/bash
for x in `ls /Users/friedt2/spack/var/spack/cdash$1`; do curl -d \@$x https://spack.io/cdash/submit.php?project=spack; rm $x; done