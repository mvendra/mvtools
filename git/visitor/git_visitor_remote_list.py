#!/usr/bin/env python3

import os

import git_visitor_base
import git_repo_query

def visitor_remote_list(repos, options):

    for rp in repos:
        print("\n* Listing remotes of %s ..." % rp)
        remotes = git_repo_query.get_remotes(rp)
        if remotes is None:
            print("No remotes.")
            continue
        for rmn in remotes:
            for rmop in remotes[rmn]:
                l = os.path.basename(rp) # local folder name
                n = rmn # remote name
                o = rmop # remote operation
                p = remotes[rmn][rmop] # remote path

                print("%s: %s %s (%s)" % (l, n, p, o))

    return True

if __name__ == "__main__":
    r = git_visitor_base.do_visit(None, None, visitor_remote_list)
    if False in r:
        sys.exit(1)

