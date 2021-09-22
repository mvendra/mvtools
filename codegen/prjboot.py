#!/usr/bin/env python3

import sys
import os

import path_utils

import makefile_proj_gen
import codelite_proj_gen
import msvc_proj_gen

PROJECT_TYPE_MAKEFILE_C = "makefile_c"
PROJECT_TYPE_MAKEFILE_CPP = "makefile_cpp"

PROJECT_TYPE_CODELITE15_C = "codelite15_c"
PROJECT_TYPE_CODELITE13_CPP = "codelite13_cpp"

PROJECT_TYPE_MSVC15_C = "msvc15_c"
PROJECT_TYPE_MSVC15_CPP = "msvc15_cpp"

PROJECT_TYPES = [PROJECT_TYPE_MAKEFILE_C, PROJECT_TYPE_MAKEFILE_CPP, PROJECT_TYPE_CODELITE15_C, PROJECT_TYPE_CODELITE13_CPP, PROJECT_TYPE_MSVC15_C, PROJECT_TYPE_MSVC15_CPP]
PROJECT_TYPE_DEFAULT = PROJECT_TYPE_CODELITE15_C

def prjboot(target_dir, proj_name, proj_type):

    chosen_function = None

    if proj_type == PROJECT_TYPE_MAKEFILE_C:
        chosen_function = makefile_proj_gen.generate_makefile_c
    elif proj_type == PROJECT_TYPE_MAKEFILE_CPP:
        chosen_function = makefile_proj_gen.generate_makefile_cpp
    elif proj_type == PROJECT_TYPE_CODELITE15_C:
        chosen_function = codelite_proj_gen.generate_codelite15_c
    elif proj_type == PROJECT_TYPE_CODELITE13_CPP:
        chosen_function = codelite_proj_gen.generate_codelite13_cpp
    elif proj_type == PROJECT_TYPE_MSVC15_C:
        chosen_function = msvc_proj_gen.generate_msvc15_c
    elif proj_type == PROJECT_TYPE_MSVC15_CPP:
        chosen_function = msvc_proj_gen.generate_msvc15_cpp
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
