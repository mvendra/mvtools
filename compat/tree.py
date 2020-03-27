#!/usr/bin/env python3

import sys
import os

import path_utils
import fsquery

class gentree:
    def __init__(self, path):
        self.rootpath = path
        self.clear()

    def clear(self):
        self.result = ""
        self.ident = ""
        self.files_total = 0
        self.dirs_total = 0

    def getresult(self):
        return self.result

    def addtoresult(self, content):
        self.result += self.ident + content

    def increase_ident(self):
        self.ident = self.ident + "---- "

    def decrease_ident(self):
        if len(self.ident) > 4:
            self.ident = self.ident[0:len(self.ident)-5]

    def traverse(self):

        self.clear()

        self.addtoresult( "* ")
        self.addtoresult( os.path.basename(path_utils.filter_remove_trailing_sep(self.rootpath)) )
        self.addtoresult(os.linesep)

        self.increase_ident()
        self.traverse_delegate(self.rootpath)
        self.decrease_ident()

        self.addtoresult(os.linesep)
        self.addtoresult("%d directories, %d files" % (self.dirs_total, self.files_total))

    def traverse_delegate(self, current_node):

        children = fsquery.makecontentlist(current_node, False, True, True, True, True, True, None)
        for c in children:

            if os.path.isdir(c):
                self.dirs_total += 1
                self.addtoresult( "* %s%s" % (os.path.basename(path_utils.filter_remove_trailing_sep(c)), os.linesep) )

                self.increase_ident()
                self.traverse_delegate(c)
                self.decrease_ident()
            else:
                self.files_total += 1
                self.addtoresult("%s%s" % (os.path.basename(path_utils.filter_remove_trailing_sep(c)), os.linesep) )

def gen_tree(path):

    if not os.path.exists(path):
        False, "%s does not exist" % path
    if not os.path.isdir(path):
        False, "%s is not a directory" % path

    contents = ""

    the_tree = gentree(path)
    the_tree.traverse()
    contents = the_tree.getresult()

    return True, contents

if __name__ == "__main__":

    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.getcwd()

    v, r = gen_tree(path)

    print(r)
    if not v:
        sys.exit(1)
