#!/usr/bin/env python

import sys
import os

def writecontents(filename, contents):
    with open(filename, "w") as f:
        f.write(contents)

def readcontents(filename):
    contents = ""
    with open(filename, "r") as f:
        contents = f.read()
    return contents

def prjrename_validate(target_dir, project_name):
    if not os.path.exists(target_dir):
        print("%s does not exist. Specify another target directory." % target_dir)
        return False
    return True

def remove_ext(path):
    if (path.find(".") == -1):
        return path
    f, e = path.split(".")
    return f

def codelite_rename(base_prj_codelite_fn, new_project_name):

    opn = remove_ext(poplastmaybe(os.path.basename(base_prj_codelite_fn)))
    npn = remove_ext(poplastmaybe(os.path.basename(new_project_name)))
    npn_full = os.path.join(os.path.dirname(base_prj_codelite_fn), "%s.project" % new_project_name)
    os.rename(base_prj_codelite_fn, npn_full)

    contents = readcontents(npn_full)
    str_cur = "CodeLite_Project Name=\"%s\"" % opn
    str_new = "CodeLite_Project Name=\"%s\"" % npn

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def msvc15sln_rename(base_prj_msvc15_sln, new_project_name):

    opn = remove_ext(poplastmaybe(os.path.basename(base_prj_msvc15_sln)))
    npn = remove_ext(poplastmaybe(os.path.basename(new_project_name)))
    npn_full = os.path.join(os.path.dirname(base_prj_msvc15_sln), "%s.sln" % new_project_name)
    os.rename(base_prj_msvc15_sln, npn_full)

    contents = readcontents(npn_full)
    str_cur = "\"%s\", \"%s.vcxproj\"" % (opn, opn)
    str_new = "\"%s\", \"%s.vcxproj\"" % (npn, npn)

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def msvc15vcxproj_rename(base_prj_msvc15_fn, new_project_name):

    opn = remove_ext(poplastmaybe(os.path.basename(base_prj_msvc15_fn)))
    npn = remove_ext(poplastmaybe(os.path.basename(new_project_name)))
    npn_full = os.path.join(os.path.dirname(base_prj_msvc15_fn), "%s.vcxproj" % new_project_name)
    os.rename(base_prj_msvc15_fn, npn_full)

    contents = readcontents(npn_full)
    str_cur = "<RootNamespace>%s</RootNamespace>" % opn
    str_new = "<RootNamespace>%s</RootNamespace>" % npn

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def makefile_rename(base_prj_makefile_fn, current_project_name, new_project_name):

    opn = poplastmaybe(current_project_name)
    npn = remove_ext(poplastmaybe(os.path.basename(new_project_name)))
    npn_full = os.path.join(os.path.dirname(base_prj_makefile_fn), "Makefile")

    contents = readcontents(npn_full)
    str_cur = "APPNAME=%s" % opn
    str_new = "APPNAME=%s" % npn

    contents = contents.replace(str_cur, str_new)
    writecontents(npn_full, contents)

def poplastmaybe(pathname):
    if pathname[len(pathname)-1] == os.sep:
        return pathname[:len(pathname)-1]
    return pathname

def prjrename(target_dir, original_project_name, new_project_name):

    original_project_name = poplastmaybe(original_project_name)
    new_project_name = poplastmaybe(new_project_name)

    full_original = os.path.join(target_dir, original_project_name)
    full_new = os.path.join(target_dir, new_project_name)

    if not prjrename_validate(target_dir, original_project_name):
        sys.exit(1)

    prj_fullname_base = os.path.join(target_dir, original_project_name)
    base_prj = os.path.join(prj_fullname_base, "proj")

    # codelite
    base_prj_codelite = os.path.join(base_prj, "codelite")
    base_prj_codelite_fn = os.path.join(base_prj_codelite, "%s.project" % original_project_name)
    codelite_rename(base_prj_codelite_fn, new_project_name)

    # msvc15
    base_prj_msvc15 = os.path.join(base_prj, "msvc15")
    base_prj_msvc15_sln = os.path.join(base_prj_msvc15, "%s.sln" % original_project_name)
    msvc15sln_rename(base_prj_msvc15_sln, new_project_name)
    base_prj_msvc15_fn = os.path.join(base_prj_msvc15, "%s.vcxproj" % original_project_name)
    msvc15vcxproj_rename(base_prj_msvc15_fn, new_project_name)

    base_prj_makefile = os.path.join(base_prj, "makefile")
    base_prj_makefile_fn = os.path.join(base_prj_makefile, "Makefile")
    makefile_rename(base_prj_makefile_fn, original_project_name, new_project_name)

    os.rename(full_original, full_new)

def puaq():
    print("Usage: %s proj-name new-proj-name [target-dir]" % os.path.basename(__file__))
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
