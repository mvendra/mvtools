#!/usr/bin/env python3

import sys
import os

import fsquery
import mvtools_exception
import prjs_gitignore_lister

def prjs_gitignore_onelevel_caller(path):
    ls = []
    v, r = fsquery.makecontentlist(path, False, False, False, True, False, False, True, None)
    if not v:
        raise mvtools_exception.mvtools_exception(r)
    subcats = r
    for c in subcats:
        tl = prjs_gitignore_lister.prjs_gitignore_lister(c)
        for a in tl:
            ls.append(a)
    return ls

if __name__ == "__main__":

    path = os.getcwd()
    ls = prjs_gitignore_onelevel_caller(path)
    for l in ls:
        print(l)
