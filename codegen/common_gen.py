#!/usr/bin/env python3

import sys
import os

import path_utils
import prjboot_util

def generate_common_structure(target_dir, project_name):

    # base folders / base structure
    prj_fullname_base = path_utils.concat_path(target_dir, project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")

    base_build = path_utils.concat_path(prj_fullname_base, "build")
    base_build_linux_x64_debug = path_utils.concat_path(base_build, "linux_x64_debug")
    base_build_linux_x64_release = path_utils.concat_path(base_build, "linux_x64_release")
    base_build_windows_x64_debug = path_utils.concat_path(base_build, "windows_x64_debug")
    base_build_windows_x64_release = path_utils.concat_path(base_build, "windows_x64_release")
    base_build_macosx_x64_debug = path_utils.concat_path(base_build, "macosx_x64_debug")
    base_build_macosx_x64_release = path_utils.concat_path(base_build, "macosx_x64_release")

    base_run = path_utils.concat_path(prj_fullname_base, "run")
    base_run_linux_x64_debug = path_utils.concat_path(base_run, "linux_x64_debug")
    base_run_linux_x64_release = path_utils.concat_path(base_run, "linux_x64_release")
    base_run_windows_x64_debug = path_utils.concat_path(base_run, "windows_x64_debug")
    base_run_windows_x64_release = path_utils.concat_path(base_run, "windows_x64_release")
    base_run_macosx_x64_debug = path_utils.concat_path(base_run, "macosx_x64_debug")
    base_run_macosx_x64_release = path_utils.concat_path(base_run, "macosx_x64_release")

    base_lib = path_utils.concat_path(prj_fullname_base, "lib")

    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # create folders accordingly
    prjboot_util.makedir_if_needed(prj_fullname_base)
    prjboot_util.makedir_if_needed(base_prj)

    prjboot_util.makedir_if_needed(base_build)
    prjboot_util.makedir_if_needed(base_build_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_build_linux_x64_release)
    prjboot_util.makedir_if_needed(base_build_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_build_windows_x64_release)
    prjboot_util.makedir_if_needed(base_build_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_build_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_run)
    prjboot_util.makedir_if_needed(base_run_linux_x64_debug)
    prjboot_util.makedir_if_needed(base_run_linux_x64_release)
    prjboot_util.makedir_if_needed(base_run_windows_x64_debug)
    prjboot_util.makedir_if_needed(base_run_windows_x64_release)
    prjboot_util.makedir_if_needed(base_run_macosx_x64_debug)
    prjboot_util.makedir_if_needed(base_run_macosx_x64_release)

    prjboot_util.makedir_if_needed(base_lib)

    prjboot_util.makedir_if_needed(base_src)

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "build/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "run/")
    #prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "lib/") -> stopped adding the lib/ folder by default to gitignore, so its lib/.gitkeep can more easily be noticed and committed for the first time

    # lib/gitkeep
    libgitkeep_filename = path_utils.concat_path(prj_fullname_base, "lib", ".gitkeep")
    if not prjboot_util.writecontents(libgitkeep_filename, "lib"):
        return False, "Failed creating [%s]" % libgitkeep_filename

    return True, None
