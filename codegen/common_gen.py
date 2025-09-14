#!/usr/bin/env python

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
    base_build_macos = path_utils.concat_path(base_build, "macos")

    # tmp
    base_tmp = path_utils.concat_path(prj_fullname_base, "tmp")
    base_tmp_linux = path_utils.concat_path(base_tmp, "linux")
    base_tmp_linux_debug = path_utils.concat_path(base_tmp_linux, "debug")
    base_tmp_linux_release = path_utils.concat_path(base_tmp_linux, "release")
    base_tmp_windows = path_utils.concat_path(base_tmp, "windows")
    base_tmp_windows_debug = path_utils.concat_path(base_tmp_windows, "debug")
    base_tmp_windows_release = path_utils.concat_path(base_tmp_windows, "release")
    base_tmp_macos = path_utils.concat_path(base_tmp, "macos")
    base_tmp_macos_debug = path_utils.concat_path(base_tmp_macos, "debug")
    base_tmp_macos_release = path_utils.concat_path(base_tmp_macos, "release")

    # out
    base_out = path_utils.concat_path(prj_fullname_base, "out")
    base_out_linux = path_utils.concat_path(base_out, "linux")
    base_out_linux_debug = path_utils.concat_path(base_out_linux, "debug")
    base_out_linux_release = path_utils.concat_path(base_out_linux, "release")
    base_out_windows = path_utils.concat_path(base_out, "windows")
    base_out_windows_debug = path_utils.concat_path(base_out_windows, "debug")
    base_out_windows_release = path_utils.concat_path(base_out_windows, "release")
    base_out_macos = path_utils.concat_path(base_out, "macos")
    base_out_macos_debug = path_utils.concat_path(base_out_macos, "debug")
    base_out_macos_release = path_utils.concat_path(base_out_macos, "release")

    # dep
    base_dep = path_utils.concat_path(prj_fullname_base, "dep")
    base_dep_linux = path_utils.concat_path(base_dep, "linux")
    base_dep_windows = path_utils.concat_path(base_dep, "windows")
    base_dep_macos = path_utils.concat_path(base_dep, "macos")

    # src
    base_src = path_utils.concat_path(prj_fullname_base, "src")

    # create folders accordingly
    prjboot_util.makedir_if_needed(prj_fullname_base)
    prjboot_util.makedir_if_needed(base_build)
    prjboot_util.makedir_if_needed(base_build_linux)
    prjboot_util.makedir_if_needed(base_build_windows)
    prjboot_util.makedir_if_needed(base_build_macos)

    prjboot_util.makedir_if_needed(base_tmp)
    prjboot_util.makedir_if_needed(base_tmp_linux)
    prjboot_util.makedir_if_needed(base_tmp_linux_debug)
    prjboot_util.makedir_if_needed(base_tmp_linux_release)
    prjboot_util.makedir_if_needed(base_tmp_windows)
    prjboot_util.makedir_if_needed(base_tmp_windows_debug)
    prjboot_util.makedir_if_needed(base_tmp_windows_release)
    prjboot_util.makedir_if_needed(base_tmp_macos)
    prjboot_util.makedir_if_needed(base_tmp_macos_debug)
    prjboot_util.makedir_if_needed(base_tmp_macos_release)

    prjboot_util.makedir_if_needed(base_out)
    prjboot_util.makedir_if_needed(base_out_linux)
    prjboot_util.makedir_if_needed(base_out_linux_debug)
    prjboot_util.makedir_if_needed(base_out_linux_release)
    prjboot_util.makedir_if_needed(base_out_windows)
    prjboot_util.makedir_if_needed(base_out_windows_debug)
    prjboot_util.makedir_if_needed(base_out_windows_release)
    prjboot_util.makedir_if_needed(base_out_macos)
    prjboot_util.makedir_if_needed(base_out_macos_debug)
    prjboot_util.makedir_if_needed(base_out_macos_release)

    prjboot_util.makedir_if_needed(base_dep)
    prjboot_util.makedir_if_needed(base_dep_linux)
    prjboot_util.makedir_if_needed(base_dep_windows)
    prjboot_util.makedir_if_needed(base_dep_macos)

    prjboot_util.makedir_if_needed(base_src)

    # gitignore
    gitignore_filename = path_utils.concat_path(prj_fullname_base, ".gitignore")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "/tmp/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "/out/")
    prjboot_util.add_to_gitignore_if_needed(gitignore_filename, "/dep/")

    # dep/gitkeep
    base_tmp_gitkeep_fn = path_utils.concat_path(base_tmp, ".gitkeep")
    base_out_gitkeep_fn = path_utils.concat_path(base_out, ".gitkeep")
    base_dep_gitkeep_fn = path_utils.concat_path(base_dep, ".gitkeep")

    # tmp/gitkeep
    base_tmp_gitkeep_fn = path_utils.concat_path(base_tmp, ".gitkeep")

    # out/gitkeep
    base_out_gitkeep_fn = path_utils.concat_path(base_out, ".gitkeep")

    gitkeeps = [base_dep_gitkeep_fn, base_tmp_gitkeep_fn, base_out_gitkeep_fn]
    for gk in gitkeeps:
        if not prjboot_util.writecontents(gk, ".gitkeep"):
            return False, "Failed creating [%s]" % gk

    return True, None
