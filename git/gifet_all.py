#!/usr/bin/env python

import sys
import os
from subprocess import check_output

def puaq(): # print usage and quit
    print("Usage: %s repo_path (.git folder included)." % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo_path = sys.argv[1]
    print("Fetching %s..." % repo_path)

    try:
        out = check_output(["git", "--git-dir=%s" % repo_path, "--work-tree=%s" % os.path.dirname(repo_path), "fetch", "--all"])
        out = "Done with success."
    except:
        out = "Failed."

    print("\n%s" % out)

