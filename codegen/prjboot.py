#!/usr/bin/env python

import sys
import os

import path_utils

import common_gen
import makefile_proj_gen
import codelite_proj_gen
import msvc_proj_gen

# Linux
PROJECT_TYPE_LINUX_CODELITE15_C = ("linux_codelite15_c", codelite_proj_gen.generate_linux_codelite15_c)
PROJECT_TYPE_LINUX_MAKEFILE_C = ("linux_makefile_c", makefile_proj_gen.generate_linux_makefile_c)
PROJECT_TYPE_LINUX_MAKEFILE_CPP = ("linux_makefile_cpp", makefile_proj_gen.generate_linux_makefile_cpp)

# Windows
PROJECT_TYPE_WINDOWS_MSVC17_C = ("windows_msvc17_c", msvc_proj_gen.generate_windows_msvc17_c)
PROJECT_TYPE_WINDOWS_CODELITE15_C = ("windows_codelite15_c", codelite_proj_gen.generate_windows_codelite15_c)

# hint: adding new project types should warrant a review of the accompanying "prjrenamer" tool as well
PROJECT_TYPES = [PROJECT_TYPE_LINUX_CODELITE15_C, PROJECT_TYPE_LINUX_MAKEFILE_C, PROJECT_TYPE_LINUX_MAKEFILE_CPP, PROJECT_TYPE_WINDOWS_MSVC17_C, PROJECT_TYPE_WINDOWS_CODELITE15_C]
PROJECT_TYPE_DEFAULT = PROJECT_TYPE_LINUX_CODELITE15_C

def prjboot(target_dir, proj_name, proj_type):

    chosen_function = None

    # select the right function for this project type
    for pt in PROJECT_TYPES:
        if proj_type == pt[0]:
            chosen_function = pt[1]
            break

    if chosen_function is None:
        return False, "Unknown project type: [%s]" % proj_type

    # generate common structure for all projects
    v, r = common_gen.generate_common_structure(target_dir, proj_name)
    if not v:
        return False, r

    # carry out specific generation
    v, r = chosen_function(target_dir, proj_name)
    if not v:
        return False, r

    return True, None

def parse_proj_types(proj_types):
    contents = "["
    cut_last = False
    for pt in proj_types:
        cut_last = True
        contents += pt[0] + " | "
    if cut_last:
        contents = contents[:len(contents)-3]
    return contents + "]"

def puaq(selfhelp):
    print("Usage: %s [--help] [--target-dir target_dir] [--project-name proj_name] [--project-type %s]" % (path_utils.basename_filtered(__file__), parse_proj_types(PROJECT_TYPES)))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    params = sys.argv[1:]

    target_dir = os.getcwd()
    target_dir_next = False

    proj_name = "newproject"
    proj_name_next = False

    proj_type = PROJECT_TYPE_DEFAULT[0]
    proj_type_next = False

    for p in params:

        if p == "--help":
            puaq(True)

        if target_dir_next:
            target_dir_next = False
            target_dir = p
            continue

        if proj_name_next:
            proj_name_next = False
            proj_name = p
            continue

        if proj_type_next:
            proj_type_next = False
            proj_type = p
            continue

        if p == "--target-dir":
            target_dir_next = True
            continue
        elif p == "--project-name":
            proj_name_next = True
            continue
        elif p == "--project-type":
            proj_type_next = True
            continue

    v, r = prjboot(path_utils.filter_remove_trailing_sep(target_dir), path_utils.filter_remove_trailing_sep(proj_name), proj_type)
    if not v:
        print(r)
        sys.exit(1)
