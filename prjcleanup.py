#!/usr/bin/env python3

import sys
import os

import path_utils

def prjcleanup_dep(proj):

    path_proj_dep = path_utils.concat_path(proj, "dep")
    path_proj_dep_linux = path_utils.concat_path(path_proj_dep, "linux")
    path_proj_dep_windows = path_utils.concat_path(path_proj_dep, "windows")
    path_proj_dep_macosx = path_utils.concat_path(path_proj_dep, "macosx")

    recreate_paths = [path_proj_dep_linux, path_proj_dep_windows, path_proj_dep_macosx]

    for rp in recreate_paths:
        if not path_utils.recreate_as_folder_if_needed(rp):
            return False, "Unable to recreate-as-folder [%s]" % rp

    return True, None

def prjcleanup_tmp(proj):

    path_proj_tmp = path_utils.concat_path(proj, "tmp")
    path_proj_tmp_linux = path_utils.concat_path(path_proj_tmp, "linux")
    path_proj_tmp_linux_debug = path_utils.concat_path(path_proj_tmp_linux, "debug")
    path_proj_tmp_linux_release = path_utils.concat_path(path_proj_tmp_linux, "release")
    path_proj_tmp_windows = path_utils.concat_path(path_proj_tmp, "windows")
    path_proj_tmp_windows_debug = path_utils.concat_path(path_proj_tmp_windows, "debug")
    path_proj_tmp_windows_release = path_utils.concat_path(path_proj_tmp_windows, "release")
    path_proj_tmp_macosx = path_utils.concat_path(path_proj_tmp, "macosx")
    path_proj_tmp_macosx_debug = path_utils.concat_path(path_proj_tmp_macosx, "debug")
    path_proj_tmp_macosx_release = path_utils.concat_path(path_proj_tmp_macosx, "release")

    recreate_paths = [path_proj_tmp_linux, path_proj_tmp_linux_debug, path_proj_tmp_linux_release, path_proj_tmp_windows, path_proj_tmp_windows_debug, path_proj_tmp_windows_release, path_proj_tmp_macosx, path_proj_tmp_macosx_debug, path_proj_tmp_macosx_release]

    for rp in recreate_paths:
        if not path_utils.recreate_as_folder_if_needed(rp):
            return False, "Unable to recreate-as-folder [%s]" % rp

    return True, None

def prjcleanup_out(proj):

    path_proj_out = path_utils.concat_path(proj, "out")
    path_proj_out_linux = path_utils.concat_path(path_proj_out, "linux")
    path_proj_out_linux_debug = path_utils.concat_path(path_proj_out_linux, "debug")
    path_proj_out_linux_release = path_utils.concat_path(path_proj_out_linux, "release")
    path_proj_out_windows = path_utils.concat_path(path_proj_out, "windows")
    path_proj_out_windows_debug = path_utils.concat_path(path_proj_out_windows, "debug")
    path_proj_out_windows_release = path_utils.concat_path(path_proj_out_windows, "release")
    path_proj_out_macosx = path_utils.concat_path(path_proj_out, "macosx")
    path_proj_out_macosx_debug = path_utils.concat_path(path_proj_out_macosx, "debug")
    path_proj_out_macosx_release = path_utils.concat_path(path_proj_out_macosx, "release")

    recreate_paths = [path_proj_out_linux, path_proj_out_linux_debug, path_proj_out_linux_release, path_proj_out_windows, path_proj_out_windows_debug, path_proj_out_windows_release, path_proj_out_macosx, path_proj_out_macosx_debug, path_proj_out_macosx_release]

    for rp in recreate_paths:
        if not path_utils.recreate_as_folder_if_needed(rp):
            return False, "Unable to recreate-as-folder [%s]" % rp

    return True, None

def prjcleanup(proj, dep, tmp, out):

    # precond validations
    if not os.path.exists(proj):
        return False, "Project path [%s] does not exist." % proj

    # dep
    if dep:
        v, r = prjcleanup_dep(proj)
        if not v:
            return False, r

    # tmp
    if tmp:
        v, r = prjcleanup_tmp(proj)
        if not v:
            return False, r

    # out
    if out:
        v, r = prjcleanup_out(proj)
        if not v:
            return False, r

    return True, None

def puaq():
    print("Usage: %s proj [--dep | --tmp | --out]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        puaq()

    proj = os.path.abspath(sys.argv[1])
    dep = False
    tmp = False
    out = False

    for o in sys.argv[2:]:
        if o == "--dep":
            dep = True
        elif o == "--tmp":
            tmp = True
        elif o == "--out":
            out = True

    v, r = prjcleanup(proj, dep, tmp, out)
    if not v:
        print(r)
        sys.exit(1)
    print("Cleanup of [%s] succeeded" % proj)
