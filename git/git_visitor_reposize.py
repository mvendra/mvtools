#!/usr/bin/env python

import os
import git_visitor_base

import path_utils
import dirsize

# source: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix='b'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)

def visitor_reposize(repos, options):

    # this tool will ignore submodules, since dirsize will consider subfolders
    repos_filtered = path_utils.filter_path_list_no_same_branch(repos)

    total = 0
    for rp in repos_filtered:
        rs = dirsize.get_dir_size(rp, False)
        total += int(rs)
        print("%s: %s" % (rp, sizeof_fmt(int(rs), '')))

    print("Total size of all repos: %s" % sizeof_fmt(total, ''))

if __name__ == "__main__":
    git_visitor_base.do_visit(None, None, visitor_reposize)

