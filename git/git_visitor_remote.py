#!/usr/bin/env python

import os

import git_visitor_base
import git_repo_query

def visitor_remote(repos, options):

    for rp in repos:
        print("\n* Listing remotes of %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        for rmn in remotes:
            for rmop in remotes[rmn]:
                l = os.path.basename(rp) # local folder name
                n = rmn # remote name
                o = rmop # remote operation
                p = remotes[rmn][rmop] # remote path

                print("%s: %s %s (%s)" % (l, n, p, o))

if __name__ == "__main__":
    git_visitor_base.do_visit(None, None, visitor_remote)

