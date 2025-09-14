#!/usr/bin/env python

import os
import sys

import git_visitor_base
import git_lib
import path_utils

def visitor_remote_list(repos, options):

    for rp in repos:
        print("\n* Listing remotes of %s ..." % rp)
        v, r = git_lib.get_remotes(rp)
        if not v:
            print("visitor_remote_list failed: [%s]: [%s]" % (rp, r))
            return False
        remotes = r
        if remotes == {}:
            print("No remotes.")
            continue
        for rmn in remotes:
            for rmop in remotes[rmn]:
                l = path_utils.basename_filtered(rp) # local folder name
                n = rmn # remote name
                o = rmop # remote operation
                p = remotes[rmn][rmop] # remote path

                print("%s: %s %s (%s)" % (l, n, p, o))

    return True

if __name__ == "__main__":
    r = git_visitor_base.do_visit(None, None, visitor_remote_list)
    if False in r:
        sys.exit(1)
