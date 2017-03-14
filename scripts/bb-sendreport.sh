#!/bin/bash
# Check for a local cached configuration.
python << END
import requests
import os
import glob
path = "var/spack/cdash/"
#path = "/Users/friedt2/Desktop/good_files/"
files = [name for name in glob.glob(os.path.join(path,'*.*')) if os.path.isfile(os.path.join(path,name))]
for f in files:
        if "dstore" not in f:
                with open(f) as fh:
                        mydata = fh.read()
                        response = requests.put('https://spack.io/cdash/submit.php?project=spack',#&FileName=build-bzip2-1.0.6-gh6bktroppxbca4kxgmrjfezzrknb6he.xml',
                                data=mydata,
                                auth=('omer', 'b01ad0ce'),
                                headers={'content-type':'text/plain'},
                                params={'file': path+f}
                                )
                        print f
                        print response.status_code
END
