#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

def generate_common_structure(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)

    # build
    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_build_linux = path_utils.concat_path(base_build, "linux")
    base_build_windows = path_utils.concat_path(base_build, "windows")
    base_build_macosx = path_utils.concat_path(base_build, "macosx")

    # tmp
    base_tmp = path_utils.concat_path(prj_fullname_base, "tmp")
    base_tmp_linux = path_utils.concat_path(base_tmp, "linux")
    base_tmp_windows = path_utils.concat_path(base_tmp, "windows")
    base_tmp_macosx = path_utils.concat_path(base_tmp, "macosx")
    base_tmp_linux_debug = path_utils.concat_path(base_tmp, "linux_debug")
    base_tmp_linux_release = path_utils.concat_path(base_tmp, "linux_release")
    base_tmp_windows_debug = path_utils.concat_path(base_tmp, "windows_debug")
    base_tmp_windows_release = path_utils.concat_path(base_tmp, "windows_release")
    base_tmp_macosx_debug = path_utils.concat_path(base_tmp, "macosx_debug")
    base_tmp_macosx_release = path_utils.concat_path(base_tmp, "macosx_release")

    # out
    base_out = path_utils.concat_path(prj_fullname_base, "out")
    base_out_linux = path_utils.concat_path(base_out, "linux")
    base_out_windows = path_utils.concat_path(base_out, "windows")
    base_out_macosx = path_utils.concat_path(base_out, "macosx")
    base_out_linux_debug = path_utils.concat_path(base_out, "linux_debug")
    base_out_linux_release = path_utils.concat_path(base_out, "linux_release")
    base_out_windows_debug = path_utils.concat_path(base_out, "windows_debug")
    base_out_windows_release = path_utils.concat_path(base_out, "windows_release")
    base_out_macosx_debug = path_utils.concat_path(base_out, "macosx_debug")
    base_out_macosx_release = path_utils.concat_path(base_out, "macosx_release")

    # dep
    base_dep = path_utils.concat_path(prj_fullname_base, "dep")
    base_dep_linux = path_utils.concat_path(base_dep, "linux")
    base_dep_windows = path_utils.concat_path(base_dep, "windows")
    base_dep_macosx = path_utils.concat_path(base_dep, "macosx")

    # src
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # create folders accordingly
    prjboot_util.makedir_if_needed(prj_fullname_base)
    prjboot_util.makedir_if_needed(base_build)
    prjboot_util.makedir_if_needed(base_build_linux)
    prjboot_util.makedir_if_needed(base_build_windows)
    prjboot_util.makedir_if_needed(base_build_macosx)

    prjboot_util.makedir_if_needed(base_tmp)
    prjboot_util.makedir_if_needed(base_tmp_linux)
    prjboot_util.makedir_if_needed(base_tmp_windows)
    prjboot_util.makedir_if_needed(base_tmp_macosx)
    prjboot_util.makedir_if_needed(base_tmp_linux_debug)
    prjboot_util.makedir_if_needed(base_tmp_linux_release)
    prjboot_util.makedir_if_needed(base_tmp_windows_debug)
    prjboot_util.makedir_if_needed(base_tmp_windows_release)
    prjboot_util.makedir_if_needed(base_tmp_macosx_debug)
    prjboot_util.makedir_if_needed(base_tmp_macosx_release)

    prjboot_util.makedir_if_needed(base_out)
    prjboot_util.makedir_if_needed(base_out_linux)
    prjboot_util.makedir_if_needed(base_out_windows)
    prjboot_util.makedir_if_needed(base_out_macosx)
    prjboot_util.makedir_if_needed(base_out_linux_debug)
    prjboot_util.makedir_if_needed(base_out_linux_release)
    prjboot_util.makedir_if_needed(base_out_windows_debug)
    prjboot_util.makedir_if_needed(base_out_windows_release)
    prjboot_util.makedir_if_needed(base_out_macosx_debug)
    prjboot_util.makedir_if_needed(base_out_macosx_release)

    prjboot_util.makedir_if_needed(base_dep)
    prjboot_util.makedir_if_needed(base_dep_linux)
    prjboot_util.makedir_if_needed(base_dep_windows)
    prjboot_util.makedir_if_needed(base_dep_macosx)

    prjboot_util.makedir_if_needed(base_src)

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "tmp/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "out/")
    #prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "dep/") -> stopped adding the dep/ folder by default to gitignore, so its dep/.gitkeep can more easily be noticed and committed for the first time

    # dep/gitkeep
    depgitkeep_filename = path_utils.concat_path(prj_fullname_base, "dep", ".gitkeep")
    if not prjboot_util.writecontents(depgitkeep_filename, "dep"):
        return False, "Failed creating [%s]" % depgitkeep_filename

    return True, None
