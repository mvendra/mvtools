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

    # tmp
    base_tmp = path_utils.concat_path(prj_fullname_base, "tmp")
    base_tmp_linux_x64_debug = path_utils.concat_path(base_tmp, "linux_x64_debug")
    base_tmp_linux_x64_release = path_utils.concat_path(base_tmp, "linux_x64_release")
    base_tmp_windows_x64_debug = path_utils.concat_path(base_tmp, "windows_x64_debug")
    base_tmp_windows_x64_release = path_utils.concat_path(base_tmp, "windows_x64_release")
    base_tmp_macosx_x64_debug = path_utils.concat_path(base_tmp, "macosx_x64_debug")
    base_tmp_macosx_x64_release = path_utils.concat_path(base_tmp, "macosx_x64_release")

    # out
    base_out = path_utils.concat_path(prj_fullname_base, "out")
    base_out_linux_x64_debug = path_utils.concat_path(base_out, "linux_x64_debug")
    base_out_linux_x64_release = path_utils.concat_path(base_out, "linux_x64_release")
    base_out_windows_x64_debug = path_utils.concat_path(base_out, "windows_x64_debug")
    base_out_windows_x64_release = path_utils.concat_path(base_out, "windows_x64_release")
    base_out_macosx_x64_debug = path_utils.concat_path(base_out, "macosx_x64_debug")
    base_out_macosx_x64_release = path_utils.concat_path(base_out, "macosx_x64_release")

    # dep
    base_dep = path_utils.concat_path(prj_fullname_base, "dep")

    # src
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # create folders accordingly
    prjboot_util.makedir_if_needed(prj_fullname_base)
    prjboot_util.makedir_if_needed(base_build)

    prjboot_util.makedir_if_needed(base_tmp)
    prjboot_util.makedir_if_needed(base_tmp_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_tmp_linux_x64_release)
    prjboot_util.makedir_if_needed(base_tmp_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_tmp_windows_x64_release)
    prjboot_util.makedir_if_needed(base_tmp_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_tmp_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_out)
    prjboot_util.makedir_if_needed(base_out_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_out_linux_x64_release)
    prjboot_util.makedir_if_needed(base_out_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_out_windows_x64_release)
    prjboot_util.makedir_if_needed(base_out_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_out_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_dep)

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
