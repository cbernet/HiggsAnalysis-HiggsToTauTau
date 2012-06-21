#!/usr/bin/env python

'''

Parellelize calls to limit.py using LXBATCH.

Usage:

    lxb_limit.py submit_name "ARG_GLOB" [other options]

ARG_GLOB must expand to a list of directories.  Each entry in this list will be
a separate lxbatch job.  NB the use of quotes about ARG_GLOB.

Note also you may need to escape the quotes around sub-arguments.  For example,

    limit.py --tanb+ --userOpt '--minosAlgo stepping' cmb/*

would be

    lxb_limit.py my_limits "cmb/*"  --tanb+ --userOpt \'--minosAlgo stepping\'

will produce

    my_limits_submit.sh

which bsubs

    my_limits_0.sh
    ...
    my_limits_n.sh

'''

import glob
import logging
import os
import sys

log = logging.getLogger("lxb_limit")
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

if len(sys.argv) < 4:
    print "Usage: lxb_limit.py submit_name \"ARG_GLOB\" \"[other options]\""
    sys.exit(1)

name = sys.argv[1]
dirglob = sys.argv[2]
option_str = sys.argv[3:]

script_template = '''
#!/usr/bin/bash

cd {working_dir}
eval `scram runtime -sh`

$CMSSW_BASE/src/HiggsAnalysis/HiggsToTauTau/scripts/limit.py {options} {directory}

'''

submit_name = '%s_submit.sh' % name
with open(submit_name, 'w') as submit_script:
    for i, dir in enumerate(glob.glob(dirglob)):
        log.info("Generating limit.py script for %s", dir)
        script_file_name = '%s_%i.sh' % (name, i)
        with open(script_file_name, 'w') as script:
            script.write(script_template.format(
                working_dir = os.getcwd(),
                options = ' '.join(option_str),
                directory = dir
            ))
        os.system('chmod 755 %s' % script_file_name)
        submit_script.write('bsub -q 1nh %s\n' % script_file_name)
os.system('chmod 755 %s' % submit_name)