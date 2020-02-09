#!/usr/bin/env python3

import sys
import os

import fsquery
import path_utils

def prjs_gitignore_lister(path):
    
    ls = []
    projs = fsquery.makecontentlist(path, False, False, True, False, False, True, None)
    for p in projs:

        #pb = p[len(path)+1:]
        pb = p
        pn = os.path.basename(p)

        ign_build = path_utils.concat_path(pb, "build")
        ign_run = path_utils.concat_path(pb, "run")

        c_mk = "%s.mk" % pn
        c_txt = "%s.txt" % pn
        ign_proj_codelite_mk = path_utils.concat_path(pb, "proj", "codelite", c_mk)
        ign_proj_codelite_txt = path_utils.concat_path(pb, "proj", "codelite", c_txt)

        m_vs = ".vs"
        m_db = "%s.VC.db" % pn
        m_usr = "%s.vcxproj.user" % pn
        ign_proj_msvc15_vc = path_utils.concat_path(pb, "proj", "msvc15", m_vs)
        ign_proj_msvc15_vc_db = path_utils.concat_path(pb, "proj", "msvc15", m_db)
        ign_proj_msvc15_user = path_utils.concat_path(pb, "proj", "msvc15", m_usr)

        ls.append("# %s" % pn)
        ls.append(ign_build)
        ls.append(ign_run)
        ls.append(ign_proj_codelite_mk)
        ls.append(ign_proj_codelite_txt)
        ls.append(ign_proj_msvc15_vc)
        ls.append(ign_proj_msvc15_vc_db)
        ls.append(ign_proj_msvc15_user)
        ls.append("\n")

    return ls

if __name__ == "__main__":

    path = os.getcwd()
    ls = prjs_gitignore_lister(path)
    for l in ls:
        print(l)
