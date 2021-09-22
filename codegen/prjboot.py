#!/usr/bin/env python3

import sys
import os

import path_utils

import makefile_proj_gen
import codelite_proj_gen
import msvc_proj_gen

PROJECT_TYPE_C_MAKEFILE = "c_makefile"
PROJECT_TYPE_CPP_MAKEFILE = "cpp_makefile"

PROJECT_TYPE_C_CODELITE_15 = "c_codelite_15"
PROJECT_TYPE_CPP_CODELITE_13 = "cpp_codelite_13"

PROJECT_TYPE_C_MSVC_15 = "c_msvc_15"
PROJECT_TYPE_CPP_MSVC_15 = "cpp_msvc_15"

PROJECT_TYPES = [PROJECT_TYPE_C_MAKEFILE, PROJECT_TYPE_CPP_MAKEFILE, PROJECT_TYPE_C_CODELITE_15, PROJECT_TYPE_CPP_CODELITE_13, PROJECT_TYPE_C_MSVC_15, PROJECT_TYPE_CPP_MSVC_15]
PROJECT_TYPE_DEFAULT = PROJECT_TYPE_C_CODELITE_15

def prjboot(target_dir, proj_name, proj_type):

    chosen_function = None

    if proj_type == PROJECT_TYPE_C_MAKEFILE:
        chosen_function = makefile_proj_gen.generate_c_makefile
    elif proj_type == PROJECT_TYPE_CPP_MAKEFILE:
        chosen_function = makefile_proj_gen.generate_cpp_makefile
    elif proj_type == PROJECT_TYPE_C_CODELITE_15:
        chosen_function = codelite_proj_gen.generate_c_codelite_15
    elif proj_type == PROJECT_TYPE_CPP_CODELITE_13:
        chosen_function = codelite_proj_gen.generate_cpp_codelite_13
    elif proj_type == PROJECT_TYPE_C_MSVC_15:
        chosen_function = msvc_proj_gen.generate_c_msvc_15
    elif proj_type == PROJECT_TYPE_CPP_MSVC_15:
        chosen_function = msvc_proj_gen.generate_cpp_msvc_15
    else:
        print("Unknown project type: [%s]" % proj_type)
        sys.exit(1)

    v, r = chosen_function(target_dir, proj_name)
    if not v:
        print(r)
        sys.exit(1)

def parse_proj_types(proj_types):
    contents = "["
    cut_last = False
    for pt in proj_types:
        cut_last = True
        contents += pt + " | "
    if cut_last:
        contents = contents[:len(contents)-3]
    return contents + "]"

def puaq():
    print("Usage: %s [--help] [--target-dir target_dir] [--project-name proj_name] [--project-type %s]" % (path_utils.basename_filtered(__file__), parse_proj_types(PROJECT_TYPES)))
    sys.exit(1)

if __name__ == "__main__":

    params = sys.argv[1:]

    target_dir = os.getcwd()
    target_dir_next = False

    proj_name = "newproject"
    proj_name_next = False

    proj_type = PROJECT_TYPE_DEFAULT
    proj_type_next = False

    for p in params:

        if p == "--help":
            puaq()

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

    prjboot(target_dir, proj_name, proj_type)
