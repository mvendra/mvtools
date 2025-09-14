#!/usr/bin/env python

import sys
import os

import path_utils
import fsquery

def _clean_target(project_name, target_path):

    project_name = "%s.project" % project_name

    v, r = fsquery.makecontentlist(target_path, False, False, True, True, True, True, True, None)
    if not v:
        return False, [r]
    filelist = r

    failures = []
    for entry in filelist:

        if path_utils.basename_filtered(entry) == project_name:
            continue

        if not path_utils.remove_path(entry):
            failures.append("Unable to remove: [%s]" % entry)

    if len(failures) == 0:
        return True, ["Successfully cleaned up [%s]." % target_path]
    return False, failures

def codelite_build_cleaner(target_path):

    if not os.path.exists(target_path):
        return False, ["Target path [%s] does not exist." % target_path]

    # build
    target_path_build = path_utils.concat_path(target_path, "build")

    if not os.path.exists(target_path_build):
        return False, ["Target path's [%s] build subfolder does not exist." % target_path]

    if not os.path.isdir(target_path_build):
        return False, ["Target path's [%s] build subpath is not a folder." % target_path]

    # plats
    target_path_build_linux = path_utils.concat_path(target_path_build, "linux")
    target_path_build_windows = path_utils.concat_path(target_path_build, "windows")
    target_path_build_macos = path_utils.concat_path(target_path_build, "macos")

    targets = [target_path_build_linux, target_path_build_windows, target_path_build_macos]
    report = []

    for tg in targets:

        tg_clproj = path_utils.concat_path(tg, "codelite15_c")
        if os.path.isdir(tg_clproj):
            v, r = _clean_target(path_utils.basename_filtered(target_path), tg_clproj)
            report += r

    return True, report

if __name__ == "__main__":

    target = os.getcwd()

    v, r = codelite_build_cleaner(target)
    for e in r:
        print(e)
    if not v:
        sys.exit(1)
    print("Done.")
