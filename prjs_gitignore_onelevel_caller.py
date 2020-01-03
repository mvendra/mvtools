#!/usr/bin/env python3

import sys
import os

import fsquery
import prjs_gitignore_lister

def prjs_gitignore_onelevel_caller(path):
    ls = []
    subcats = fsquery.makecontentlist(path, False, False, True, False, False, None)
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
