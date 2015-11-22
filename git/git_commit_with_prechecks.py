#!/usr/bin/env python

import sys
import os

from subprocess import check_output
from subprocess import CalledProcessError

def prechecks(repo):
    return True
    ret = check_output

#  TARGET=`pwd -P`
#  TARGET=(`git_discover_repo_root.py $TARGET`) # resolve to the actual repo
#  if [ $? -eq 1 ]; then
#    # not a git repo. bail out.
#    echo "This is not a git repository. Bailing out."
#    return 1
#  fi
#  RESULT=(`test_mvtags_in_git_cache.py $TARGET`)
#  if [ $? -eq 1 ]; then
#    # a pre-commit check failed: mvtags
#    echo "Pre-commit check failed - mvtags are present in the following files:"
#    echo $RESULT
#    # mvtodo: allow the commit to be interactively forced despite of this warning.
#    return 1
#  fi
#  git commit $@

def gicom(params):
    cmd = "git commit"
    for p in params:
        cmd += " %s" % p
    cmd += "!"
    # mvtodo: awesome... this ALSO does not carry the quotes.
    print(cmd)
    #cmd += params
    #os.system(cmd)

if __name__ == "__main__":
    repo = os.getcwd()
    repo = check_output(["git_discover_repo_root.py", repo])
    if prechecks(repo):
        gicom(sys.argv[1:])

