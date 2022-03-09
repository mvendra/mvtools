#!/usr/bin/env python3

import sys
import os

import path_utils

def writecontents(filename, contents):
    with open(filename, "w") as f:
        f.write(contents)

def readcontents(filename):
    contents = ""
    with open(filename, "r") as f:
        contents = f.read()
    return contents

def prjrename_validate(target_dir, project_name, project_new_name):
    if not os.path.exists(target_dir):
        print("%s does not exist. Specify another target directory." % target_dir)
        return False
    if not os.path.exists(path_utils.concat_path(target_dir, project_name)):
        print("%s does not exist. Specify another original project." % path_utils.concat_path(target_dir, project_name))
        return False
    if os.path.exists(path_utils.concat_path(target_dir, project_new_name)):
        print("%s already exists. Pick another new name." % path_utils.concat_path(target_dir, project_new_name))
        return False
    return True

def remove_ext(path):
    if (path.find(".") == -1):
        return path
    f, e = path.split(".")
    return f

def codelite_rename(base_prj_codelite_fn, new_project_name):

    opn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(base_prj_codelite_fn)))
    npn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(new_project_name)))
    npn_full = path_utils.concat_path(path_utils.dirname_filtered(base_prj_codelite_fn), "%s.project" % new_project_name)
    os.rename(base_prj_codelite_fn, npn_full)

    contents = readcontents(npn_full)
    str_cur = "CodeLite_Project Name=\"%s\"" % opn
    str_new = "CodeLite_Project Name=\"%s\"" % npn

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def msvc15sln_rename(base_prj_msvc15_sln, new_project_name):

    opn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(base_prj_msvc15_sln)))
    npn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(new_project_name)))
    npn_full = path_utils.concat_path(path_utils.dirname_filtered(base_prj_msvc15_sln), "%s.sln" % new_project_name)
    os.rename(base_prj_msvc15_sln, npn_full)

    contents = readcontents(npn_full)
    str_cur = "\"%s\", \"%s.vcxproj\"" % (opn, opn)
    str_new = "\"%s\", \"%s.vcxproj\"" % (npn, npn)

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def msvc15vcxproj_rename(base_prj_msvc15_fn, new_project_name):

    opn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(base_prj_msvc15_fn)))
    npn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(new_project_name)))
    npn_full = path_utils.concat_path(path_utils.dirname_filtered(base_prj_msvc15_fn), "%s.vcxproj" % new_project_name)
    os.rename(base_prj_msvc15_fn, npn_full)

    contents = readcontents(npn_full)
    str_cur = "<RootNamespace>%s</RootNamespace>" % opn
    str_new = "<RootNamespace>%s</RootNamespace>" % npn

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def msvc17sln_rename(base_prj_msvc17_sln, new_project_name):

    opn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(base_prj_msvc17_sln)))
    npn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(new_project_name)))
    npn_full = path_utils.concat_path(path_utils.dirname_filtered(base_prj_msvc17_sln), "%s.sln" % new_project_name)
    os.rename(base_prj_msvc17_sln, npn_full)

    contents = readcontents(npn_full)
    str_cur = "\"%s\", \"%s.vcxproj\"" % (opn, opn)
    str_new = "\"%s\", \"%s.vcxproj\"" % (npn, npn)
    contents = contents.replace(str_cur, str_new)

    writecontents(npn_full, contents)

def msvc17vcxproj_rename(base_prj_msvc17_fn, new_project_name):

    opn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(base_prj_msvc17_fn)))
    npn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(new_project_name)))
    npn_full = path_utils.concat_path(path_utils.dirname_filtered(base_prj_msvc17_fn), "%s.vcxproj" % new_project_name)
    os.rename(base_prj_msvc17_fn, npn_full)

    contents = readcontents(npn_full)
    str_cur = "<RootNamespace>%s</RootNamespace>" % opn
    str_new = "<RootNamespace>%s</RootNamespace>" % npn

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def msvc17vcxprojfilters_rename(base_prj_msvc17_c_vcxproj_filters_fn, new_project_name):

    npf_full = path_utils.concat_path(path_utils.dirname_filtered(base_prj_msvc17_c_vcxproj_filters_fn), "%s.vcxproj.filters" % new_project_name)
    os.rename(base_prj_msvc17_c_vcxproj_filters_fn, npf_full)

