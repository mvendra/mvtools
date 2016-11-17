#!/usr/bin/env python

import sys
import os

class codelite_vs_msvc14_checker():

    def __init__(_self, codelite_proj, msvc14_proj, exclude_list):
        _self.codelite_proj = codelite_proj
        _self.msvc14_proj = msvc14_proj
        _self.exclude_list = exclude_list

    def between_quotes(_self, the_str):
        if the_str is None:
            return ""
        if the_str == "":
            return ""
        s = the_str.find("\"")
        if s == -1:
            return ""
        if len(the_str) - 1 == s:
            return ""
        f = the_str.find("\"", s + 1)
        return the_str[s+1:f]

    def run(_self):

        if not os.path.exists(_self.codelite_proj):
            print("%s does not exist. Aborting." % _self.codelite_proj)
            return

        if not os.path.exists(_self.msvc14_proj):
            print("%s does not exist. Aborting." % _self.msvc14_proj)
            return

        c_contents = ""
        with open(_self.codelite_proj, "U") as f:
            c_contents = f.read()

        m_contents = ""
        with open(_self.msvc14_proj, "U") as f:
            m_contents = f.read()

        c_files = []
        for l in c_contents.split("\n"):
            if "File Name" in l:
                lt = l.strip()
                lc = _self.between_quotes(lt)
                if not lc in _self.exclude_list:
                    c_files.append(lc)

        m_files = []
        for l in m_contents.split("\n"):
            if ("ClCompile Include" in l) or ("ClInclude Include" in l) or ("None Include" in l):
                lt = l.strip()
                lc = _self.between_quotes(lt)
                lc = lc.replace("\\", "/")
                if not lc in _self.exclude_list:
                    m_files.append(lc)

        only_on_msvc = []
        only_on_codelite = []

        for f in m_files:
            if not f in c_files:
                only_on_msvc.append(f)

        for f in c_files:
            if not f in m_files:
                only_on_codelite.append(f)

        if len(only_on_codelite) > 0:
            print("ONLY ON CODELITE:")
            for f in only_on_codelite:
                print(f)

        if len(only_on_msvc) > 0:
            print("ONLY ON MSVC:")
            for f in only_on_msvc:
                print(f)
