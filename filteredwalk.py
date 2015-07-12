#!/usr/bin/env python

import sys
import os

def makefilelist(path, exts):

  """
  Makes a file list by walking the provided path
  path = a path string
  exts = a list of extensions to consider, without the dot
  returns a dictionary with extensions as keys, and each dict entry is a list of filenames with full path
  """

  ret_lists = {}
  for x in exts:
    ret_lists[x] = []

  for dirpath, dirnames, filenames in os.walk(path):
    for f in filenames:
      for x in exts:
        if f.endswith(x):
          ret_lists[x].append(os.path.join(os.path.abspath(dirpath), f))

  return ret_lists

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Usage: %s path extensions " % os.path.basename(__file__))
    exit(1)
  ret = makefilelist(sys.argv[1], sys.argv[2:])
  for k in ret:
    for r in ret[k]:
      print(r)

