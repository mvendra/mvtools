#!/usr/bin/env python3

import sys
import os
from subprocess import check_output

def puaq(): # print usage and quit
    print("Usage: %s repo_path." % os.path.basename(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 2:
        puaq()

    repo_path = sys.argv[1]
    print("Fetching %s..." % repo_path)

    try:
        out = check_output(["git", "-C", repo_path, "fetch", "--all"])
        out = "Done with success."
    except:
        out = "Failed."

    print("\n%s" % out)