def makefile_rename(base_prj_makefile_fn, current_project_name, new_project_name):

    opn = path_utils.filter_remove_trailing_sep(current_project_name)
    npn = remove_ext(path_utils.filter_remove_trailing_sep(path_utils.basename_filtered(new_project_name)))
    npn_full = path_utils.concat_path(path_utils.dirname_filtered(base_prj_makefile_fn), "Makefile")

    contents = readcontents(npn_full)
    str_cur = "APPNAME=%s" % opn
    str_new = "APPNAME=%s" % npn

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def prjrename(target_dir, original_project_name, new_project_name):

    original_project_name = path_utils.filter_remove_trailing_sep(original_project_name)
    new_project_name = path_utils.filter_remove_trailing_sep(new_project_name)

    full_original = path_utils.concat_path(target_dir, original_project_name)
    full_new = path_utils.concat_path(target_dir, new_project_name)

    if not prjrename_validate(target_dir, original_project_name, new_project_name):
        sys.exit(1)

    prj_fullname_base = path_utils.concat_path(target_dir, original_project_name)
    base_prj = path_utils.concat_path(prj_fullname_base, "proj")

    # makefile_c
    base_prj_makefile_c = path_utils.concat_path(base_prj, "makefile_c")
    base_prj_makefile_c_fn = path_utils.concat_path(base_prj_makefile_c, "Makefile")
    if os.path.isfile(base_prj_makefile_c_fn):
        makefile_rename(base_prj_makefile_c_fn, original_project_name, new_project_name)
        print("Adapted [%s]" % base_prj_makefile_c_fn)

    # makefile_cpp
    base_prj_makefile_cpp = path_utils.concat_path(base_prj, "makefile_cpp")
    base_prj_makefile_cpp_fn = path_utils.concat_path(base_prj_makefile_cpp, "Makefile")
    if os.path.isfile(base_prj_makefile_cpp_fn):
        makefile_rename(base_prj_makefile_cpp_fn, original_project_name, new_project_name)
        print("Adapted [%s]" % base_prj_makefile_cpp_fn)

    # codelite15_c
    base_prj_codelite15_c = path_utils.concat_path(base_prj, "codelite15_c")
    base_prj_codelite15_c_fn = path_utils.concat_path(base_prj_codelite15_c, "%s.project" % original_project_name)
    if os.path.isfile(base_prj_codelite15_c_fn):
        codelite_rename(base_prj_codelite15_c_fn, new_project_name)
        print("Adapted [%s]" % base_prj_codelite15_c_fn)

    # codelite13_cpp
    base_prj_codelite13_cpp = path_utils.concat_path(base_prj, "codelite13_cpp")
    base_prj_codelite13_cpp_fn = path_utils.concat_path(base_prj_codelite13_cpp, "%s.project" % original_project_name)
    if os.path.isfile(base_prj_codelite13_cpp_fn):
        codelite_rename(base_prj_codelite13_cpp_fn, new_project_name)
        print("Adapted [%s]" % base_prj_codelite13_cpp_fn)

    # msvc15_c
    base_prj_msvc15_c = path_utils.concat_path(base_prj, "msvc15_c")
    base_prj_msvc15_c_sln_fn = path_utils.concat_path(base_prj_msvc15_c, "%s.sln" % original_project_name)
    base_prj_msvc15_c_vcxproj_fn = path_utils.concat_path(base_prj_msvc15_c, "%s.vcxproj" % original_project_name)
    if os.path.isfile(base_prj_msvc15_c_sln_fn) and os.path.isfile(base_prj_msvc15_c_vcxproj_fn):
        msvc15sln_rename(base_prj_msvc15_c_sln_fn, new_project_name)
        msvc15vcxproj_rename(base_prj_msvc15_c_vcxproj_fn, new_project_name)
        print("Adapted [%s] and [%s]" % (base_prj_msvc15_c_sln_fn, base_prj_msvc15_c_vcxproj_fn))

    # msvc15_cpp
    base_prj_msvc15_cpp = path_utils.concat_path(base_prj, "msvc15_cpp")
    base_prj_msvc15_cpp_sln_fn = path_utils.concat_path(base_prj_msvc15_cpp, "%s.sln" % original_project_name)
    base_prj_msvc15_cpp_vcxproj_fn = path_utils.concat_path(base_prj_msvc15_cpp, "%s.vcxproj" % original_project_name)
    if os.path.isfile(base_prj_msvc15_cpp_sln_fn) and os.path.isfile(base_prj_msvc15_cpp_vcxproj_fn):
        msvc15sln_rename(base_prj_msvc15_cpp_sln_fn, new_project_name)
        msvc15vcxproj_rename(base_prj_msvc15_cpp_vcxproj_fn, new_project_name)
        print("Adapted [%s] and [%s]" % (base_prj_msvc15_cpp_sln_fn, base_prj_msvc15_cpp_vcxproj_fn))

    # msvc17_c
    base_prj_msvc17_c = path_utils.concat_path(base_prj, "msvc17_c")
    base_prj_msvc17_c_sln_fn = path_utils.concat_path(base_prj_msvc17_c, "%s.sln" % original_project_name)
    base_prj_msvc17_c_vcxproj_fn = path_utils.concat_path(base_prj_msvc17_c, "%s.vcxproj" % original_project_name)
    base_prj_msvc17_c_vcxproj_filters_fn = path_utils.concat_path(base_prj_msvc17_c, "%s.vcxproj.filters" % original_project_name)
    if os.path.isfile(base_prj_msvc17_c_sln_fn) and os.path.isfile(base_prj_msvc17_c_vcxproj_fn):
        msvc17sln_rename(base_prj_msvc17_c_sln_fn, new_project_name)
        msvc17vcxproj_rename(base_prj_msvc17_c_vcxproj_fn, new_project_name)
        msvc17vcxprojfilters_rename(base_prj_msvc17_c_vcxproj_filters_fn, new_project_name)
        print("Adapted [%s], [%s] and [%s]" % (base_prj_msvc17_c_sln_fn, base_prj_msvc17_c_vcxproj_fn, base_prj_msvc17_c_vcxproj_filters_fn))

    os.rename(full_original, full_new)

def puaq():
    print("Usage: %s proj-name new-proj-name [target-dir]" % path_utils.basename_filtered(__file__))
    sys.exit(1)

if __name__ == "__main__":

    td = os.getcwd()
    pn_orig = ""
    pn_new = ""

    if len(sys.argv) < 3:
        puaq()

    pn_orig = sys.argv[1]
    pn_new = sys.argv[2]

    if len(sys.argv) > 3:
        td = sys.argv[3]

    prjrename(td, pn_orig, pn_new)
